# RoboCopilot Stack Extension

An AI-powered stacking interface with chat functionality for Isaac Sim manipulation tasks using the Franka robot.

## Overview

The RoboCopilot Stack Extension provides an intuitive chat-based interface for controlling robotic manipulation tasks in Isaac Sim. While the underlying functionality performs the same cube stacking operations as the Simple Stack example, this extension enhances the user experience with:

- **🤖 Chat Interface**: Natural language command input with visual feedback
- **🚀 Execute Task Button**: Clear action button for task execution
- **📊 Real-time Status**: Live system status updates and execution monitoring
- **💬 Interactive Feedback**: Conversational interface with timestamped messages

## Features

### Chat Interface
- **Text Input Field**: Enter natural language commands for the robot
- **Chat History**: View conversation history with timestamps
- **Visual Feedback**: Distinct styling for user and system messages
- **Send Button**: Submit commands to the chat (visual feedback only)

### Task Control
- **Execute Task Button**: Triggers the actual stacking operation
- **Status Display**: Real-time system status with color-coded indicators
- **Clear Chat**: Reset conversation history
- **Refresh Status**: Update system status manually

### Enhanced User Experience
- **Emoji Icons**: Intuitive visual elements throughout the interface
- **Color-coded Messages**: Easy distinction between user and system messages
- **Responsive Layout**: Collapsible frames for optimal workspace usage
- **Tooltips**: Helpful descriptions for all interactive elements

## Usage

### Getting Started

1. **Load the Extension**
   - Open Isaac Sim
   - Navigate to the Extensions window
   - Search for "RoboCopilot Stack"
   - Enable the extension

2. **Open the Interface**
   - Go to Isaac Examples > Manipulation > RoboCopilot Stack
   - The extension window will open with the chat interface

3. **Load the Scene**
   - Click "Load" to initialize the Franka robot and cubes
   - Wait for the scene to fully load

### Using the Chat Interface

1. **Enter Commands**
   - Type your command in the text input field
   - Example: "Stack the cubes on top of each other"
   - Click "📤 Send" for visual feedback (optional)

2. **Execute Tasks**
   - Click "🚀 Execute Task" to run the stacking operation
   - The system will use the current text in the input field
   - Monitor progress through the status display and chat messages

3. **Monitor Progress**
   - Watch the status indicator for real-time updates
   - View execution logs in the chat history
   - Use "🔄 Refresh" to update status manually

### Example Commands

While the extension currently performs cube stacking regardless of the specific command, you can enter various natural language instructions:

- "Stack the cubes on top of each other"
- "Pick up the bottom cube and place it on the top cube"
- "Perform a stacking operation"
- "Arrange the cubes vertically"
- "Execute cube manipulation task"

## Technical Details

### Architecture

The extension consists of two main components:

1. **RoboCopilotStack**: Core functionality class that extends the original SimpleStack
   - Maintains execution logs and status
   - Provides enhanced task execution with prompt context
   - Manages system state and feedback

2. **RoboCopilotUI**: Enhanced user interface class
   - Implements chat interface with message history
   - Provides visual feedback and status updates
   - Handles user interactions and task execution

### Key Enhancements

- **Chat Message System**: Timestamped conversation history
- **Status Management**: Real-time task status tracking
- **Visual Styling**: Modern UI with color-coded elements
- **Error Handling**: Graceful handling of various system states
- **Extensibility**: Designed for future AI integration

## Installation

### Prerequisites

- Isaac Sim 4.5.0 or later
- Isaac Examples extension enabled
- Isaac Manipulators extension enabled
- Isaac Franka extension enabled

### Installation Steps

1. Copy the `robocopilot-extension` folder to your Isaac Sim extensions directory
2. Enable the extension through the Extensions window
3. The extension will appear in Isaac Examples > Manipulation

## Development

### File Structure

```
robocopilot-extension/
├── __init__.py                 # Extension module initialization
├── robocopilot_stack.py       # Core functionality class
├── robocopilot_extension.py   # UI and extension management
├── extension.toml             # Extension configuration
└── docs/
    ├── README.md              # This documentation
    └── CHANGELOG.md           # Version history
```

### Customization

The extension is designed to be easily customizable:

- **UI Layout**: Modify frame sizes and arrangements in `build_extra_frames()`
- **Chat Styling**: Update colors and fonts in the UI styling dictionaries
- **Status Messages**: Customize feedback messages in the various event handlers
- **Task Logic**: Extend the core functionality in `RoboCopilotStack`

### Future Enhancements

Potential areas for extension:

- **AI Integration**: Connect to language models for intelligent command parsing
- **Multi-task Support**: Extend beyond stacking to other manipulation tasks
- **Voice Interface**: Add speech-to-text capabilities
- **Advanced Visualization**: Enhanced 3D feedback and planning visualization
- **Real Robot Integration**: Support for physical Franka robots

## Troubleshooting

### Common Issues

1. **Extension Not Loading**
   - Verify all dependencies are installed
   - Check Isaac Sim version compatibility
   - Review extension.toml configuration

2. **Execute Button Disabled**
   - Ensure scene is loaded properly
   - Check that all required objects are present
   - Try resetting the scene

3. **Chat Interface Not Responding**
   - Verify UI components are properly initialized
   - Check for any console errors
   - Try refreshing the extension

### Support

For issues and questions:
- Check the Isaac Sim documentation
- Review the original Simple Stack example
- Consult the Isaac Sim community forums

## License

Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.

NVIDIA CORPORATION and its licensors retain all intellectual property and proprietary rights in and to this software, related documentation and any modifications thereto. 