# Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto. Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import numpy as np
from isaacsim.core.api.objects.cuboid import DynamicCuboid, FixedCuboid
from isaacsim.core.api.world import World
from isaacsim.core.prims import SingleArticulation, XFormPrim
from isaacsim.core.utils.stage import add_reference_to_stage, create_new_stage, get_current_stage
from isaacsim.storage.native import get_assets_root_path
from omni.isaac.franka.controllers import PickPlaceController

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
        self._cube_positions = [] 
        self._goal_position = [] 
        self.prompt = ""

    def setup_scene(self):
        """Setup the scene with Franka robot and cubes"""
        try:
            self._log_message("Starting custom scene setup...")

            # Create new stage
            self._log_message("Creating new stage...")
            create_new_stage()
            self._add_light_to_stage()

            # Add ground plane first for physics support
            self._log_message("Adding ground plane...")
            ground_plane = FixedCuboid(
                prim_path="/World/GroundPlane",
                name="ground_plane",
                position=np.array([0.0, 0.0, -0.05]),
                size=np.array([2.0, 2.0, 0.1]),
                color=np.array([0.5, 0.5, 0.5])  # Gray
            )

            # Load Franka robot
            self._log_message("Loading Franka robot...")
            robot_prim_path = "/franka"
            path_to_robot_usd = get_assets_root_path() + "/Isaac/Robots/Franka/franka.usd"
            add_reference_to_stage(path_to_robot_usd, robot_prim_path)

            # Create Franka articulation
            self._log_message("Creating Franka articulation...")
            self._franka = SingleArticulation(robot_prim_path)

            # Create cubes for stacking - positioned higher to avoid falling through ground
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
                    color = np.array([1.0, 0.0, 0.0])  # Red
                else:
                    color = np.array([0.0, 1.0, 0.0])  # Green
                colors = ['red', 'green']
                cube = DynamicCuboid(
                    f"/World/cube_{i}",
                    position=position,
                    size=0.05,
                    color=color,
                    name=f"cube_{colors[i]}"
                )
                self._cubes.append(cube)

            # Add objects to world (World will be created by LoadButton)
            self._log_message("Getting World instance...")
            self._world = World.instance()

            self._log_message("Adding objects to World...")
            # Add ground plane first
            self._world.scene.add(ground_plane)
            # Add robot
            self._world.scene.add(self._franka)
            # Add cubes
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
            self._log_message("Starting pickplace controller setup with custom coordinates...")

            # Import the stacking controller
            self._log_message("Importing PickPlaceController...")
            try:
                from omni.isaac.franka.controllers import PickPlaceController
                self._log_message("PickPlaceController imported successfully")
            except ImportError as e:
                self._log_message(f"Failed to import PickPlaceController: {str(e)}")
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
                cube_names.append(cube.name)
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
            self._log_message("Creating PickPlaceController with custom cube positions...")
            self._controller = PickPlaceController(
                name="pick_place_controller",
                gripper=gripper,
                robot_articulation=self._franka,
            )
            self._log_message("PickPlaceController created successfully")

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

            # IMPORTANT: Setup observations for the World
            self._log_message("Setting up World observations...")
            
            # Add robot observations
            self._world.add_physics_callback("observations", self._update_observations)
            
            # Initialize observations dictionary
            self._observations = {}
            self._update_observations(0.0)  # Initial update
            
            self._log_message("World observations configured")

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

    def _update_observations(self, step_size):
        """Update observations for the World"""
        try:
            if not self._franka or not self._cubes:
                return
            
            # Get robot state
            joint_positions = self._franka.get_joint_positions()
            joint_velocities = self._franka.get_joint_velocities()
            
            # Get end effector pose
            if hasattr(self._franka, 'end_effector'):
                ee_position, ee_orientation = self._franka.end_effector.get_world_pose()
            else:
                ee_position = np.array([0.0, 0.0, 0.0])
                ee_orientation = np.array([1.0, 0.0, 0.0, 0.0])
            
            # Update observations dictionary
            self._observations = {
                self._franka.name: {
                    "joint_positions": joint_positions,
                    "joint_velocities": joint_velocities,
                    "end_effector_position": ee_position,
                    "end_effector_orientation": ee_orientation,
                }
            }
            
            # Add cube observations
            for i, cube in enumerate(self._cubes):
                cube_position, cube_orientation = cube.get_world_pose()
                cube_velocity = cube.get_linear_velocity()
                
                self._observations[f"cube_{i}"] = {
                    "position": cube_position,
                    "orientation": cube_orientation,
                    "linear_velocity": cube_velocity,
                }
            
        except Exception as e:
            self._log_message(f"Error updating observations: {str(e)}")
    
    # Simpler approach for your specific case
    def extract_colors_simple(prompt):
        words = prompt.lower().split()
        colors = ['red', 'green', 'blue', 'yellow', 'orange', 'purple', 'pink', 'black', 'white', 'gray', 'brown']
        
        found_colors = [word for word in words if word in colors]
        
        pick_color = found_colors[0] if len(found_colors) > 0 else None
        place_color = found_colors[1] if len(found_colors) > 1 else None
        
        return pick_color, place_color



    def _on_stacking_physics_step(self, step_size):
        """Physics step callback for stacking execution with custom cube coordinates"""
        if not self._controller or not self._articulation_controller:
            return

        try:
            # Use our custom observations instead of World.get_observations()
            observations = getattr(self, '_observations', {})
            if not observations:
                self._log_message("Warning: No custom observations available")
                return
            
            # Log observation keys for debugging (only first few times)
            if not hasattr(self, '_obs_logged'):
                obs_keys = list(observations.keys())
                self._log_message(f"Available observation keys: {obs_keys}")
                for key, value in observations.items():
                    if isinstance(value, dict):
                        self._log_message(f"  {key}: {list(value.keys())}")
                self._obs_logged = True
            # extract pick and place positions from prompt
            pick_color, place_color = self.extract_colors_simple(self.prompt)

            #place position should be 0.1m above the pick position
            place_position = observations[f"cube_{pick_color}"]["position"] + np.array([0.0, 0.0, 0.1])

            # Get actions from stacking controller
            actions = self._controller.forward(
                picking_position=observations[f"cube_{pick_color}"]["position"],
                placing_position=place_position,
                current_joint_positions=observations[self._franka.name]["joint_positions"],
            )
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
            self.prompt = prompt

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
            if self._world and self._world.physics_callback_exists("observations"):
                self._world.remove_physics_callback("observations")
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
            if self._world and self._world.physics_callback_exists("observations"):
                self._world.remove_physics_callback("observations")
            self._controller = None
            self._articulation_controller = None
            self._franka = None
            self._cubes = []
            self._cube_positions = []
            self._observations = {}
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