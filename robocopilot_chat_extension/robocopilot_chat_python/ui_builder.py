# Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto. Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import asyncio
from datetime import datetime

import omni.ui as ui
from isaacsim.core.api.world import World
from isaacsim.examples.extension.core_connectors import LoadButton, ResetButton
from isaacsim.gui.components.element_wrappers import CollapsableFrame
from isaacsim.gui.components.ui_utils import get_style

from .robocopilot_chat import RoboCopilotChat


class UIBuilder:
    def __init__(self):
        """Initialize the UI builder with RoboCopilot functionality"""
        self.chat_messages = []
        self.current_prompt = ""
        self.task_ui_elements = {}
        self.robocopilot_sample = None
        self.world = None
        self.wrapped_ui_elements = []  # For cleanup

    def on_menu_callback(self):
        """Called when the extension menu is opened"""
        print("RoboCopilot Chat extension opened")

    def on_timeline_event(self, event):
        """Called when timeline events occur (play, pause, stop)"""
        pass

    def on_physics_step(self, step):
        """Called on every physics step"""
        pass

    def on_stage_event(self, event):
        """Called when stage events occur (open, close)"""
        pass

    def cleanup(self):
        """Clean up resources"""
        # Clean up wrapped UI elements
        for ui_elem in self.wrapped_ui_elements:
            if hasattr(ui_elem, 'cleanup'):
                ui_elem.cleanup()
        
        if self.robocopilot_sample:
            self.robocopilot_sample.world_cleanup()
        self.robocopilot_sample = None
        self.world = None

    def build_ui(self):
        """Build the main UI for RoboCopilot Chat"""
        with ui.VStack(spacing=10):
            # Header
            ui.Label(
                "🤖 RoboCopilot Chat Interface",
                height=30,
                style={"font_size": 18, "color": 0xFF00AAFF, "font_weight": "bold"}
            )

            ui.Separator(height=2)

            # Scene Control Section
            with ui.CollapsableFrame(
                title="🎬 Scene Control",
                height=120,
                collapsed=False,
            ):
                self._build_scene_controls()

            # Chat Interface Section
            with ui.CollapsableFrame(
                title="Chat Interface",
                height=300,
                collapsed=False,
            ):
                self._build_chat_interface()

            # Task Control Section
            with ui.CollapsableFrame(
                title="🎯 Task Control",
                height=150,
                collapsed=False,
            ):
                self._build_task_controls()

    def _build_scene_controls(self):
        """Build scene loading and control UI"""
        with ui.VStack(spacing=5):
            ui.Label("Scene Management:", style={"font_size": 14})

            with ui.HStack(spacing=5):
                self._load_btn = LoadButton(
                    "Load Button", 
                    "Load Scene",
                    setup_scene_fn=self._setup_scene,
                    setup_post_load_fn=self._setup_post_load
                )
                self._load_btn.set_world_settings(physics_dt=1 / 60.0, rendering_dt=1 / 60.0)
                self.wrapped_ui_elements.append(self._load_btn)

                self._reset_btn = ResetButton(
                    "Reset Button",
                    "Reset Scene", 
                    pre_reset_fn=self._pre_reset,
                    post_reset_fn=self._post_reset
                )
                self._reset_btn.enabled = False
                self.wrapped_ui_elements.append(self._reset_btn)

                clear_btn = ui.Button(
                    "🗑️ Clear Scene",
                    height=30,
                    clicked_fn=self._on_clear_scene,
                    style={"background_color": 0xFFFF6600}
                )

            # Status display
            self.scene_status_label = ui.Label(
                "Scene not loaded",
                height=25,
                style={"font_size": 12, "color": 0xFFFF6600}
            )

    def _build_chat_interface(self):
        """Build the chat interface UI"""
        with ui.VStack(spacing=10):
            # Chat display area
            ui.Label("Chat History:", style={"font_size": 14, "color": 0xFF00AAFF})

            with ui.ScrollingFrame(height=180):
                self.chat_display = ui.VStack(spacing=5)
                self._update_chat_display()

            # Input area
            ui.Label("Enter your command:", style={"font_size": 12})

            with ui.HStack(spacing=5, height=30):
                self.prompt_input = ui.StringField(
                    height=25,
                    style={"background_color": 0xFF1E1E1E, "border_color": 0xFF00AAFF, "border_width": 1}
                )
                self.prompt_input.model.set_value("Stack the cubes on top of each other")

                send_btn = ui.Button(
                    "📤 Send",
                    width=80,
                    height=25,
                    clicked_fn=self._on_send_message,
                    style={"background_color": 0xFF00AA00, "color": 0xFFFFFFFF}
                )

    def _build_task_controls(self):
        """Build task control UI"""
        with ui.VStack(spacing=10):
            # Status display
            ui.Label("System Status:", style={"font_size": 14, "color": 0xFF00AAFF})
            self.status_label = ui.Label(
                "Ready",
                height=25,
                style={"font_size": 12, "color": 0xFF00FF00}
            )

            # Control buttons
            with ui.HStack(spacing=5):
                execute_btn = ui.Button(
                    "Execute Task",
                    height=35,
                    clicked_fn=self._on_execute_task,
                    style={"background_color": 0xFF0066CC, "color": 0xFFFFFFFF, "font_size": 14}
                )
                execute_btn.enabled = False  # Disabled until scene is loaded
                self.task_ui_elements["Execute Task"] = execute_btn

                clear_chat_btn = ui.Button(
                    "Clear Chat",
                    height=35,
                    clicked_fn=self._on_clear_chat,
                    style={"background_color": 0xFF666666, "color": 0xFFFFFFFF}
                )

    def _update_chat_display(self):
        """Update the chat display with current messages"""
        self.chat_display.clear()

        if not self.chat_messages:
            with self.chat_display:
                ui.Label(
                    "👋 Welcome to RoboCopilot! Load a scene and enter commands to begin.",
                    word_wrap=True,
                    style={"color": 0xFF888888, "font_size": 11}
                )
        else:
            with self.chat_display:
                for message in self.chat_messages[-10:]:  # Show last 10 messages
                    timestamp = message.get("timestamp", "")
                    sender = message.get("sender", "")
                    text = message.get("text", "")

                    # Message styling based on sender
                    if sender == "User":
                        color = 0xFF00AAFF
                        bg_color = 0xFF2A2A2A
                        icon = "👤"
                    else:
                        color = 0xFF00FF00
                        bg_color = 0xFF1A3A1A
                        icon = "🤖"

                    with ui.VStack(spacing=2):
                        ui.Label(
                            f"{icon} {sender} ({timestamp}):",
                            style={"color": color, "font_size": 10}
                        )
                        ui.Label(
                            text,
                            word_wrap=True,
                            style={"color": 0xFFFFFFFF, "font_size": 11, "background_color": bg_color}
                        )
                    ui.Spacer(height=5)

    def _add_chat_message(self, sender, text):
        """Add a message to the chat"""
        timestamp = datetime.now().strftime("%H:%M")
        self.chat_messages.append({
            "sender": sender,
            "text": text,
            "timestamp": timestamp
        })
        self._update_chat_display()

    def _setup_scene(self):
        """Setup scene callback for LoadButton - creates the scene and adds objects to World"""
        try:
            # Create RoboCopilot sample
            if not self.robocopilot_sample:
                self.robocopilot_sample = RoboCopilotChat()
                self._add_chat_message("RoboCopilot", "🔄 Creating RoboCopilot sample...")
            
            # Setup the scene (this will create stage and add objects)
            self._add_chat_message("RoboCopilot", "🔄 Setting up scene...")
            success = self.robocopilot_sample.setup_scene()
            
            if not success:
                self.robocopilot_sample = None  # Clear failed sample
                raise Exception("Failed to setup scene")
            
            # Get the world instance (created by LoadButton)
            self.world = World.instance()
            
            # Update scene status immediately
            self.scene_status_label.text = "Scene setup completed"
            self.scene_status_label.style = {"color": 0xFF00FF00, "font_size": 12}
            
            self._add_chat_message("RoboCopilot", "Scene created successfully...")
            
        except Exception as e:
            # Clear the sample if setup failed
            self.robocopilot_sample = None
            self.scene_status_label.text = f"Scene setup failed: {str(e)}"
            self.scene_status_label.style = {"color": 0xFFFF0000, "font_size": 12}
            self._add_chat_message("RoboCopilot", f"Error setting up scene: {str(e)}")
            print(f"Scene setup error: {e}")
            import traceback
            traceback.print_exc()
            # Re-raise the exception so LoadButton knows setup failed
            raise

    def _setup_post_load(self):
        """Post-load callback for LoadButton - setup controllers after World is initialized"""
        try:
            # Setup controllers asynchronously
            asyncio.ensure_future(self._setup_post_load_async())
            
        except Exception as e:
            self.scene_status_label.text = f"Error in post-load: {str(e)}"
            self.scene_status_label.style = {"color": 0xFFFF0000, "font_size": 12}
            self._add_chat_message("RoboCopilot", f" Error in post-load: {str(e)}")
            print(f"Post-load error: {e}")
            import traceback
            traceback.print_exc()

    async def _setup_post_load_async(self):
        """Async version of post-load setup"""
        try:
            # Check if robocopilot_sample exists
            if not self.robocopilot_sample:
                raise Exception("RoboCopilot sample not initialized")
            
            # Setup controllers
            success = await self.robocopilot_sample.setup_post_load()
            
            if not success:
                raise Exception("Failed to setup controllers")
            
            # Update status
            self.scene_status_label.text = "Scene loaded successfully"
            self.scene_status_label.style = {"color": 0xFF00FF00, "font_size": 12}
            
            # Enable buttons
            if hasattr(self, '_reset_btn'):
                self._reset_btn.enabled = True
            if "Execute Task" in self.task_ui_elements:
                self.task_ui_elements["Execute Task"].enabled = True
            
            self._add_chat_message("RoboCopilot", "Scene loaded successfully! Ready to execute tasks.")
            
        except Exception as e:
            # Clear sample on controller setup failure
            if self.robocopilot_sample:
                self.robocopilot_sample.world_cleanup()
                self.robocopilot_sample = None
                
            self.scene_status_label.text = f"Controller setup failed: {str(e)}"
            self.scene_status_label.style = {"color": 0xFFFF0000, "font_size": 12}
            self._add_chat_message("RoboCopilot", f"Error in controller setup: {str(e)}")
            print(f"Async post-load error: {e}")
            import traceback
            traceback.print_exc()

    def _pre_reset(self):
        """Pre-reset callback for ResetButton"""
        try:
            if self.robocopilot_sample:
                asyncio.ensure_future(self.robocopilot_sample.setup_pre_reset())
        except Exception as e:
            self._add_chat_message("RoboCopilot", f"Error in pre-reset: {str(e)}")

    def _post_reset(self):
        """Post-reset callback for ResetButton"""
        try:
            self.scene_status_label.text = "Scene reset"
            self.scene_status_label.style = {"color": 0xFFFFAA00, "font_size": 12}
            self._add_chat_message("RoboCopilot", "🔄 Scene reset successfully.")
        except Exception as e:
            self._add_chat_message("RoboCopilot", f"Error in post-reset: {str(e)}")

    def _on_clear_scene(self):
        """Clear the scene"""
        try:
            # Clean up RoboCopilot sample first
            if self.robocopilot_sample:
                self.robocopilot_sample.world_cleanup()
                self.robocopilot_sample = None

            # Clear the world
            if self.world:
                self.world.clear()
                self.world = None

            # Update UI state
            self.scene_status_label.text = "Scene cleared"
            self.scene_status_label.style = {"color": 0xFF888888, "font_size": 12}

            # Disable buttons
            if hasattr(self, '_reset_btn'):
                self._reset_btn.enabled = False
            if "Execute Task" in self.task_ui_elements:
                self.task_ui_elements["Execute Task"].enabled = False

            self._add_chat_message("RoboCopilot", "🧹 Scene cleared.")

        except Exception as e:
            self._add_chat_message("RoboCopilot", f"Error clearing scene: {str(e)}")
            print(f"Clear scene error: {e}")

    def _on_send_message(self):
        """Handle sending a message"""
        prompt = self.prompt_input.model.get_value_as_string().strip()
        if prompt:
            self._add_chat_message("User", prompt)
            self._add_chat_message("RoboCopilot", f"Command received: '{prompt}'. Click 'Execute Task' to run.")
            self.current_prompt = prompt

    def _on_execute_task(self):
        """Execute the stacking task"""
        prompt = self.prompt_input.model.get_value_as_string().strip()
        if not prompt:
            prompt = "Stack the cubes"

        # Check if scene is properly loaded
        if not self.robocopilot_sample:
            self._add_chat_message("RoboCopilot", "Please load the scene first!")
            return
            
        if not self.world:
            self._add_chat_message("RoboCopilot", "World not initialized. Please load the world first!")
            return

        self.current_prompt = prompt
        self._add_chat_message("User", prompt)
        self._add_chat_message("RoboCopilot", f"🚀 Executing task: {prompt}")

        # Update status
        self.status_label.text = "Executing Task..."
        self.status_label.style = {"color": 0xFFFFAA00, "font_size": 12}

        # Disable execute button during execution
        if "Execute Task" in self.task_ui_elements:
            self.task_ui_elements["Execute Task"].enabled = False

        # Execute the task
        asyncio.ensure_future(self._execute_task_async(prompt))

    async def _execute_task_async(self, prompt):
        """Execute the task asynchronously"""
        try:
            await self.robocopilot_sample._on_execute_task_async(prompt)

            # Re-enable execute button
            if "Execute Task" in self.task_ui_elements:
                self.task_ui_elements["Execute Task"].enabled = True

            self.status_label.text = "Task Completed"
            self.status_label.style = {"color": 0xFF00AAFF, "font_size": 12}
            self._add_chat_message("RoboCopilot", "Task completed successfully!")

        except Exception as e:
            if "Execute Task" in self.task_ui_elements:
                self.task_ui_elements["Execute Task"].enabled = True

            self.status_label.text = "Task Failed"
            self.status_label.style = {"color": 0xFFFF0000, "font_size": 12}
            self._add_chat_message("RoboCopilot", f"Task failed: {str(e)}")

    def _on_clear_chat(self):
        """Clear the chat history"""
        self.chat_messages = []
        self._update_chat_display()
        if self.robocopilot_sample:
            self.robocopilot_sample.clear_execution_log()
        self._add_chat_message("RoboCopilot", "Chat history cleared. Ready for new commands!")