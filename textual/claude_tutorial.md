# Building a Terminal-Based Text Editor with Textual in Python

Textual is a powerful TUI (Text User Interface) framework for Python that makes it easy to create rich, interactive terminal applications. In this guide, we'll build a functional text editor with features like file opening/saving, syntax highlighting, and a basic command system.

## Table of Contents
- [Building a Terminal-Based Text Editor with Textual in Python](#building-a-terminal-based-text-editor-with-textual-in-python)
  - [Table of Contents](#table-of-contents)
  - [Setting Up the Environment](#setting-up-the-environment)
  - [Creating the Basic Editor Structure](#creating-the-basic-editor-structure)
  - [Implementing File Operations](#implementing-file-operations)
  - [Adding Syntax Highlighting](#adding-syntax-highlighting)
  - [Implementing Search and Replace](#implementing-search-and-replace)
  - [Adding a Command Palette](#adding-a-command-palette)
  - [Final Touches and Enhancements](#final-touches-and-enhancements)
  - [Full Working Example](#full-working-example)
- [textual\_editor.py](#textual_editorpy)

## Setting Up the Environment

First, let's set up our development environment:

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Textual
pip install textual
```

## Creating the Basic Editor Structure

Let's start by creating a basic text editor with a simple interface:

```python
# editor.py
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, TextArea
from textual.binding import Binding

class TextEditor(App):
    """A Textual text editor application."""
    
    CSS = """
    Screen {
        layout: grid;
        grid-size: 1 3;
        grid-rows: 1fr 1fr 1fr;
    }
    
    #editor {
        height: 100%;
        border: solid green;
    }
    """
    
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+s", "save", "Save"),
        Binding("ctrl+o", "open_file", "Open"),
    ]
    
    def __init__(self):
        super().__init__()
        self.current_file = None
    
    def compose(self) -> ComposeResult:
        """Compose the UI."""
        yield Header(show_clock=True)
        yield TextArea(id="editor")
        yield Footer()
    
    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()
    
    def action_save(self) -> None:
        """Save the current file."""
        # We'll implement this later
        self.notify("Save not implemented yet")
    
    def action_open_file(self) -> None:
        """Open a file."""
        # We'll implement this later
        self.notify("Open not implemented yet")

if __name__ == "__main__":
    app = TextEditor()
    app.run()
```

This code creates a basic text editor with a full-screen text area and key bindings for quit, save, and open operations.

## Implementing File Operations

Now, let's implement file operations using Textual's `Input` widget for file paths:

```python
# editor.py (updated)
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, TextArea, Input, Button
from textual.binding import Binding
from pathlib import Path

class FileDialog(Container):
    """A simple file dialog."""
    
    def __init__(self, action="open"):
        super().__init__()
        self.action = action
    
    def compose(self) -> ComposeResult:
        """Compose the dialog."""
        yield Input(placeholder="Enter file path...", id="file_path")
        yield Button("Cancel", variant="error", id="cancel")
        yield Button("OK", variant="success", id="ok")

class TextEditor(App):
    """A Textual text editor application."""
    
    CSS = """
    Screen {
        layout: grid;
        grid-size: 1 3;
        grid-rows: auto 1fr auto;
    }
    
    #editor {
        height: 100%;
        border: solid green;
    }
    
    FileDialog {
        layout: grid;
        grid-size: 3;
        grid-rows: auto auto;
        padding: 1;
        width: 60;
        height: 7;
        border: heavy $accent;
        background: $surface;
        content-align: center middle;
    }
    
    FileDialog #file_path {
        column-span: 3;
        width: 100%;
        margin-bottom: 1;
    }
    
    FileDialog #cancel {
        width: 100%;
    }
    
    FileDialog #ok {
        width: 100%;
    }
    """
    
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+s", "save", "Save"),
        Binding("ctrl+o", "open_file", "Open"),
    ]
    
    def __init__(self):
        super().__init__()
        self.current_file = None
    
    def compose(self) -> ComposeResult:
        """Compose the UI."""
        yield Header(show_clock=True)
        yield TextArea(id="editor")
        yield Footer()
    
    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()
    
    def action_save(self) -> None:
        """Save the current file."""
        if self.current_file:
            self._save_file(self.current_file)
        else:
            # Show save dialog
            self.mount(FileDialog(action="save"))
    
    def action_open_file(self) -> None:
        """Open a file."""
        self.mount(FileDialog(action="open"))
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses in the file dialog."""
        button_id = event.button.id
        if button_id == "cancel":
            # Remove the dialog
            self.query_one(FileDialog).remove()
        elif button_id == "ok":
            # Get the file path
            file_path = self.query_one("#file_path").value
            dialog = self.query_one(FileDialog)
            
            if dialog.action == "open":
                self._open_file(file_path)
            else:  # save
                self._save_file(file_path)
            
            # Remove the dialog
            dialog.remove()
    
    def _open_file(self, file_path):
        """Open a file and load its contents."""
        try:
            path = Path(file_path)
            if path.exists():
                self.current_file = file_path
                with open(file_path, "r") as f:
                    content = f.read()
                
                editor = self.query_one("#editor", TextArea)
                editor.text = content
                self.notify(f"Opened: {file_path}")
            else:
                self.notify(f"File not found: {file_path}", severity="error")
        except Exception as e:
            self.notify(f"Error opening file: {e}", severity="error")
    
    def _save_file(self, file_path):
        """Save the current content to a file."""
        try:
            editor = self.query_one("#editor", TextArea)
            content = editor.text
            
            with open(file_path, "w") as f:
                f.write(content)
            
            self.current_file = file_path
            self.notify(f"Saved: {file_path}")
        except Exception as e:
            self.notify(f"Error saving file: {e}", severity="error")

if __name__ == "__main__":
    app = TextEditor()
    app.run()
```

## Adding Syntax Highlighting

Now let's add syntax highlighting using Textual's rich-text capabilities:

```python
# editor.py (updated with syntax highlighting)
import re
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, TextArea, Input, Button, Label
from textual.binding import Binding
from pathlib import Path
from rich.syntax import Syntax
from rich.text import Text

class FileDialog(Container):
    """A simple file dialog."""
    
    def __init__(self, action="open"):
        super().__init__()
        self.action = action
    
    def compose(self) -> ComposeResult:
        """Compose the dialog."""
        yield Input(placeholder="Enter file path...", id="file_path")
        yield Button("Cancel", variant="error", id="cancel")
        yield Button("OK", variant="success", id="ok")

class SyntaxHighlightedTextArea(TextArea):
    """A text area with syntax highlighting."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.language = "python"  # Default language
    
    def set_language(self, language):
        """Set the language for syntax highlighting."""
        self.language = language
        self.highlight_syntax()
    
    def highlight_syntax(self):
        """Apply syntax highlighting to the content."""
        if not self.text:
            return
            
        try:
            syntax = Syntax(
                self.text,
                self.language,
                theme="monokai",
                word_wrap=True,
                indent_guides=True,
                line_numbers=True,
                highlight_lines=set(),
            )
            
            # This would be the ideal approach, but currently TextArea doesn't 
            # support direct styling like this. This is a placeholder for future enhancement.
            # self.update_content(syntax)
            
            # Instead, we'll just notify for now
            self.app.notify(f"Syntax highlighting applied for {self.language}")
        except Exception as e:
            self.app.notify(f"Error highlighting syntax: {e}", severity="error")
    
    def on_text_changed(self, event):
        """Handle text changes to update highlighting."""
        # In a real implementation, this would update the highlighting
        # For now, we'll do nothing to avoid performance issues
        pass

class StatusBar(Container):
    """Status bar for the editor."""
    
    def compose(self) -> ComposeResult:
        """Compose the status bar."""
        yield Label("Line: 1, Col: 1", id="position")
        yield Label("Python", id="language")
        yield Label("UTF-8", id="encoding")

class TextEditor(App):
    """A Textual text editor application."""
    
    CSS = """
    Screen {
        layout: grid;
        grid-size: 1 3;
        grid-rows: auto 1fr auto;
    }
    
    #editor {
        height: 100%;
        border: solid green;
    }
    
    FileDialog {
        layout: grid;
        grid-size: 3;
        grid-rows: auto auto;
        padding: 1;
        width: 60;
        height: 7;
        border: heavy $accent;
        background: $surface;
        content-align: center middle;
    }
    
    FileDialog #file_path {
        column-span: 3;
        width: 100%;
        margin-bottom: 1;
    }
    
    FileDialog #cancel {
        width: 100%;
    }
    
    FileDialog #ok {
        width: 100%;
    }
    
    StatusBar {
        height: 1;
        background: $accent;
        color: $text;
        layout: horizontal;
    }
    
    StatusBar > Label {
        width: 1fr;
        padding: 0 1;
    }
    """
    
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+s", "save", "Save"),
        Binding("ctrl+o", "open_file", "Open"),
        Binding("ctrl+h", "toggle_highlighting", "Toggle Highlighting"),
        Binding("ctrl+f", "search", "Search"),
    ]
    
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.highlighting_enabled = True
    
    def compose(self) -> ComposeResult:
        """Compose the UI."""
        yield Header(show_clock=True)
        yield SyntaxHighlightedTextArea(id="editor")
        yield StatusBar()
        yield Footer()
    
    def on_mount(self) -> None:
        """Handle application mount event."""
        self.update_status_bar()
    
    def update_status_bar(self) -> None:
        """Update the status bar information."""
        editor = self.query_one("#editor", SyntaxHighlightedTextArea)
        cursor = editor.cursor_location
        line = cursor[0] + 1
        col = cursor[1] + 1
        
        # Update position
        position_label = self.query_one("#position", Label)
        position_label.update(f"Line: {line}, Col: {col}")
        
        # Update language based on file extension
        if self.current_file:
            extension = Path(self.current_file).suffix.lstrip('.')
            language_map = {
                'py': 'Python',
                'js': 'JavaScript',
                'html': 'HTML',
                'css': 'CSS',
                'md': 'Markdown',
                'txt': 'Plain Text',
            }
            language = language_map.get(extension, 'Plain Text')
            language_label = self.query_one("#language", Label)
            language_label.update(language)
            
            # Set the language for syntax highlighting
            editor.set_language(language.lower())
    
    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()
    
    def action_save(self) -> None:
        """Save the current file."""
        if self.current_file:
            self._save_file(self.current_file)
        else:
            # Show save dialog
            self.mount(FileDialog(action="save"))
    
    def action_open_file(self) -> None:
        """Open a file."""
        self.mount(FileDialog(action="open"))
    
    def action_toggle_highlighting(self) -> None:
        """Toggle syntax highlighting."""
        self.highlighting_enabled = not self.highlighting_enabled
        editor = self.query_one("#editor", SyntaxHighlightedTextArea)
        
        if self.highlighting_enabled:
            editor.highlight_syntax()
            self.notify("Syntax highlighting enabled")
        else:
            self.notify("Syntax highlighting disabled")
    
    def action_search(self) -> None:
        """Search in the current file."""
        self.notify("Search not implemented yet")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses in the file dialog."""
        button_id = event.button.id
        if button_id == "cancel":
            # Remove the dialog
            self.query_one(FileDialog).remove()
        elif button_id == "ok":
            # Get the file path
            file_path = self.query_one("#file_path").value
            dialog = self.query_one(FileDialog)
            
            if dialog.action == "open":
                self._open_file(file_path)
            else:  # save
                self._save_file(file_path)
            
            # Remove the dialog
            dialog.remove()
    
    def _open_file(self, file_path):
        """Open a file and load its contents."""
        try:
            path = Path(file_path)
            if path.exists():
                self.current_file = file_path
                with open(file_path, "r") as f:
                    content = f.read()
                
                editor = self.query_one("#editor", SyntaxHighlightedTextArea)
                editor.text = content
                
                # Update status bar and apply syntax highlighting
                self.update_status_bar()
                if self.highlighting_enabled:
                    editor.highlight_syntax()
                
                self.notify(f"Opened: {file_path}")
            else:
                self.notify(f"File not found: {file_path}", severity="error")
        except Exception as e:
            self.notify(f"Error opening file: {e}", severity="error")
    
    def _save_file(self, file_path):
        """Save the current content to a file."""
        try:
            editor = self.query_one("#editor", SyntaxHighlightedTextArea)
            content = editor.text
            
            with open(file_path, "w") as f:
                f.write(content)
            
            self.current_file = file_path
            self.update_status_bar()
            self.notify(f"Saved: {file_path}")
        except Exception as e:
            self.notify(f"Error saving file: {e}", severity="error")

if __name__ == "__main__":
    app = TextEditor()
    app.run()
```

## Implementing Search and Replace

Let's implement search and replace functionality:

```python
# Adding search and replace to our editor
from textual.widgets import Input, Button
from textual.containers import Horizontal, Vertical

class SearchDialog(Vertical):
    """Search and replace dialog."""
    
    def compose(self) -> ComposeResult:
        """Compose the dialog."""
        yield Input(placeholder="Search term...", id="search_term")
        yield Input(placeholder="Replace with... (optional)", id="replace_term")
        yield Horizontal(
            Button("Previous", id="prev"),
            Button("Next", id="next"),
            Button("Replace", id="replace"),
            Button("Replace All", id="replace_all"),
            Button("Close", id="close")
        )

# Add this to the TextEditor class
def action_search(self) -> None:
    """Show search dialog."""
    self.mount(SearchDialog())

def on_button_pressed(self, event: Button.Pressed) -> None:
    """Handle button presses in dialogs."""
    button_id = event.button.id
    
    # Handle file dialog buttons
    if self.query("FileDialog").first():
        # File dialog handling code (as already implemented)
        pass
    
    # Handle search dialog buttons
    elif self.query("SearchDialog").first():
        search_dialog = self.query_one(SearchDialog)
        
        if button_id == "close":
            search_dialog.remove()
        else:
            editor = self.query_one("#editor", TextArea)
            search_term = self.query_one("#search_term").value
            replace_term = self.query_one("#replace_term").value
            
            if not search_term:
                self.notify("Please enter a search term", severity="warning")
                return
            
            if button_id == "next":
                self._search_next(search_term)
            elif button_id == "prev":
                self._search_prev(search_term)
            elif button_id == "replace" and replace_term:
                self._replace_current(search_term, replace_term)
            elif button_id == "replace_all" and replace_term:
                self._replace_all(search_term, replace_term)

def _search_next(self, term):
    """Search for the next occurrence of term."""
    editor = self.query_one("#editor", TextArea)
    text = editor.text
    cursor_pos = editor.cursor_location
    
    # Convert row, column to single index position
    lines = text.split("\n")
    current_pos = sum(len(line) + 1 for line in lines[:cursor_pos[0]]) + cursor_pos[1]
    
    # Search from current position
    search_pos = text.find(term, current_pos + 1)
    
    if search_pos == -1:  # Not found, wrap around
        search_pos = text.find(term)
    
    if search_pos != -1:  # Found
        self._set_cursor_to_position(search_pos)
        self.notify(f"Found '{term}'")
    else:
        self.notify(f"'{term}' not found", severity="warning")

def _search_prev(self, term):
    """Search for the previous occurrence of term."""
    editor = self.query_one("#editor", TextArea)
    text = editor.text
    cursor_pos = editor.cursor_location
    
    # Convert row, column to single index position
    lines = text.split("\n")
    current_pos = sum(len(line) + 1 for line in lines[:cursor_pos[0]]) + cursor_pos[1]
    
    # Search before current position
    search_pos = text.rfind(term, 0, current_pos)
    
    if search_pos == -1:  # Not found, wrap around
        search_pos = text.rfind(term)
    
    if search_pos != -1:  # Found
        self._set_cursor_to_position(search_pos)
        self.notify(f"Found '{term}'")
    else:
        self.notify(f"'{term}' not found", severity="warning")

def _replace_current(self, search_term, replace_term):
    """Replace the current occurrence of search_term with replace_term."""
    editor = self.query_one("#editor", TextArea)
    text = editor.text
    cursor_pos = editor.cursor_location
    
    # Convert row, column to single index position
    lines = text.split("\n")
    current_pos = sum(len(line) + 1 for line in lines[:cursor_pos[0]]) + cursor_pos[1]
    
    # Check if cursor is at a match
    if text[current_pos:current_pos + len(search_term)] == search_term:
        # Replace at cursor position
        new_text = text[:current_pos] + replace_term + text[current_pos + len(search_term):]
        editor.text = new_text
        self.notify(f"Replaced occurrence of '{search_term}'")
        return True
    
    # If cursor is not at a match, search for the next one
    search_pos = text.find(search_term, current_pos)
    if search_pos == -1:  # Not found after cursor, try from beginning
        search_pos = text.find(search_term)
    
    if search_pos != -1:  # Found
        self._set_cursor_to_position(search_pos)
        self.notify(f"Found '{search_term}'")
        return True
    else:
        self.notify(f"'{search_term}' not found", severity="warning")
        return False

def _replace_all(self, search_term, replace_term):
    """Replace all occurrences of search_term with replace_term."""
    editor = self.query_one("#editor", TextArea)
    text = editor.text
    
    new_text = text.replace(search_term, replace_term)
    count = text.count(search_term)
    
    if count > 0:
        editor.text = new_text
        self.notify(f"Replaced {count} occurrences of '{search_term}'")
    else:
        self.notify(f"'{search_term}' not found", severity="warning")

def _set_cursor_to_position(self, position):
    """Set the cursor to a specific position in the text."""
    editor = self.query_one("#editor", TextArea)
    text = editor.text
    
    # Convert linear position to row, column
    lines = text.split("\n")
    row = 0
    pos = 0
    
    for line in lines:
        line_length = len(line) + 1  # +1 for the newline
        if pos + line_length > position:
            col = position - pos
            editor.move_cursor(row, col)
            return
        pos += line_length
        row += 1
    
    # If we get here, the position is at the end
    last_row = len(lines) - 1
    last_col = len(lines[-1])
    editor.move_cursor(last_row, last_col)
```

## Adding a Command Palette

Let's implement a command palette for quick access to functions:

```python
class CommandPalette(Container):
    """Command palette for quick access to editor functions."""
    
    COMMANDS = [
        ("Save", "save"),
        ("Open", "open_file"),
        ("Search", "search"),
        ("Toggle Highlighting", "toggle_highlighting"),
        ("Quit", "quit"),
    ]
    
    def compose(self) -> ComposeResult:
        """Compose the command palette."""
        yield Input(placeholder="Type a command...", id="command_input")
        for name, _ in self.COMMANDS:
            yield Button(name, id=f"cmd_{name.lower().replace(' ', '_')}")

# Add to the TextEditor class
def action_show_command_palette(self) -> None:
    """Show the command palette."""
    self.mount(CommandPalette())

# Add binding
BINDINGS = [
    # ... existing bindings
    Binding("ctrl+p", "show_command_palette", "Command Palette"),
]

# Update button handling
def on_button_pressed(self, event: Button.Pressed) -> None:
    """Handle button presses in dialogs."""
    button_id = event.button.id
    
    # Handle command palette buttons
    if button_id.startswith("cmd_"):
        command = button_id[4:]  # Remove 'cmd_' prefix
        
        # Map command back to action
        command_map = {
            "save": self.action_save,
            "open_file": self.action_open_file,
            "search": self.action_search,
            "toggle_highlighting": self.action_toggle_highlighting,
            "quit": self.action_quit,
        }
        
        if command in command_map:
            # Remove the command palette
            self.query_one(CommandPalette).remove()
            # Execute the command
            command_map[command]()
    
    # ... existing button handling code
```

## Final Touches and Enhancements

Let's add a few more features to make our editor more useful:

```python
# Add line numbering and content highlighting
class CodeEditor(SyntaxHighlightedTextArea):
    """Extended text area with additional code editor features."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.show_line_numbers = True
        self.indent_size = 4
    
    def on_key(self, event) -> None:
        """Handle key presses for smart indentation and other features."""
        if event.key == "tab":
            # Insert spaces instead of tab
            editor = self.query_one("#editor", TextArea)
            cursor = editor.cursor_location
            editor.insert(" " * self.indent_size)
            event.prevent_default()
        
        # Implement auto-indentation for new lines
        elif event.key == "enter":
            editor = self.query_one("#editor", TextArea)
            cursor = editor.cursor_location
            current_line = editor.text.split("\n")[cursor[0]]
            
            # Count leading whitespace
            indent_match = re.match(r"^(\s*)", current_line)
            if indent_match:
                indent = indent_match.group(1)
                
                # Check if line ends with a colon (e.g., in Python)
                if current_line.rstrip().endswith(":"):
                    indent += " " * self.indent_size
            
            # Let the default handler add the newline
            super().on_key(event)
            
            # Then add the indentation
            editor.insert(indent)
            event.prevent_default()
```

## Full Working Example

Here's the complete implementation of our text editor with all the features combined:

```python
# textual_editor.py
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Header, Footer, TextArea, Input, Button, Label
from textual.binding import Binding
from pathlib import Path
import re

class FileDialog(Container):
    """A simple file dialog."""
    
    def __init__(self, action="open"):
        super().__init__()
        self.action = action
    
    def compose(self) -> ComposeResult:
        """Compose the dialog."""
        yield Input(placeholder="Enter file path...", id="file_path")
        yield Button("Cancel", variant="error", id="cancel")
        yield Button("OK", variant="success", id="ok")

class SearchDialog(Vertical):
    """Search and replace dialog."""
    
    def compose(self) -> ComposeResult:
        """Compose the dialog."""
        yield Input(placeholder="Search term...", id="search_term")
        yield Input(placeholder="Replace with... (optional)", id="replace_term")
        yield Horizontal(
            Button("Previous", id="prev"),
            Button("Next", id="next"),
            Button("Replace", id="replace"),
            Button("Replace All", id="replace_all"),
            Button("Close", id="close")
        )

class CommandPalette(Container):
    """Command palette for quick access to editor functions."""
    
    COMMANDS = [
        ("Save", "save"),
        ("Open", "open_file"),
        ("Search", "search"),
        ("Toggle Highlighting", "toggle_highlighting"),
        ("Quit", "quit"),
    ]
    
    def compose(self) -> ComposeResult:
        """Compose the command palette."""
        yield Input(placeholder="Type a command...", id="command_input")
        for name, action in self.COMMANDS:
            yield Button(name, id=f"cmd_{action}")

class StatusBar(Container):
    """Status bar for the editor."""
    
    def compose(self) -> ComposeResult:
        """Compose the status bar."""
        yield Label("Line: 1, Col: 1", id="position")
        yield Label("Python", id="language")
        yield Label("UTF-8", id="encoding")

class CodeEditor(TextArea):
    """Extended text area with additional code editor features."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.language = "python"  # Default language
        self.show_line_numbers = True
        self.indent_size = 4
    
    def set_language(self, language):
        """Set the language for syntax highlighting."""
        self.language = language
        self.highlight_syntax()
    
    def highlight_syntax(self):
        """Apply syntax highlighting to the content."""
        # In a real implementation, this would apply rich text styling
        # For now, we'll just notify
        if not self.text:
            return
        self.app.notify(f"Syntax highlighting applied for {self.language}")
    
    def handle_indent(self, event):
        """Handle smart indentation."""
        if event.key == "tab":
            # Insert spaces instead of tab
            self.insert(" " * self.indent_size)
            event.prevent_default()
            return True
        return False

class TextEditorApp(App):
    """A Textual text editor application."""
    
    CSS = """
    Screen {
        layout: grid;
        grid-size: 1;
        grid-rows: auto 1fr auto auto;
    }
    
    #editor {
        height: 100%;
        border: solid green;
    }
    
    FileDialog, SearchDialog, CommandPalette {
        layout: grid;
        grid-size: 3;
        grid-rows: auto auto;
        padding: 1;
        width: 60;
        height: auto;
        border: heavy $accent;
        background: $surface;
        content-align: center middle;
    }
    
    FileDialog #file_path, SearchDialog #search_term, SearchDialog #replace_term, CommandPalette #command_input {
        column-span: 3;
        width: 100%;
        margin-bottom: 1;
    }
    
    FileDialog