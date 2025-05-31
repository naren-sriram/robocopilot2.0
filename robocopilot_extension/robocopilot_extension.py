# Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto. Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import asyncio
import os
from datetime import datetime

import omni.ext
import omni.ui as ui
from isaacsim.examples.browser import get_instance as get_browser_instance
from isaacsim.examples.interactive.base_sample import BaseSampleUITemplate
from .robocopilot_stack import RoboCopilotStack
from isaacsim.gui.components.ui_utils import btn_builder


class RoboCopilotExtension(omni.ext.IExt):
    def on_startup(self, ext_id: str):
        self.example_name = "RoboCopilot Stack"
        self.category = "Manipulation"

        ui_kwargs = {
            "ext_id": ext_id,
            "file_path": os.path.abspath(__file__),
            "title": "RoboCopilot Stack",
            "doc_link": "https://docs.isaacsim.omniverse.nvidia.com/latest/core_api_tutorials/tutorial_core_adding_manipulator.html",
            "overview": "This Extension shows an AI-powered stacking interface using Franka robot in Isaac Sim.\n\nEnter natural language commands in the chat window and click 'Execute Task' to perform stacking operations.\n\nPress the 'Open in IDE' button to view the source code.",
            "sample": RoboCopilotStack(),
        }

        ui_handle = RoboCopilotUI(**ui_kwargs)

        get_browser_instance().register_example(
            name=self.example_name,
            execute_entrypoint=ui_handle.build_window,
            ui_hook=ui_handle.build_ui,
            category=self.category,
        )

        return

    def on_shutdown(self):
        get_browser_instance().deregister_example(name=self.example_name, category=self.category)
        return


