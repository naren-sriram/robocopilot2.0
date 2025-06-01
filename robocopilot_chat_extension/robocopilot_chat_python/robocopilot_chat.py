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
    """RoboCopilot Chat implementation with stacking controller and custom scene"""

    def __init__(self) -> None:
        self._controller = None
        self._articulation_controller = None
        self._execution_log = []
        self._current_status = "Ready"
        self._franka = None
        self._cubes = []
        self._world = None
        self._cube_positions = []  # Store actual cube positions

    def setup_scene(self):
        """Setup the scene with Franka robot and cubes"""
        try:
            self._log_message("Starting custom scene setup...")

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
        """Setup stacking controller with custom cube coordinates"""
        try:
            self._log_message("Starting stacking controller setup with custom coordinates...")

            # Import the stacking controller
            self._log_message("Importing StackingController...")
            try:
                from omni.isaac.franka.controllers.stacking_controller import StackingController
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
            if len(self._cubes) < 2:
                raise Exception("Need at least 2 cubes for stacking")

            self._log_message(f"Found {len(self._cubes)} cubes for stacking")

            # Get actual cube positions from the scene
            self._cube_positions = []
            cube_names = []
            for i, cube in enumerate(self._cubes):
                cube_position, cube_rotation = cube.get_world_pose()
                self._cube_positions.append(cube_position)
                cube_names.append(f"cube_{i}")
                self._log_message(f"Cube {i} ({cube.name}) at position: {cube_position}")

            # Validate that cubes exist in the world scene
            scene_objects = self._world.scene.get_object_names()
            self._log_message(f"All objects in scene: {scene_objects}")
            
            # Check if our cubes are properly registered
            for i, cube_name in enumerate(cube_names):
                cube_obj = self._world.scene.get_object(cube_name)
                if cube_obj:
                    self._log_message(f"Validated cube in scene: {cube_name}")
                else:
                    self._log_message(f"Warning: cube {cube_name} not found in world scene")

            # Find gripper
            self._log_message("Finding Franka gripper...")
            gripper = None
            if hasattr(self._franka, 'gripper') and self._franka.gripper is not None:
                gripper = self._franka.gripper
                self._log_message(f"Found gripper: {gripper}")
            elif hasattr(self._franka, 'panda_hand') and self._franka.panda_hand is not None:
                gripper = self._franka.panda_hand
                self._log_message(f"Found panda_hand: {gripper}")
            elif hasattr(self._franka, 'end_effector') and self._franka.end_effector is not None:
                gripper = self._franka.end_effector
                self._log_message(f"Found end_effector: {gripper}")
            else:
                # Check all attributes for gripper-like objects
                gripper_attrs = [attr for attr in dir(self._franka) if any(keyword in attr.lower() for keyword in ['gripper', 'hand', 'end_effector'])]
                self._log_message(f"Gripper/hand-related attributes: {gripper_attrs}")
                
                for attr in gripper_attrs:
                    attr_value = getattr(self._franka, attr, None)
                    if attr_value is not None:
                        self._log_message(f"Found {attr}: {attr_value}, type: {type(attr_value)}")
                        gripper = attr_value
                        break
            
            if not gripper:
                raise Exception("Franka gripper not found or not initialized")
            
            self._log_message(f"Using gripper: {gripper}")
            
            # Initialize the stacking controller with cube coordinates
            self._log_message("Creating StackingController with custom cube positions...")
            self._controller = StackingController(
                name="stacking_controller",
                gripper=gripper,
                robot_articulation=self._franka,
                picking_order_cube_names=cube_names,
                robot_observation_name=self._franka.name,
            )
            self._log_message("StackingController created successfully")

            # IMPORTANT: Configure the controller with actual cube positions
            self._log_message("Configuring controller with actual cube coordinates...")
            
            # Try to set cube positions if the controller supports it
            if hasattr(self._controller, '_cube_positions'):
                self._controller._cube_positions = self._cube_positions
                self._log_message("Set _cube_positions on controller")
            
            if hasattr(self._controller, 'set_cube_positions'):
                self._controller.set_cube_positions(self._cube_positions)
                self._log_message("Called set_cube_positions on controller")
            
            # Set target stacking position (place cube_1 on cube_0)
            if len(self._cube_positions) >= 2:
                target_position = self._cube_positions[0].copy()  # Base cube position
                target_position[2] += 0.1  # Stack on top
                
                if hasattr(self._controller, '_target_position'):
                    self._controller._target_position = target_position
                    self._log_message(f"Set target position: {target_position}")
                
                if hasattr(self._controller, 'set_target_position'):
                    self._controller.set_target_position(target_position)
                    self._log_message(f"Called set_target_position: {target_position}")

            # Get articulation controller
            self._log_message("Getting articulation controller...")
            self._articulation_controller = self._franka.get_articulation_controller()
            if not self._articulation_controller:
                raise Exception("Failed to get articulation controller from Franka")
            self._log_message("Articulation controller obtained successfully")

            self._log_message("Stacking controller with custom coordinates initialized successfully")
            self._current_status = "Ready for execution"
            return True

        except Exception as e:
            self._log_message(f"Error setting up stacking controller: {str(e)}")
            self._log_message(f"Error type: {type(e).__name__}")
            import traceback
            error_details = traceback.format_exc()
            self._log_message(f"Full error traceback: {error_details}")
            traceback.print_exc()
            return False

    def _on_stacking_physics_step(self, step_size):
        """Physics step callback for stacking execution with custom cube coordinates"""
        if not self._controller or not self._articulation_controller:
            return

        try:
            # Get observations from world
            observations = self._world.get_observations()
            if not observations:
                self._log_message("Warning: No observations received from world")
                return
            
            # Log observation keys for debugging (only first few times)
            if not hasattr(self, '_obs_logged'):
                if hasattr(observations, 'keys'):
                    obs_keys = list(observations.keys())
                    self._log_message(f"Available observation keys: {obs_keys}")
                else:
                    self._log_message(f"Observations type: {type(observations)}")
                self._obs_logged = True
            
            # Update cube positions in observations if needed
            # The stacking controller expects cube positions in observations
            if hasattr(observations, 'update') and self._cube_positions:
                # Add current cube positions to observations
                for i, cube_pos in enumerate(self._cube_positions):
                    # Update with current cube position from scene
                    if i < len(self._cubes):
                        current_pos, _ = self._cubes[i].get_world_pose()
                        observations[f"cube_{i}_position"] = current_pos
                        observations[f"cube_{i}_orientation"] = np.array([1.0, 0.0, 0.0, 0.0])
            
            # Get actions from stacking controller
            actions = self._controller.forward(observations=observations)
            if actions is None:
                self._log_message("Warning: No actions received from controller")
                return
            
            # Apply actions to robot
            self._articulation_controller.apply_action(actions)

            # Check if stacking task is done
            if self._controller.is_done():
                self._world.pause()
                self._log_message("Stacking task completed successfully!")
                self._current_status = "Task completed"
                
        except Exception as e:
            self._log_message(f"Error in stacking physics step: {str(e)}")
            self._log_message(f"Error type: {type(e).__name__}")
            
            # Log more details about the error
            import traceback
            error_details = traceback.format_exc()
            self._log_message(f"Full error traceback: {error_details}")
            
            # Pause simulation on error
            if self._world:
                self._world.pause()
            
            self._current_status = "Task failed"

    async def _on_execute_task_async(self, prompt="Stack the cubes"):
        """Execute the stacking task asynchronously with custom cube coordinates"""
        try:
            self._log_message(f"Executing stacking task: {prompt}")
            self._current_status = "Executing task..."

            if not self._world:
                raise Exception("World not initialized")

            if not self._controller:
                raise Exception("Stacking controller not initialized")

            # Reset controller
            self._controller.reset()
            self._log_message("Controller reset completed")

            # Add physics callback for stacking
            self._world.add_physics_callback("sim_step", self._on_stacking_physics_step)

            # Start simulation
            await self._world.play_async()

        except Exception as e:
            self._log_message(f"Error executing stacking task: {str(e)}")
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
            self._cube_positions = []
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