# Integration Guide: Chatbot GUI with Your Supervisor

This guide explains how to integrate the chatbot GUI with your existing supervisor code.

## Current Mock Implementation

The GUI currently uses a `MockSupervisor` class that simulates your supervisor's behavior. Here's what you need to know:

### Mock Supervisor Interface

```python
def process_query(self, user_input: str) -> Generator[Tuple[str, str], None, None]:
    """
    Expected interface for your supervisor
    Args:
        user_input (str): The user's input message
    
    Yields:
        Tuple[str, str]: (output_thoughts, final_res)
        - output_thoughts: Intermediate thinking process (can be empty "")
        - final_res: Final response (empty "" until the last yield)
    """
```

## Integration Steps

### Step 1: Replace Mock Supervisor

Replace the `MockSupervisor` instantiation in `ChatbotGUI.__init__()`:

```python
# Current (line ~52):
self.supervisor = MockSupervisor()

# Replace with:
self.supervisor = YourActualSupervisor()  # Your supervisor instance
```

### Step 2: Ensure Your Supervisor Matches the Interface

Your supervisor's method should:

1. **Accept a string input**: The user's message
2. **Return a generator**: That yields tuples of `(output_thoughts, final_res)`
3. **Yield intermediate thoughts**: With empty `final_res` (`""`)
4. **Yield final response**: On the last iteration with the complete response

### Example Integration Pattern

```python
class YourSupervisor:
    def process_query(self, user_input: str) -> Generator[Tuple[str, str], None, None]:
        """Your existing supervisor method - adapt as needed"""
        
        # Your existing logic here...
        # As you process, yield thoughts:
        
        yield ("Analyzing the request...", "")
        yield ("Searching knowledge base...", "")
        yield ("Formulating response...", "")
        
        # Final yield with both thought and response:
        final_response = "Your final AI response here"
        yield ("Response ready!", final_response)
```

### Step 3: Modify the GUI Integration Point

The integration happens in the `process_user_input` method (line ~217):

```python
def process_user_input(self, user_input: str):
    """Process user input using the supervisor (runs in separate thread)"""
    try:
        # This calls your supervisor's process_query method
        for output_thoughts, final_res in self.supervisor.process_query(user_input):
            if output_thoughts:
                self.message_queue.put(("thought", output_thoughts))
            
            if final_res:
                self.message_queue.put(("final", final_res))
    
    except Exception as e:
        self.message_queue.put(("error", f"Error processing request: {str(e)}"))
    
    finally:
        self.message_queue.put(("enable_submit", ""))
```

## Advanced Integration Options

### Option 1: Direct Class Integration

If your supervisor is a class, simply import and instantiate it:

```python
from your_project.supervisor import YourSupervisor

class ChatbotGUI:
    def __init__(self, root):
        # ... existing init code ...
        self.supervisor = YourSupervisor()
```

### Option 2: Function-Based Integration

If your supervisor is a function, create a wrapper:

```python
from your_project.supervisor import your_supervisor_function

class SupervisorWrapper:
    def process_query(self, user_input: str):
        return your_supervisor_function(user_input)

class ChatbotGUI:
    def __init__(self, root):
        # ... existing init code ...
        self.supervisor = SupervisorWrapper()
```

### Option 3: Callback Integration

If you need more complex integration, you can modify the GUI to accept a callback:

```python
class ChatbotGUI:
    def __init__(self, root, supervisor_callback=None):
        # ... existing init code ...
        self.supervisor_callback = supervisor_callback or MockSupervisor().process_query
    
    def process_user_input(self, user_input: str):
        try:
            for output_thoughts, final_res in self.supervisor_callback(user_input):
                # ... rest of the method
```

## Running the Integrated Version

Once integrated, run your application:

```python
if __name__ == "__main__":
    root = tk.Tk()
    
    # Option 1: With your supervisor class
    app = ChatbotGUI(root)
    
    # Option 2: With callback (if using Option 3 above)
    # app = ChatbotGUI(root, supervisor_callback=your_supervisor_function)
    
    root.mainloop()
```

## Troubleshooting

### Common Issues:

1. **Import Errors**: Ensure your supervisor module is in the Python path
2. **Generator Issues**: Make sure your supervisor yields tuples, not returns them
3. **Threading Issues**: The GUI handles threading automatically, but ensure your supervisor is thread-safe
4. **Performance**: If your supervisor is slow, the GUI will show "Processing..." - this is normal

### Testing Your Integration:

1. Start with a simple supervisor that just yields test data
2. Gradually add your actual logic
3. Test the thoughts toggle functionality
4. Verify error handling works with invalid inputs

## Customization

### Modifying Thought Display Format

You can customize how thoughts are displayed by modifying the `create_message_widget` method around line 278.

### Adding Additional Message Types

Add new message types by:
1. Extending the `message_type` handling in `create_message_widget`
2. Adding new queue message types in `check_message_queue`
3. Modifying your supervisor to yield additional information

### Styling Changes

Modify the `setup_styles` method (line ~69) to change colors, fonts, and appearance.

## Next Steps

1. Test the GUI with your supervisor
2. Customize the appearance as needed
3. Add any additional features specific to your use case
4. Consider adding logging, configuration files, or other production features