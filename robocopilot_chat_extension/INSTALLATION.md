# RoboCopilot Extension - Installation Guide

## Quick Start

### 1. Prerequisites
- Isaac Sim 4.5.0 or later installed
- All required Isaac extensions enabled (Examples, Manipulators, Franka, Core, UI)

### 2. Installation Options

#### Option A: Copy to Extensions Directory
```bash
# Copy the extension to Isaac Sim extensions directory
cp -r robocopilot-extension ~/.local/share/ov/pkg/isaac_sim-*/exts/
```

#### Option B: Development Mode
```bash
# For development, you can link the extension
ln -s /path/to/robocopilot-extension ~/.local/share/ov/pkg/isaac_sim-*/exts/
```

### 3. Enable the Extension

1. Open Isaac Sim
2. Go to **Window > Extensions**
3. Search for "RoboCopilot Stack"
4. Click the toggle to enable the extension

### 4. Access the Extension

1. Go to **Isaac Examples > Manipulation > RoboCopilot Stack**
2. The extension window will open
3. Click **Load** to initialize the scene
4. Start using the chat interface!

## Usage

### Basic Workflow

1. **Load Scene**: Click "Load" button to set up Franka robot and cubes
2. **Enter Command**: Type your instruction in the chat input field
   - Example: "Stack the cubes on top of each other"
3. **Execute Task**: Click "🚀 Execute Task" to run the operation
4. **Monitor Progress**: Watch the status and chat for updates

### Interface Elements

- **💬 Chat History**: Shows conversation with timestamps
- **✍️ Command Input**: Enter natural language instructions
- **📤 Send Button**: Add message to chat (visual feedback)
- **🚀 Execute Task**: Run the stacking operation
- **📊 Status Display**: Real-time system status
- **🗑️ Clear Chat**: Reset conversation history
- **🔄 Refresh**: Update system status

## Troubleshooting

### Extension Not Appearing
- Verify Isaac Sim version compatibility
- Check that all dependencies are installed
- Restart Isaac Sim after installation

### Execute Button Disabled
- Ensure scene is loaded properly
- Check console for any error messages
- Try resetting the scene with the Reset button

### Chat Interface Issues
- Refresh the extension window
- Check Isaac Sim console for errors
- Verify UI components loaded correctly

## Development

### File Structure
```
robocopilot-extension/
├── __init__.py                 # Module initialization
├── robocopilot_stack.py       # Core functionality
├── robocopilot_chat.py   # UI and extension logic
├── extension.toml             # Extension configuration
├── docs/                      # Documentation
└── INSTALLATION.md            # This file
```

### Customization
- Modify UI layout in `robocopilot_chat.py`
- Extend functionality in `robocopilot_stack.py`
- Update styling and colors in the UI classes
- Add new features following Isaac Sim extension patterns

For more detailed information, see the full README.md in the docs/ directory. 