class RoboCopilotUI(BaseSampleUITemplate):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chat_messages = []
        self.current_prompt = ""

    def build_extra_frames(self):
        extra_stacks = self.get_extra_frames_handle()
        self.task_ui_elements = {}

        with extra_stacks:
            # Chat Interface Frame
            with ui.CollapsableFrame(
                title="🤖 RoboCopilot Chat Interface",
                width=ui.Fraction(0.5),
                height=300,
                visible=True,
                collapsed=False,
                horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
                vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
            ):
                self.build_chat_interface()

            # Task Control Frame
            with ui.CollapsableFrame(
                title="🎯 Task Control",
                width=ui.Fraction(0.5),
                height=200,
                visible=True,
                collapsed=False,
                horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
                vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
            ):
                self.build_task_controls_ui()

    def build_chat_interface(self):
        with ui.VStack(spacing=10, height=0):
            # Chat display area
            ui.Label("💬 Chat History:", height=20, style={"font_size": 14, "color": 0xFF00AAFF})
            
            with ui.ScrollingFrame(height=180, horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED):
                self.chat_display = ui.VStack(spacing=5)
                self._update_chat_display()

            # Input area
            ui.Spacer(height=5)
            ui.Label("✍️ Enter your command:", height=20, style={"font_size": 12})
            
            with ui.HStack(spacing=5, height=30):
                self.prompt_input = ui.StringField(
                    height=25,
                    style={"background_color": 0xFF1E1E1E, "border_color": 0xFF00AAFF, "border_width": 1}
                )
                self.prompt_input.model.set_value("Stack the cubes on top of each other")
                
                # Send button (for visual feedback, but doesn't actually send)
                send_btn = ui.Button(
                    "📤 Send",
                    width=80,
                    height=25,
                    clicked_fn=self._on_send_message,
                    style={"background_color": 0xFF00AA00, "color": 0xFFFFFFFF}
                )

    def build_task_controls_ui(self):
        with ui.VStack(spacing=10):
            # Status display
            ui.Label("📊 System Status:", height=20, style={"font_size": 14, "color": 0xFF00AAFF})
            self.status_label = ui.Label(
                "Ready", 
                height=25,
                style={"font_size": 12, "color": 0xFF00FF00, "background_color": 0xFF1E1E1E}
            )

            ui.Spacer(height=10)

            # Main execute button
            execute_dict = {
                "label": "Execute Task",
                "type": "button",
                "text": "🚀 Execute Task",
                "tooltip": "Execute the task based on the current prompt",
                "on_clicked_fn": self._on_execute_task_event,
            }
            self.task_ui_elements["Execute Task"] = btn_builder(**execute_dict)
            self.task_ui_elements["Execute Task"].enabled = False
            self.task_ui_elements["Execute Task"].style = {
                "background_color": 0xFF0066CC,
                "color": 0xFFFFFFFF,
                "font_size": 14
            }

            ui.Spacer(height=5)

            # Additional control buttons
            with ui.HStack(spacing=5):
                clear_chat_dict = {
                    "label": "Clear Chat",
                    "type": "button", 
                    "text": "🗑️ Clear Chat",
                    "tooltip": "Clear the chat history",
                    "on_clicked_fn": self._on_clear_chat,
                }
                self.task_ui_elements["Clear Chat"] = btn_builder(**clear_chat_dict)
                self.task_ui_elements["Clear Chat"].style = {
                    "background_color": 0xFF666666,
                    "color": 0xFFFFFFFF
                }

                refresh_dict = {
                    "label": "Refresh Status",
                    "type": "button",
                    "text": "🔄 Refresh",
                    "tooltip": "Refresh the system status",
                    "on_clicked_fn": self._on_refresh_status,
                }
                self.task_ui_elements["Refresh Status"] = btn_builder(**refresh_dict)
                self.task_ui_elements["Refresh Status"].style = {
                    "background_color": 0xFF666666,
                    "color": 0xFFFFFFFF
                }

    def _update_chat_display(self):
        """Update the chat display with current messages"""
        self.chat_display.clear()
        
        if not self.chat_messages:
            with self.chat_display:
                ui.Label(
                    "👋 Welcome to RoboCopilot! Enter a command above and click 'Execute Task' to begin.",
                    word_wrap=True,
                    style={"color": 0xFF888888, "font_size": 11}
                )
        else:
            with self.chat_display:
                for message in self.chat_messages[-10:]:  # Show last 10 messages
                    timestamp = message.get("timestamp", "")
                    sender = message.get("sender", "")
                    text = message.get("text", "")
                    
                    # Message container
                    with ui.HStack(spacing=5, height=0):
                        if sender == "User":
                            ui.Spacer(width=20)
                            with ui.VStack(spacing=2):
                                ui.Label(
                                    f"👤 You ({timestamp}):",
                                    style={"color": 0xFF00AAFF, "font_size": 10}
                                )
                                ui.Label(
                                    text,
                                    word_wrap=True,
                                    style={"color": 0xFFFFFFFF, "font_size": 11, "background_color": 0xFF2A2A2A}
                                )
                        else:
                            with ui.VStack(spacing=2):
                                ui.Label(
                                    f"🤖 RoboCopilot ({timestamp}):",
                                    style={"color": 0xFF00FF00, "font_size": 10}
                                )
                                ui.Label(
                                    text,
                                    word_wrap=True,
                                    style={"color": 0xFFFFFFFF, "font_size": 11, "background_color": 0xFF1A3A1A}
                                )
                            ui.Spacer(width=20)
                    
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

    def _on_send_message(self):
        """Handle sending a message (visual feedback only)"""
        prompt = self.prompt_input.model.get_value_as_string().strip()
        if prompt:
            self._add_chat_message("User", prompt)
            self._add_chat_message("RoboCopilot", f"Command received: '{prompt}'. Click 'Execute Task' to run the stacking operation.")
            self.current_prompt = prompt

    def _on_execute_task_event(self):
        """Handle the execute task button click"""
        prompt = self.prompt_input.model.get_value_as_string().strip()
        if not prompt:
            prompt = "Stack the cubes"
        
        self.current_prompt = prompt
        self._add_chat_message("User", prompt)
        self._add_chat_message("RoboCopilot", f"🚀 Executing task: {prompt}")
        
        # Update status
        self.status_label.text = "Executing Task..."
        self.status_label.style = {"color": 0xFFFFAA00, "font_size": 12, "background_color": 0xFF1E1E1E}
        
        # Disable execute button during execution
        self.task_ui_elements["Execute Task"].enabled = False
        
        # Execute the actual stacking task
        asyncio.ensure_future(self.sample._on_execute_task_async(prompt))
        
        # Add to sample's log
        self.sample.add_log_entry(f"User command: {prompt}")

    def _on_clear_chat(self):
        """Clear the chat history"""
        self.chat_messages = []
        self._update_chat_display()
        self.sample.clear_execution_log()
        self._add_chat_message("RoboCopilot", "Chat history cleared. Ready for new commands!")

    def _on_refresh_status(self):
        """Refresh the system status"""
        status = self.sample.get_task_status()
        self.status_label.text = status
        
        # Update status color based on state
        if "Ready" in status:
            self.status_label.style = {"color": 0xFF00FF00, "font_size": 12, "background_color": 0xFF1E1E1E}
        elif "Executing" in status:
            self.status_label.style = {"color": 0xFFFFAA00, "font_size": 12, "background_color": 0xFF1E1E1E}
        elif "Completed" in status:
            self.status_label.style = {"color": 0xFF00AAFF, "font_size": 12, "background_color": 0xFF1E1E1E}
        else:
            self.status_label.style = {"color": 0xFFFF0000, "font_size": 12, "background_color": 0xFF1E1E1E}

        # Show execution log in chat
        log_entries = self.sample.get_execution_log()
        if log_entries:
            latest_entry = log_entries[-1]
            self._add_chat_message("RoboCopilot", f"Status update: {latest_entry}")

    def post_reset_button_event(self):
        """Called after reset button is pressed"""
        self.task_ui_elements["Execute Task"].enabled = True
        self.status_label.text = "Ready"
        self.status_label.style = {"color": 0xFF00FF00, "font_size": 12, "background_color": 0xFF1E1E1E}
        self._add_chat_message("RoboCopilot", "🔄 System reset complete. Ready for new tasks!")

    def post_load_button_event(self):
        """Called after load button is pressed"""
        self.task_ui_elements["Execute Task"].enabled = True
        self.status_label.text = "Ready"
        self.status_label.style = {"color": 0xFF00FF00, "font_size": 12, "background_color": 0xFF1E1E1E}
        self._add_chat_message("RoboCopilot", "✅ Scene loaded successfully. Ready to execute tasks!")

    def post_clear_button_event(self):
        """Called after clear button is pressed"""
        self.task_ui_elements["Execute Task"].enabled = False
        self.status_label.text = "Scene Cleared"
        self.status_label.style = {"color": 0xFF888888, "font_size": 12, "background_color": 0xFF1E1E1E}
        self._add_chat_message("RoboCopilot", "🧹 Scene cleared. Please load a scene to continue.") 