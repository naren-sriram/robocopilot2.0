# Quick Installation Guide - RoboCopilot Extension

## Import Issues Fixed ✅

The extension has been updated to use relative imports, which should resolve the package import errors. Here's how to install it properly:

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
cp -r robocopilot_extension ~/.local/share/ov/pkg/isaac_sim-*/exts/
```

### 3. Verify Directory Structure

After copying, your Isaac Sim extensions directory should contain:
```
isaac_sim-*/exts/
└── robocopilot_extension/
    ├── __init__.py
    ├── robocopilot_stack.py
    ├── robocopilot_extension.py
    ├── extension.toml
    ├── docs/
    └── other files...
```

### 4. Enable in Isaac Sim

1. Open Isaac Sim
2. Go to **Window > Extensions**
3. Search for "RoboCopilot"
4. Toggle the extension ON
5. If you see any errors, check the Console window

### 5. Access the Extension

1. Go to **Isaac Examples > Manipulation > RoboCopilot Stack**
2. The extension window should open
3. Click **Load** to initialize the scene
4. Start using the chat interface!

## Recent Fixes

✅ **Import Error Fixed**: Changed from absolute imports (`from robocopilot_extension.module`) to relative imports (`from .module`)  
✅ **Package Structure**: Proper Python package structure with relative imports  
✅ **Isaac Sim Compatibility**: Follows Isaac Sim extension development patterns  

## Troubleshooting

### Import Errors
- The extension now uses relative imports which should work properly
- Ensure the directory is named `robocopilot_extension` (with underscore)
- Check that all files are present in the extension directory
- Restart Isaac Sim after copying the extension

### Extension Not Appearing
- Verify the extension.toml file is present
- Check the Extensions window for any error messages
- Look at the Isaac Sim console for detailed error information

### Execute Button Disabled
- Make sure to click "Load" first to initialize the scene
- Check that all required Isaac extensions are enabled (Examples, Manipulators, Franka)

## Success Indicators

✅ Extension appears in Extensions window  
✅ No import errors in console  
✅ "RoboCopilot Stack" appears in Isaac Examples > Manipulation  
✅ Chat interface loads properly  
✅ Execute Task button becomes enabled after loading scene  

## Next Steps

Once installed successfully:
1. Load the scene
2. Enter commands like "Stack the cubes on top of each other"
3. Click "🚀 Execute Task"
4. Watch the Franka robot perform the stacking operation!

The extension performs the same cube stacking as the original Simple Stack but with an enhanced chat-based interface. 