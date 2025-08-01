import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
from datetime import datetime
from typing import Generator, Tuple
import queue


class MockSupervisor:
    """Mock supervisor class that simulates your actual supervisor with yield functionality"""
    
    def process_query(self, user_input: str) -> Generator[Tuple[str, str], None, None]:
        """
        Mock function that simulates your supervisor's yield behavior
        Returns: Generator yielding (output_thoughts, final_res) tuples
        """
        # Simulate thinking process with multiple thoughts
        thoughts = [
            f"Analyzing user input: '{user_input}'",
            "Searching knowledge base for relevant information...",
            "Processing contextual understanding...",
            "Formulating comprehensive response...",
            "Finalizing output and ensuring accuracy..."
        ]
        
        final_response = f"Based on your query '{user_input}', here's my response: This is a comprehensive answer that addresses your question with detailed information and helpful insights."
        
        # Simulate gradual thought process
        for i, thought in enumerate(thoughts):
            time.sleep(0.5)  # Simulate processing time
            if i == len(thoughts) - 1:
                # Last iteration - return both final thought and response
                yield (thought, final_response)
            else:
                # Intermediate thoughts
                yield (thought, "")


class ChatMessage:
    """Class to represent a chat message"""
    
    def __init__(self, sender: str, content: str, timestamp: datetime, message_type: str = "normal"):
        self.sender = sender  # "user" or "assistant"
        self.content = content
        self.timestamp = timestamp
        self.message_type = message_type  # "normal", "thought", "final"


class ChatbotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Chatbot Interface")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        # Initialize supervisor (replace this with your actual supervisor later)
        self.supervisor = MockSupervisor()
        
        # Queue for thread-safe GUI updates
        self.message_queue = queue.Queue()
        
        # State variables
        self.show_thoughts = tk.BooleanVar(value=True)
        self.is_processing = False
        self.messages = []
        
        self.setup_gui()
        self.setup_styles()
        
        # Start checking for queued messages
        self.check_message_queue()
    
    def setup_styles(self):
        """Setup custom styles for the interface"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), background="#f0f0f0")
        style.configure('Timestamp.TLabel', font=('Arial', 8), foreground="#666666")
        style.configure('User.TLabel', font=('Arial', 10, 'bold'), foreground="#0066cc")
        style.configure('Assistant.TLabel', font=('Arial', 10, 'bold'), foreground="#cc6600")
        style.configure('Thought.TLabel', font=('Arial', 9, 'italic'), foreground="#666666")
    
    def setup_gui(self):
        """Setup the main GUI layout"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="AI Chatbot Interface", style='Title.TLabel')
        title_label.grid(row=0, column=0, pady=(0, 10), sticky=tk.W)
        
        # Thoughts toggle
        thoughts_frame = ttk.Frame(main_frame)
        thoughts_frame.grid(row=0, column=0, sticky=tk.E, pady=(0, 10))
        
        ttk.Label(thoughts_frame, text="Show Thoughts:").pack(side=tk.LEFT, padx=(0, 5))
        thoughts_checkbox = ttk.Checkbutton(
            thoughts_frame, 
            variable=self.show_thoughts,
            command=self.toggle_thoughts_display
        )
        thoughts_checkbox.pack(side=tk.LEFT)
        
        # Chat history area
        self.setup_chat_area(main_frame)
        
        # Input area
        self.setup_input_area(main_frame)
    
    def setup_chat_area(self, parent):
        """Setup the scrollable chat history area"""
        # Create frame for chat area
        chat_frame = ttk.Frame(parent)
        chat_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(0, weight=1)
        
        # Create canvas and scrollbar for custom scrolling
        canvas = tk.Canvas(chat_frame, bg="white", highlightthickness=1, highlightbackground="#cccccc")
        scrollbar = ttk.Scrollbar(chat_frame, orient="vertical", command=canvas.yview)
        self.chat_content_frame = ttk.Frame(canvas)
        
        # Configure scrolling
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.create_window((0, 0), window=self.chat_content_frame, anchor="nw")
        
        # Grid layout
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind events
        self.chat_content_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas.find_all()[0], width=canvas.winfo_width()))
        
        # Enable mouse wheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        self.canvas = canvas
        self.chat_content_frame.columnconfigure(0, weight=1)
    
    def setup_input_area(self, parent):
        """Setup the user input area"""
        input_frame = ttk.Frame(parent)
        input_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        input_frame.columnconfigure(0, weight=1)
        
        # Input text area
        self.input_text = tk.Text(
            input_frame, 
            height=3, 
            wrap=tk.WORD,
            font=('Arial', 10),
            relief=tk.SOLID,
            borderwidth=1
        )
        self.input_text.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Submit button
        self.submit_button = ttk.Button(
            input_frame, 
            text="Submit",
            command=self.submit_message
        )
        self.submit_button.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind Enter key
        self.input_text.bind("<Control-Return>", lambda e: self.submit_message())
        
        # Add placeholder text
        self.input_text.insert("1.0", "Type your message here... (Ctrl+Enter to submit)")
        self.input_text.bind("<FocusIn>", self.clear_placeholder)
        self.input_text.bind("<FocusOut>", self.add_placeholder)
        self.input_text.config(foreground="#888888")
    
    def clear_placeholder(self, event):
        """Clear placeholder text when input is focused"""
        if self.input_text.get("1.0", tk.END).strip() == "Type your message here... (Ctrl+Enter to submit)":
            self.input_text.delete("1.0", tk.END)
            self.input_text.config(foreground="black")
    
    def add_placeholder(self, event):
        """Add placeholder text when input loses focus and is empty"""
        if not self.input_text.get("1.0", tk.END).strip():
            self.input_text.insert("1.0", "Type your message here... (Ctrl+Enter to submit)")
            self.input_text.config(foreground="#888888")
    
    def submit_message(self):
        """Handle message submission"""
        if self.is_processing:
            return
        
        user_input = self.input_text.get("1.0", tk.END).strip()
        
        # Check if input is empty or placeholder
        if not user_input or user_input == "Type your message here... (Ctrl+Enter to submit)":
            return
        
        # Clear input
        self.input_text.delete("1.0", tk.END)
        self.add_placeholder(None)
        
        # Add user message
        self.add_message("user", user_input, "normal")
        
        # Disable submit button during processing
        self.is_processing = True
        self.submit_button.config(state="disabled", text="Processing...")
        
        # Start processing in separate thread
        thread = threading.Thread(target=self.process_user_input, args=(user_input,))
        thread.daemon = True
        thread.start()
    
    def process_user_input(self, user_input: str):
        """Process user input using the supervisor (runs in separate thread)"""
        try:
            # This is where you'll integrate with your actual supervisor
            # For now, using the mock supervisor
            for output_thoughts, final_res in self.supervisor.process_query(user_input):
                if output_thoughts:
                    # Queue thought message
                    self.message_queue.put(("thought", output_thoughts))
                
                if final_res:
                    # Queue final response
                    self.message_queue.put(("final", final_res))
        
        except Exception as e:
            # Queue error message
            self.message_queue.put(("error", f"Error processing request: {str(e)}"))
        
        finally:
            # Re-enable submit button
            self.message_queue.put(("enable_submit", ""))
    
    def check_message_queue(self):
        """Check for messages from the processing thread and update GUI"""
        try:
            while True:
                message_type, content = self.message_queue.get_nowait()
                
                if message_type == "thought":
                    self.add_message("assistant", content, "thought")
                elif message_type == "final":
                    self.add_message("assistant", content, "final")
                elif message_type == "error":
                    self.add_message("system", content, "error")
                elif message_type == "enable_submit":
                    self.is_processing = False
                    self.submit_button.config(state="normal", text="Submit")
        
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.check_message_queue)
    
    def add_message(self, sender: str, content: str, message_type: str):
        """Add a message to the chat history"""
        timestamp = datetime.now()
        message = ChatMessage(sender, content, timestamp, message_type)
        self.messages.append(message)
        
        # Create message widget
        self.create_message_widget(message)
        
        # Scroll to bottom
        self.root.after_idle(self.scroll_to_bottom)
    
    def create_message_widget(self, message: ChatMessage):
        """Create a widget for displaying a message"""
        # Don't show thoughts if toggle is off
        if message.message_type == "thought" and not self.show_thoughts.get():
            return
        
        # Create message frame
        msg_frame = ttk.Frame(self.chat_content_frame)
        msg_frame.grid(sticky=(tk.W, tk.E), padx=10, pady=5)
        msg_frame.columnconfigure(1, weight=1)
        
        # Configure row in parent
        row = len([child for child in self.chat_content_frame.winfo_children()])
        self.chat_content_frame.rowconfigure(row, weight=0)
        
        # Sender and timestamp
        if message.sender == "user":
            sender_text = "You"
            sender_style = "User.TLabel"
            bg_color = "#e6f3ff"
        elif message.message_type == "thought":
            sender_text = "AI (thinking)"
            sender_style = "Thought.TLabel"
            bg_color = "#f9f9f9"
        elif message.message_type == "error":
            sender_text = "System"
            sender_style = "Assistant.TLabel"
            bg_color = "#ffe6e6"
        else:
            sender_text = "AI Assistant"
            sender_style = "Assistant.TLabel"
            bg_color = "#f0f8e6"
        
        # Create colored background frame
        content_frame = tk.Frame(msg_frame, bg=bg_color, relief=tk.SOLID, borderwidth=1)
        content_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        content_frame.columnconfigure(0, weight=1)
        
        # Sender label
        sender_label = tk.Label(
            content_frame,
            text=sender_text,
            font=('Arial', 10, 'bold'),
            bg=bg_color,
            fg="#0066cc" if message.sender == "user" else "#cc6600" if message.message_type != "thought" else "#666666"
        )
        sender_label.grid(row=0, column=0, sticky=tk.W, padx=10, pady=(5, 0))
        
        # Timestamp
        timestamp_str = message.timestamp.strftime("%H:%M:%S")
        timestamp_label = tk.Label(
            content_frame,
            text=timestamp_str,
            font=('Arial', 8),
            bg=bg_color,
            fg="#666666"
        )
        timestamp_label.grid(row=0, column=1, sticky=tk.E, padx=10, pady=(5, 0))
        
        # Message content
        content_label = tk.Label(
            content_frame,
            text=message.content,
            font=('Arial', 10, 'italic' if message.message_type == "thought" else 'normal'),
            bg=bg_color,
            wraplength=600,
            justify=tk.LEFT,
            anchor="w"
        )
        content_label.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=(0, 10))
    
    def toggle_thoughts_display(self):
        """Toggle the display of thought messages"""
        # Clear and recreate all message widgets
        for widget in self.chat_content_frame.winfo_children():
            widget.destroy()
        
        # Recreate all messages
        for message in self.messages:
            self.create_message_widget(message)
        
        # Scroll to bottom
        self.root.after_idle(self.scroll_to_bottom)
    
    def scroll_to_bottom(self):
        """Scroll the chat area to the bottom"""
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def get_user_input_handler(self):
        """
        Returns a function that your supervisor can use to get user input.
        This is for future integration with your supervisor code.
        """
        def input_handler():
            # This would need to be implemented based on your supervisor's needs
            # For now, it's just a placeholder
            pass
        return input_handler


def main():
    """Main function to run the chatbot GUI"""
    root = tk.Tk()
    app = ChatbotGUI(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        root.quit()


if __name__ == "__main__":
    main()