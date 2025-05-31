# Quick Installation Guide - RoboCopilot Extension (Isaac Sim 4.5)

## Isaac Sim 4.5 Compatibility Updates ✅

This extension has been updated to address Isaac Sim 4.5 migration issues. Based on [NVIDIA Developer Forum discussions](https://forums.developer.nvidia.com/t/issues-with-extensions-moving-from-isaac-4-2-4-5/322302/3), several compatibility fixes have been implemented.

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
cp -r robocopilot_chat ~/.local/share/ov/pkg/isaac_sim-*/exts/
```

### 3. Verify Directory Structure

After copying, your Isaac Sim extensions directory should contain:
```
isaac_sim-*/exts/
└── robocopilot_chat/
    ├── __init__.py
    ├── robocopilot_chat.py
    ├── robocopilot_chat_extension.py
    ├── extension.toml
    ├── docs/
    └── other files...
```

### 4. Enable Required Extensions First

**IMPORTANT**: Before enabling RoboCopilot, ensure these extensions are enabled:
1. Go to **Window > Extensions**
2. Enable the following extensions:
   - `omni.isaac.examples`
   - `omni.isaac.manipulators` 
   - `omni.isaac.franka`
   - `omni.isaac.core`
   - `omni.isaac.ui`

### 5. Enable RoboCopilot Extension

1. In the Extensions window, search for "RoboCopilot"
2. Toggle the extension ON
3. Check the Console window for any errors

### 6. Access the Extension

1. Go to **Isaac Examples > Manipulation > RoboCopilot Stack**
2. The extension window should open
3. Click **Load** to initialize the scene
4. Start using the chat interface!

## Isaac Sim 4.5 Specific Fixes Applied

✅ **Relative Imports**: Changed from absolute to relative imports (`from .module`)  
✅ **Extension Dependencies**: Updated dependencies for Isaac Sim 4.5 compatibility  
✅ **Import Structure**: Fixed package structure to work with Isaac Sim 4.5  
✅ **Extension Registration**: Proper registration with Isaac Examples browser  

## Troubleshooting Isaac Sim 4.5 Issues

### Extension Not Appearing in Toolbar/Menu
This is a common Isaac Sim 4.5 issue. Try these steps:

1. **Check Extension Dependencies**:
   - Ensure all required Isaac extensions are enabled first
   - Look for any red error indicators in the Extensions window

2. **Restart Isaac Sim**:
   - Close Isaac Sim completely
   - Restart and re-enable the extension

3. **Check Console for Errors**:
   - Open **Window > Console**
   - Look for import errors or dependency issues
   - Common errors include missing dependencies or import path issues

4. **Verify Extension Location**:
   - Ensure the extension is in the correct `exts/` directory
   - Check that the directory name matches the module name in `extension.toml`

### Import Errors
- The extension now uses relative imports compatible with Isaac Sim 4.5
- If you see import errors, ensure all dependency extensions are enabled
- Check that the extension directory structure is correct

### Extension Loads but No UI
- Ensure `omni.isaac.examples` extension is enabled
- Check that the extension registers properly with the Examples browser
- Look for UI-related errors in the console

## Success Indicators

✅ Extension appears in Extensions window without errors  
✅ No import errors in console  
✅ "RoboCopilot Stack" appears in **Isaac Examples > Manipulation**  
✅ Chat interface loads properly  
✅ Execute Task button becomes enabled after loading scene  

## If Extension Still Not Visible

If the extension loads without errors but doesn't appear in the Isaac Examples menu:

1. **Check Extension Registration**:
   ```python
   # Look for this in the console output
   [Info] Registering example: RoboCopilot Stack in category: Manipulation
   ```

2. **Manual Access**:
   - Try accessing through **Window > Extensions**
   - Look for the extension in the "Third Party" or "Community" sections

3. **Dependency Issues**:
   - Disable and re-enable all Isaac extensions
   - Restart Isaac Sim after enabling dependencies

## Next Steps

Once installed successfully:
1. Load the scene using the **Load** button
2. Enter commands like "Stack the cubes on top of each other"
3. Click "🚀 Execute Task"
4. Watch the Franka robot perform the stacking operation!

The extension performs the same cube stacking as the original Simple Stack but with an enhanced chat-based interface optimized for Isaac Sim 4.5. 