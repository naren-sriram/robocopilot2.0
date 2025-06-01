# Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto. Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import numpy as np
from isaacsim.core.api.objects.cuboid import DynamicCuboid
from isaacsim.core.api.world import World
from isaacsim.core.prims import SingleArticulation, XFormPrim
from isaacsim.core.utils.stage import add_reference_to_stage, create_new_stage, get_current_stage
from isaacsim.storage.native import get_assets_root_path
from pxr import Sdf, UsdLux


class RoboCopilotChat:
    """RoboCopilot Chat implementation with custom scene building and stacking controller"""

    def __init__(self) -> None:
        self._controller = None
        self._articulation_controller = None
        self._execution_log = []
        self._current_status = "Ready"
        self._franka = None
        self._cubes = []
        self._world = None

    def setup_scene(self):
        """Setup the scene with Franka robot and cubes"""
        try:
            self._log_message("Starting scene setup...")
            
            # Create new stage
            self._log_message("Creating new stage...")
            create_new_stage()
            self._add_light_to_stage()
            
            # Load Franka robot
            self._log_message("Loading Franka robot...")
            robot_prim_path = "/franka"
            path_to_robot_usd = get_assets_root_path() + "/Isaac/Robots/Franka/franka.usd"
            add_reference_to_stage(path_to_robot_usd, robot_prim_path)
            
            # Create Franka articulation
            self._log_message("Creating Franka articulation...")
            self._franka = SingleArticulation(robot_prim_path)
            
            # Create cubes for stacking
            self._log_message("Creating cubes...")
            self._cubes = []
            cube_positions = [
                np.array([0.3, 0.3, 0.05]),  # Bottom cube
                np.array([0.3, 0.1, 0.05]),  # Top cube (to be stacked)
            ]
            
            for i, position in enumerate(cube_positions):
                self._log_message(f"Creating cube {i}...")
                # cubes should be of different colors - red and green
                if i == 0:
                    color = np.array([1.0, 0.0, 0.0])
                else:
                    color = np.array([0.0, 1.0, 0.0])
                cube = DynamicCuboid(
                    f"/World/cube_{i}",
                    position=position,
                    size=0.05,
                    color=color,
                    name=f"cube_{i}"
                )
                self._cubes.append(cube)
            
            # Add objects to world (World will be created by LoadButton)
            self._log_message("Getting World instance...")
            self._world = World.instance()
            
            self._log_message("Adding objects to World...")
            self._world.scene.add(self._franka)
            for i, cube in enumerate(self._cubes):
                self._log_message(f"Adding cube {i} to World...")
                self._world.scene.add(cube)
            
            self._log_message("Scene setup completed with Franka robot and cubes")
            return True
            
        except Exception as e:
            self._log_message(f"Error setting up scene: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def _add_light_to_stage(self):
        """Add a light to the stage"""
        sphereLight = UsdLux.SphereLight.Define(get_current_stage(), Sdf.Path("/World/SphereLight"))
        sphereLight.CreateRadiusAttr(2)
        sphereLight.CreateIntensityAttr(100000)
        XFormPrim(str(sphereLight.GetPath())).set_world_poses(np.array([[6.5, 0, 12]]))

    async def setup_post_load(self):
        """Setup controllers after scene is loaded"""
        try:
            self._log_message("Starting controller setup...")
            
            # Import the stacking controller here to avoid dependency issues
            self._log_message("Importing StackingController...")
            try:
                from omni.isaac.examples.franka.controllers.stacking_controller import StackingController
                self._log_message("StackingController imported successfully")
            except ImportError as e:
                self._log_message(f"Failed to import StackingController: {str(e)}")
                self._log_message("Make sure omni.isaac.examples extension is loaded")
                raise
            
            # Validate required objects
            if not self._franka:
                raise Exception("Franka robot not initialized")
            if not self._cubes:
                raise Exception("Cubes not created")
            if len(self._cubes) == 0:
                raise Exception("No cubes found for stacking")
                
            self._log_message(f"Found {len(self._cubes)} cubes for stacking")
            
            # Get cube names for the controller
            cube_names = [f"cube_{i}" for i in range(len(self._cubes))]
            self._log_message(f"Cube names for controller: {cube_names}")
            
            # Check if gripper exists
            if not hasattr(self._franka, 'gripper') or self._franka.gripper is None:
                raise Exception("Franka gripper not found or not initialized")
            self._log_message("Franka gripper validated")
            
            # Initialize the stacking controller
            self._log_message("Creating StackingController instance...")
            self._controller = StackingController(
                name="stacking_controller",
                gripper=self._franka.gripper,
                robot_articulation=self._franka,
                picking_order_cube_names=cube_names,
                robot_observation_name=self._franka.name,
            )
            self._log_message("StackingController created successfully")
            
            # Get articulation controller
            self._log_message("Getting articulation controller...")
            self._articulation_controller = self._franka.get_articulation_controller()
            if not self._articulation_controller:
                raise Exception("Failed to get articulation controller from Franka")
            self._log_message("Articulation controller obtained successfully")
            
            self._log_message("Controllers initialized successfully")
            self._current_status = "Ready for execution"
            return True
            
        except Exception as e:
            self._log_message(f"Error setting up controllers: {str(e)}")
            self._log_message(f"Error type: {type(e).__name__}")
            import traceback
            error_details = traceback.format_exc()
            self._log_message(f"Full error traceback: {error_details}")
            traceback.print_exc()
            return False

    def _on_stacking_physics_step(self, step_size):
        """Physics step callback for stacking execution"""
        if not self._controller or not self._articulation_controller:
            return
            
        try:
            observations = self._world.get_observations()
            actions = self._controller.forward(observations=observations)
            self._articulation_controller.apply_action(actions)

            if self._controller.is_done():
                self._world.pause()
                self._log_message("Stacking task completed successfully")
                self._current_status = "Task completed"
        except Exception as e:
            self._log_message(f"Error in physics step: {str(e)}")
            self._world.pause()

    async def _on_execute_task_async(self, prompt="Stack the cubes"):
        """Execute the stacking task asynchronously with prompt context"""
        try:
            self._log_message(f"Executing task: {prompt}")
            self._current_status = "Executing task..."

            if not self._world:
                raise Exception("World not initialized")
                
            if not self._controller:
                raise Exception("Controller not initialized")

            # Reset controller
            self._controller.reset()
            
            # Add physics callback
            self._world.add_physics_callback("sim_step", self._on_stacking_physics_step)
            
            # Start simulation
            await self._world.play_async()
            
        except Exception as e:
            self._log_message(f"Error executing task: {str(e)}")
            self._current_status = "Task failed"
            raise

    async def setup_pre_reset(self):
        """Cleanup before reset"""
        try:
            if self._world and self._world.physics_callback_exists("sim_step"):
                self._world.remove_physics_callback("sim_step")
            if self._controller:
                self._controller.reset()
            self._log_message("System reset")
            self._current_status = "Reset completed"
        except Exception as e:
            self._log_message(f"Error in pre-reset: {str(e)}")

    def world_cleanup(self):
        """Clean up world resources"""
        try:
            if self._world and self._world.physics_callback_exists("sim_step"):
                self._world.remove_physics_callback("sim_step")
            self._controller = None
            self._articulation_controller = None
            self._franka = None
            self._cubes = []
            self._log_message("World cleanup completed")
            self._current_status = "Cleaned up"
        except Exception as e:
            self._log_message(f"Error in cleanup: {str(e)}")

    def _log_message(self, message):
        """Add a message to the execution log"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self._execution_log.append(f"[{timestamp}] {message}")
        print(f"RoboCopilot: {message}")

    def get_execution_log(self):
        """Get the current execution log"""
        return self._execution_log.copy()

    def clear_execution_log(self):
        """Clear the execution log"""
        self._execution_log = []
        self._log_message("Execution log cleared")

    def get_current_status(self):
        """Get the current system status"""
        return self._current_status