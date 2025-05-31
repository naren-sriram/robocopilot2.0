# Quick Installation Guide - RoboCopilot Standalone Extension

## ✅ Standalone Extension Ready!

The RoboCopilot extension has been converted to a **standalone extension** that appears in the Isaac Sim Extensions window and creates its own UI window, rather than appearing in the Isaac Examples menu.

## Installation Steps

### 1. Find Your Isaac Sim Extensions Directory

The typical locations are:
- **Linux**: `~/.local/share/ov/pkg/isaac_sim-*/exts/`
- **Windows**: `%USERPROFILE%\AppData\Local\ov\pkg\isaac_sim-*\exts\`

### 2. Copy the Extension

```bash
# Navigate to your workspace
cd /path/to/your/workspace

# Copy the extension to Isaac Sim extensions directory
cp -r robocopilot_chat_extension ~/.local/share/ov/pkg/isaac_sim-*/exts/
```

### 3. Verify Directory Structure

After copying, your Isaac Sim extensions directory should contain:
```
isaac_sim-*/exts/
└── robocopilot_chat_extension/
    ├── config/
    │   └── extension.toml
    ├── robocopilot_chat_python/
    │   ├── __init__.py
    │   ├── extension.py
    │   ├── ui_builder.py
    │   ├── robocopilot_chat.py
    │   └── global_variables.py
    ├── data/
    └── docs/
```

### 4. Enable the Extension

1. Open Isaac Sim
2. Go to **Window > Extensions**
3. Search for "RoboCopilot Chat"
4. Toggle the extension **ON**
5. Check the Console window for any errors

### 5. Access the Extension

1. After enabling, look for **"RoboCopilot Chat"** in the Isaac Sim menu bar
2. Click on it to open the extension window
3. The extension window will dock to the left side of the viewport

## How to Use the Standalone Extension

### 1. **Scene Control**
- Click **"🔄 Load Scene"** to initialize the Franka robot and cubes
- Use **"🔄 Reset Scene"** to reset the simulation
- Use **"🗑️ Clear Scene"** to clear everything

### 2. **Chat Interface**
- Enter natural language commands in the text field
- Click **"📤 Send"** to add your message to the chat
- View conversation history in the chat display

### 3. **Task Execution**
- After loading the scene, click **"🚀 Execute Task"** to run the stacking operation
- Monitor the system status and chat for feedback
- Use **"🗑️ Clear Chat"** to clear the conversation history

## Key Features

✅ **Standalone Window**: Creates its own dockable window  
✅ **Scene Management**: Load, reset, and clear scenes independently  
✅ **Chat Interface**: Natural language command input with history  
✅ **Real-time Status**: Live status updates and error handling  
✅ **Task Execution**: Execute Franka robot stacking tasks  
✅ **Visual Feedback**: Color-coded messages and status indicators  

## Extension Architecture

The extension now follows the standard Isaac Sim extension pattern:

- **`extension.py`**: Main extension class that creates the UI window and menu
- **`ui_builder.py`**: Contains all UI logic and RoboCopilot functionality
- **`robocopilot_chat.py`**: Core stacking task implementation
- **`global_variables.py`**: Extension title and description
- **`extension.toml`**: Extension configuration with proper dependencies

## Troubleshooting

### Extension Not Appearing
- Ensure the extension is enabled in the Extensions window
- Check the Console for any import errors
- Verify the directory structure matches the example above

### Menu Item Missing
- Look for "RoboCopilot Chat" in the Isaac Sim menu bar
- If not visible, try disabling and re-enabling the extension
- Restart Isaac Sim if necessary

### Scene Loading Issues
- Ensure Isaac Sim has the required Franka and manipulation extensions enabled
- Check the Console for detailed error messages
- Try clearing and reloading the scene

## Success Indicators

✅ Extension appears in Extensions window without errors  
✅ "RoboCopilot Chat" menu item appears in Isaac Sim menu bar  
✅ Extension window opens and docks properly  
✅ Scene loads successfully with Franka robot and cubes  
✅ Chat interface responds to user input  
✅ Execute Task button works and runs stacking operation  

## Next Steps

1. **Enable the extension** in Isaac Sim Extensions window
2. **Click "RoboCopilot Chat"** in the menu bar to open the window
3. **Load the scene** using the Load Scene button
4. **Enter commands** like "Stack the cubes on top of each other"
5. **Execute tasks** and watch the Franka robot perform stacking operations!

The extension now operates as a fully standalone Isaac Sim extension with its own window and menu integration. 