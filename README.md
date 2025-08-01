# AI Chatbot GUI

A professional, easy-to-use GUI interface for chatbot applications built with Python's tkinter. This GUI is designed to work with AI supervisors/LLMs that yield both thought processes and final responses.

## Features

- **Modern Chat Interface**: Clean, professional design similar to ChatGPT
- **Real-time Thought Display**: Toggle to show/hide AI thinking processes
- **Message History**: Scrollable chat history with timestamps
- **Thread-Safe**: Non-blocking GUI that handles long-running AI processes
- **Easy Integration**: Simple interface for connecting to your existing AI supervisor
- **Professional Styling**: Color-coded messages, proper spacing, and modern UI elements

## Screenshot

```
┌─────────────────────────────────────────────────────────┐
│ AI Chatbot Interface                    Show Thoughts: ☑ │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ ┌─ You ──────────────────────────────── 14:30:25 ─────┐ │
│ │ What is machine learning?                           │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ ┌─ AI (thinking) ──────────────────────── 14:30:26 ──┐ │
│ │ Analyzing user input: 'What is machine learning?'  │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ ┌─ AI Assistant ──────────────────────── 14:30:28 ────┐ │
│ │ Machine learning is a subset of artificial         │ │
│ │ intelligence that enables computers to learn...     │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
├─────────────────────────────────────────────────────────┤
│ Type your message here...               │    Submit     │
│                                         │               │
└─────────────────────────────────────────────────────────┘
```

## Requirements

- Python 3.6 or higher
- No external dependencies (uses only Python standard library)

## Quick Start

1. **Run the GUI**:
   ```bash
   python chatbot_gui.py
   ```

2. **Test the Interface**:
   - Type a message in the input box
   - Click "Submit" or press Ctrl+Enter
   - Watch the AI thinking process (if thoughts toggle is on)
   - See the final response

## Integration with Your Supervisor

### Step 1: Understand the Interface

Your supervisor should implement a method with this signature:

```python
def process_query(self, user_input: str) -> Generator[Tuple[str, str], None, None]:
    """
    Process user input and yield thoughts + final response
    
    Args:
        user_input: The user's message as a string
    
    Yields:
        Tuple[str, str]: (thought_text, final_response)
        - thought_text: Current thinking step (can be empty "")
        - final_response: Final answer (empty "" until last yield)
    """
```

### Step 2: Replace the Mock Supervisor

In `chatbot_gui.py`, find line ~52 and replace:

```python
# Replace this:
self.supervisor = MockSupervisor()

# With this:
from your_project import YourSupervisor
self.supervisor = YourSupervisor()
```

### Step 3: Test Your Integration

Run the GUI and test with your actual supervisor logic.

For detailed integration instructions, see [`integration_guide.md`](integration_guide.md).

## Usage

### Basic Controls

- **Input Box**: Type your message here
- **Submit Button**: Send your message (or use Ctrl+Enter)
- **Thoughts Toggle**: Show/hide AI thinking processes
- **Scroll**: Use mouse wheel or scrollbar to navigate chat history

### Message Types

- **User Messages** (Blue): Your input messages
- **AI Thoughts** (Gray, Italic): Intermediate thinking steps
- **AI Responses** (Green): Final answers from the AI
- **System Messages** (Red): Error messages or system notifications

### Keyboard Shortcuts

- `Ctrl+Enter`: Submit message
- `Mouse Wheel`: Scroll through chat history

## Customization

### Styling

Modify the `setup_styles()` method to change:
- Colors and fonts
- Message appearance
- Window styling

### Layout

Adjust the `setup_gui()` method to:
- Change window size and layout
- Modify component positioning
- Add new UI elements

### Behavior

Customize the message handling in:
- `create_message_widget()`: Message display format
- `process_user_input()`: Integration logic
- `check_message_queue()`: Message processing

## File Structure

```
├── chatbot_gui.py          # Main GUI application
├── integration_guide.md    # Detailed integration instructions
├── requirements.txt        # Dependencies (all built-in)
└── README.md              # This file
```

## Classes Overview

### `ChatbotGUI`
Main GUI class that handles:
- User interface setup and styling
- Message display and management
- Threading for non-blocking AI processing
- Integration with supervisor classes

### `MockSupervisor`
Example supervisor implementation showing:
- Expected method signature
- Yield pattern for thoughts and responses
- Simulated processing time

### `ChatMessage`
Data class for storing:
- Message content and metadata
- Sender information (user/AI/system)
- Timestamps and message types

## Technical Details

### Threading
- GUI runs on main thread
- AI processing runs on background threads
- Thread-safe communication via `queue.Queue`
- Non-blocking interface during AI processing

### Message Queue System
- Thoughts and responses queued as they're generated
- GUI polls queue every 100ms for updates
- Automatic scrolling to latest messages
- Error handling and user feedback

### Memory Management
- Messages stored in memory during session
- Automatic cleanup on application exit
- Efficient widget creation and destruction

## Troubleshooting

### Common Issues

1. **GUI Freezes**: Check if your supervisor is blocking the thread
2. **No Thoughts Displayed**: Verify the thoughts toggle is enabled
3. **Import Errors**: Ensure your supervisor module is in the Python path
4. **Threading Issues**: Make sure your supervisor is thread-safe

### Debug Mode

Add debugging by modifying the error handling in `process_user_input()`:

```python
except Exception as e:
    import traceback
    error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
    self.message_queue.put(("error", error_msg))
```

## Contributing

This is a standalone GUI tool designed for easy integration. Feel free to:
- Customize the styling and layout
- Add new features as needed
- Extend the message types and handling
- Improve the integration interface

## License

This project uses only Python standard library components and can be freely used and modified for your needs.

## Next Steps

1. **Integration**: Follow the integration guide to connect your supervisor
2. **Customization**: Modify styling and behavior to match your needs
3. **Features**: Add any additional functionality your project requires
4. **Production**: Consider adding logging, configuration, and error reporting

For detailed integration instructions, see [`integration_guide.md`](integration_guide.md).
