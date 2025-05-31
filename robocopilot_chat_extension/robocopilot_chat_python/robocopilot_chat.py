# Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto. Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from isaacsim.examples.interactive.base_sample import BaseSample
from isaacsim.robot.manipulators.examples.franka.controllers.stacking_controller import StackingController
from isaacsim.robot.manipulators.examples.franka.tasks import Stacking


class RoboCopilotChat(BaseSample):
    """RoboCopilot Chat implementation based on SimpleStack with enhanced logging and chat functionality"""
    
    def __init__(self) -> None:
        super().__init__()
        self._controller = None
        self._articulation_controller = None
        self._execution_log = []
        self._current_status = "Ready"

    def setup_scene(self):
        """Setup the scene with Franka robot and stacking task"""
        world = self.get_world()
        world.add_task(Stacking(name="stacking_task"))
        self._log_message("Scene setup completed")
        return

    async def setup_post_load(self):
        """Setup controllers after scene is loaded"""
        self._franka_task = self._world.get_task(name="stacking_task")
        self._task_params = self._franka_task.get_params()
        my_franka = self._world.scene.get_object(self._task_params["robot_name"]["value"])
        
        self._controller = StackingController(
            name="stacking_controller",
            gripper=my_franka.gripper,
            robot_articulation=my_franka,
            picking_order_cube_names=self._franka_task.get_cube_names(),
            robot_observation_name=my_franka.name,
        )
        self._articulation_controller = my_franka.get_articulation_controller()
        self._log_message("Controllers initialized")
        self._current_status = "Ready for execution"
        return

    def _on_stacking_physics_step(self, step_size):
        """Physics step callback for stacking execution"""
        observations = self._world.get_observations()
        actions = self._controller.forward(observations=observations)
        self._articulation_controller.apply_action(actions)
        
        if self._controller.is_done():
            self._world.pause()
            self._log_message("Stacking task completed successfully")
            self._current_status = "Task completed"
        return

    async def _on_execute_task_async(self, prompt="Stack the cubes"):
        """Execute the stacking task asynchronously with prompt context"""
        self._log_message(f"Executing task: {prompt}")
        self._current_status = "Executing task..."
        
        world = self.get_world()
        world.add_physics_callback("sim_step", self._on_stacking_physics_step)
        await world.play_async()
        return

    async def setup_pre_reset(self):
        """Cleanup before reset"""
        world = self.get_world()
        if world.physics_callback_exists("sim_step"):
            world.remove_physics_callback("sim_step")
        if self._controller:
            self._controller.reset()
        self._log_message("System reset")
        self._current_status = "Reset completed"
        return

    def world_cleanup(self):
        """Clean up world resources"""
        self._controller = None
        self._log_message("World cleanup completed")
        self._current_status = "Cleaned up"
        return

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