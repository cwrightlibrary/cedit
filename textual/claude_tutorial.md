# Building a Terminal-Based Code Editor with Textual

This guide walks through the process of creating a fully-functional terminal-based code editor using Python and the Textual library. We'll implement syntax highlighting, file operations, and split-screen editing without using buttons.

## Table of Contents

1. [Setup and Requirements](#setup-and-requirements)
2. [Core Architecture](#core-architecture)
3. [Building the Editor Widget](#building-the-editor-widget)
4. [Implementing File Operations](#implementing-file-operations)
5. [Creating Split Views](#creating-split-views)
6. [Keyboard Shortcuts](#keyboard-shortcuts)
7. [Putting It All Together](#putting-it-all-together)
8. [Running the Application](#running-the-application)

## Setup and Requirements

Before we begin, ensure you have the necessary packages installed:

```bash
pip install textual rich
```

These packages provide the foundation for our application:
- **Textual**: A framework for creating rich terminal user interfaces (TUIs)
- **Rich**: A library for rich text and beautiful formatting in the terminal

## Core Architecture

Our application consists of four main components:

1. **Editor Widget**: Handles text editing, cursor movement, and syntax highlighting
2. **File Dialog**: Provides screens for opening and saving files
3. **Editor Container**: Manages editors and file operations
4. **Main Application**: Coordinates all components and handles keyboard shortcuts

Let's implement each component step by step.

## Building the Editor Widget

The `Editor` class is the foundation of our application. It needs to:
- Display text with syntax highlighting
- Handle cursor movement
- Process keyboard input
- Provide text editing capabilities

### Step 1: Create the basic Editor class

```python
from rich.syntax import Syntax
from rich.text import Text
from textual.app import App, ComposeResult
from textual.widgets import Static
from textual import events

class Editor(Static):
    """A code editor widget with syntax highlighting."""

    COMPONENT_CLASSES = {"editor", "editor--cursor"}
    DEFAULT_CSS = """
    Editor {
        background: $surface;
        color: $text;
        height: 1fr;
    }
    .editor--cursor {
        background: $accent;
        color: $text;
        text-style: reverse;
    }
    """

    def __init__(
        self,
        text: str = "",
        language: str = "python",
        tab_size: int = 4,
        path: Optional[str] = None,
        name: Optional[str] = None,
        id: Optional[str] = None,
        classes: Optional[str] = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.text_content = text
        self.language = language
        self.tab_size = tab_size
        self.cursor_row = 0
        self.cursor_col = 0
        self.path = path
        self.lines = text.splitlines() or [""]
        self.is_modified = False
        
    def compose(self) -> ComposeResult:
        yield Static(id="editor-content")
    
    def on_mount(self) -> None:
        self.update_syntax()
```

This sets up the basic structure of our editor. Now, let's add the functionality for syntax highlighting.

### Step 2: Implement syntax highlighting

```python
def update_syntax(self) -> None:
    content = self.query_one("#editor-content", Static)
    
    # Check if path exists to determine language based on file extension
    if self.path and os.path.exists(self.path):
        extension = pathlib.Path(self.path).suffix.lstrip(".")
        if extension:
            self.language = extension
    
    # Join lines back to text for syntax highlighting
    text = "\n".join(self.lines)
    
    # Apply syntax highlighting
    syntax = Syntax(
        text,
        self.language,
        theme="monokai",
        line_numbers=True,
        word_wrap=False,
        tab_size=self.tab_size,
    )
    
    # Update content
    content.update(syntax)
    
    # Update app title with modified indicator
    app = self.app
    if isinstance(app, CodeEditorApp):
        modified_indicator = "*" if self.is_modified else ""
        path_display = self.path if self.path else "Untitled"
        app.sub_title = f"{path_display}{modified_indicator}"
```

The `update_syntax()` method refreshes the editor content with syntax highlighting, detects the language based on file extension, and updates the application title to indicate when files have unsaved changes.

### Step 3: Implement text editing operations

Now, let's add methods for inserting and deleting text:

```python
def insert_text(self, text: str) -> None:
    current_line = self.lines[self.cursor_row]
    
    # Handle special case for tabs
    if text == "\t":
        text = " " * self.tab_size
    
    # Insert text at cursor position
    new_line = current_line[:self.cursor_col] + text + current_line[self.cursor_col:]
    self.lines[self.cursor_row] = new_line
    self.cursor_col += len(text)
    
    self.is_modified = True
    self.update_syntax()

def delete_character(self) -> None:
    if self.cursor_col > 0:
        # Delete character before cursor
        current_line = self.lines[self.cursor_row]
        new_line = current_line[:self.cursor_col - 1] + current_line[self.cursor_col:]
        self.lines[self.cursor_row] = new_line
        self.cursor_col -= 1
        self.is_modified = True
    elif self.cursor_row > 0:
        # If at beginning of line, join with previous line
        current_line = self.lines.pop(self.cursor_row)
        self.cursor_row -= 1
        self.cursor_col = len(self.lines[self.cursor_row])
        self.lines[self.cursor_row] += current_line
        self.is_modified = True
    
    self.update_syntax()

def handle_enter(self) -> None:
    current_line = self.lines[self.cursor_row]
    
    # Calculate indentation of current line
    indent = len(current_line) - len(current_line.lstrip())
    indentation = " " * indent
    
    # Split line at cursor position
    before_cursor = current_line[:self.cursor_col]
    after_cursor = current_line[self.cursor_col:]
    
    # Update current line and insert new line
    self.lines[self.cursor_row] = before_cursor
    self.lines.insert(self.cursor_row + 1, indentation + after_cursor)
    
    # Move cursor to new line
    self.cursor_row += 1
    self.cursor_col = len(indentation)
    
    self.is_modified = True
    self.update_syntax()
```

These methods handle:
- Inserting text, including proper tab handling
- Deleting characters with backspace
- Handling the Enter key, with automatic indentation preservation

### Step 4: Implement cursor movement

```python
def move_cursor(self, rows: int = 0, cols: int = 0) -> None:
    # Update row position
    new_row = max(0, min(len(self.lines) - 1, self.cursor_row + rows))
    
    # If row changed, adjust column to fit within new line
    if new_row != self.cursor_row:
        self.cursor_row = new_row
        self.cursor_col = min(self.cursor_col, len(self.lines[self.cursor_row]))
    
    # Update column position
    self.cursor_col = max(0, min(len(self.lines[self.cursor_row]), self.cursor_col + cols))
    
    self.update_syntax()
```

This method handles cursor movement, ensuring it stays within valid bounds of the text.

### Step 5: Handle keyboard events

Finally, we need to process keyboard events:

```python
def on_key(self, event: events.Key) -> None:
    if event.key == "escape":
        self.screen.focus_next()
        return
    
    # Handle cursor movement
    if event.key == "up":
        self.move_cursor(rows=-1)
    elif event.key == "down":
        self.move_cursor(rows=1)
    elif event.key == "left":
        self.move_cursor(cols=-1)
    elif event.key == "right":
        self.move_cursor(cols=1)
    elif event.key == "home":
        self.cursor_col = 0
        self.update_syntax()
    elif event.key == "end":
        self.cursor_col = len(self.lines[self.cursor_row])
        self.update_syntax()
    
    # Handle editing
    elif event.key == "enter":
        self.handle_enter()
    elif event.key == "backspace":
        self.delete_character()
    elif event.key == "delete":
        # Simulate delete by moving cursor right then backspace
        if self.cursor_col < len(self.lines[self.cursor_row]):
            self.move_cursor(cols=1)
            self.delete_character()
    
    # Handle character insertion
    elif len(event.key) == 1 or event.key == "tab":
        self.insert_text(event.key)
```

This method processes all keyboard events, directing them to the appropriate handlers for cursor movement, text editing, and character insertion.

## Implementing File Operations

Now let's implement file operations through a dialog system.

### Step 1: Create a File Dialog Screen

```python
class FileDialog(Screen):
    """A dialog screen for opening or saving files."""
    
    DEFAULT_CSS = """
    FileDialog {
        align: center middle;
        background: $surface;
        color: $text;
    }
    
    #dialog-container {
        width: 60%;
        height: auto;
        border: heavy $accent;
        background: $surface;
        padding: 1 2;
    }
    
    #dialog-title {
        content-align: center middle;
        width: 100%;
        padding-bottom: 1;
    }
    
    #file-path {
        width: 100%;
        margin-bottom: 1;
    }
    """
    
    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "confirm", "Confirm"),
    ]
    
    def __init__(self, title: str, default_path: str = "", action: str = "open"):
        super().__init__()
        self.title = title
        self.default_path = default_path
        self.action = action  # "open" or "save"
    
    def compose(self) -> ComposeResult:
        with Container(id="dialog-container"):
            yield Static(self.title, id="dialog-title")
            yield Input(value=self.default_path, placeholder="Enter file path...", id="file-path")
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value)
    
    def action_cancel(self) -> None:
        self.dismiss(None)
    
    def action_confirm(self) -> None:
        file_path = self.query_one("#file-path").value
        self.dismiss(file_path)
```

This creates a simple dialog screen for entering file paths, which we'll use for both opening and saving files.

### Step 2: Create an Editor Container for File Operations

```python
class EditorContainer(Container):
    """A container that holds an editor and manages file operations."""
    
    def __init__(
        self,
        text: str = "",
        language: str = "python",
        path: Optional[str] = None,
        name: Optional[str] = None,
        id: Optional[str] = None,
        classes: Optional[str] = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.text = text
        self.language = language
        self.path = path
    
    def compose(self) -> ComposeResult:
        yield Editor(self.text, self.language, path=self.path)
    
    def on_mount(self) -> None:
        self.editor = self.query_one(Editor)
    
    async def load_file(self, path: str) -> None:
        """Load file content into the editor."""
        try:
            with open(path, "r") as f:
                content = f.read()
            
            self.editor.text_content = content
            self.editor.lines = content.splitlines() or [""]
            self.editor.path = path
            self.editor.cursor_row = 0
            self.editor.cursor_col = 0
            self.editor.is_modified = False
            self.editor.update_syntax()
        except Exception as e:
            self.app.notify(f"Error loading file: {e}", severity="error")
    
    async def save_file(self, path: Optional[str] = None) -> bool:
        """Save editor content to file."""
        save_path = path or self.editor.path
        
        if not save_path:
            return False
        
        try:
            content = "\n".join(self.editor.lines)
            with open(save_path, "w") as f:
                f.write(content)
            
            self.editor.path = save_path
            self.editor.is_modified = False
            self.editor.update_syntax()
            self.app.notify(f"Saved to {save_path}")
            return True
        except Exception as e:
            self.app.notify(f"Error saving file: {e}", severity="error")
            return False
```

The `EditorContainer` class wraps an `Editor` instance and adds methods for loading and saving files.

## Creating Split Views

Now let's implement the ability to split the view and manage multiple editors.

### Step 1: Create the Main Application Class

```python
class CodeEditorApp(App):
    """A terminal-based code editor application."""
    
    CSS = """
    CodeEditorApp {
        background: $surface;
        color: $text;
    }
    
    Horizontal {
        height: 1fr;
    }
    
    EditorContainer {
        width: 1fr;
        height: 1fr;
    }
    
    .status-bar {
        dock: bottom;
        height: 1;
        background: $accent-darken-2;
        color: $text;
        padding: 0 1;
        content-align: left middle;
    }
    """
    
    TITLE = "Terminal Code Editor"
    SUB_TITLE = "Untitled"
    
    BINDINGS = [
        Binding("ctrl+n", "new_file", "New File"),
        Binding("ctrl+o", "open_file", "Open"),
        Binding("ctrl+s", "save_file", "Save"),
        Binding("ctrl+shift+s", "save_as", "Save As"),
        Binding("ctrl+v", "split_vertical", "Split Vertical"),
        Binding("ctrl+h", "split_horizontal", "Split Horizontal"),
        Binding("ctrl+w", "close_editor", "Close Editor"),
        Binding("ctrl+q", "quit", "Quit"),
        Binding("tab", "focus_next", "Next Editor"),
    ]
    
    def __init__(self, path: Optional[str] = None):
        super().__init__()
        self.initial_path = path
        self.editors: Dict[str, EditorContainer] = {}
        self.active_container_id = None
```

This sets up our main application class with keyboard bindings for all operations.

### Step 2: Implement Editor Management

```python
def compose(self) -> ComposeResult:
    """Create the UI layout."""
    yield Header()
    
    with Horizontal(id="main-container"):
        # Start with a single editor
        editor_id = "editor-0"
        container = EditorContainer(id=editor_id)
        self.editors[editor_id] = container
        self.active_container_id = editor_id
        yield container
    
    yield Static("Ready", classes="status-bar", id="status-bar")
    yield Footer()

def on_mount(self) -> None:
    """Initialize the application after UI is mounted."""
    if self.initial_path and os.path.exists(self.initial_path):
        self.load_file_to_editor(self.initial_path, self.active_container_id)

def get_active_editor(self) -> Optional[Editor]:
    """Get the currently active editor."""
    if not self.active_container_id:
        return None
        
    container = self.query_one(f"#{self.active_container_id}", EditorContainer)
    return container.query_one(Editor)

def get_active_container(self) -> Optional[EditorContainer]:
    """Get the currently active editor container."""
    if not self.active_container_id:
        return None
        
    return self.query_one(f"#{self.active_container_id}", EditorContainer)

def set_active_container(self, container_id: str) -> None:
    """Set the active editor container."""
    self.active_container_id = container_id
    
    # Update status bar with current file info
    container = self.get_active_container()
    if container:
        editor = container.query_one(Editor)
        path_display = editor.path if editor.path else "Untitled"
        status = self.query_one("#status-bar", Static)
        status.update(f"{path_display} | Line: {editor.cursor_row + 1}, Col: {editor.cursor_col + 1}")
```

These methods handle editor management, including tracking the active editor and updating the status bar.

### Step 3: Implement Split View Operations

```python
def action_split_vertical(self) -> None:
    """Split the view vertically."""
    if not self.active_container_id:
        return
        
    # Get the main container and active editor
    main_container = self.query_one("#main-container", Horizontal)
    active_container = self.get_active_container()
    
    # Create a new editor container
    new_id = self.generate_container_id()
    new_container = EditorContainer(id=new_id)
    self.editors[new_id] = new_container
    
    # Add to main container
    main_container.mount(new_container)
    
    # Focus the new editor
    self.set_active_container(new_id)

def action_split_horizontal(self) -> None:
    """Split the view horizontally."""
    if not self.active_container_id:
        return
        
    # Get the main container and active container index
    main_container = self.query_one("#main-container", Horizontal)
    active_container = self.get_active_container()
    active_index = list(self.editors.keys()).index(self.active_container_id)
    
    # Create a vertical container to replace the active container
    vertical_container = Vertical()
    
    # Move the active container into the vertical container
    active_container.remove()
    vertical_container.mount(active_container)
    
    # Create a new editor container and add to the vertical container
    new_id = self.generate_container_id()
    new_container = EditorContainer(id=new_id)
    self.editors[new_id] = new_container
    vertical_container.mount(new_container)
    
    # Add the vertical container to the main container at the original position
    main_container.mount(vertical_container)
    
    # Focus the new editor
    self.set_active_container(new_id)
```

These methods implement vertical and horizontal splitting. The vertical split places editors side by side, while the horizontal split places them one above the other.

## Keyboard Shortcuts

Now let's implement the file operation actions that will be triggered by keyboard shortcuts:

```python
async def action_new_file(self) -> None:
    """Create a new file in the current editor."""
    container_id = self.active_container_id
    if container_id:
        container = self.get_active_container()
        editor = container.query_one(Editor)
        
        # If the current editor has unsaved changes, ask to save
        if editor.is_modified:
            result = await self.push_screen(
                FileDialog("Save changes?", editor.path or "", "save"),
            )
            if result:
                await container.save_file(result)
        
        # Create new empty file in current editor
        editor.text_content = ""
        editor.lines = [""]
        editor.path = None
        editor.cursor_row = 0
        editor.cursor_col = 0
        editor.is_modified = False
        editor.update_syntax()

async def action_open_file(self) -> None:
    """Open a file dialog and load the selected file."""
    # Show file open dialog
    result = await self.push_screen(
        FileDialog("Open File", "", "open"),
    )
    
    if result and os.path.exists(result):
        container = self.get_active_container()
        if container:
            await container.load_file(result)

async def action_save_file(self) -> None:
    """Save the current file."""
    container = self.get_active_container()
    if not container:
        return
        
    editor = container.query_one(Editor)
    
    # If file has no path, prompt for save location
    if not editor.path:
        await self.action_save_as()
        return
        
    await container.save_file()

async def action_save_as(self) -> None:
    """Save the current file with a new name."""
    container = self.get_active_container()
    if not container:
        return
        
    editor = container.query_one(Editor)
    
    # Show save dialog
    result = await self.push_screen(
        FileDialog("Save As", editor.path or "", "save"),
    )
    
    if result:
        await container.save_file(result)
```

These methods implement the standard file operations:
- New File (Ctrl+N)
- Open File (Ctrl+O)
- Save File (Ctrl+S)
- Save As (Ctrl+Shift+S)

Let's also implement actions for managing editors:

```python
def action_close_editor(self) -> None:
    """Close the current editor."""
    if not self.active_container_id or len(self.editors) <= 1:
        return  # Don't close the last editor
        
    # Get the container to close
    container = self.get_active_container()
    container_id = self.active_container_id
    
    # Remove from editors dict
    del self.editors[container_id]
    
    # Find a new active editor
    new_active_id = next(iter(self.editors.keys()))
    self.set_active_container(new_active_id)
    
    # Remove the container from the UI
    container.remove()

def action_focus_next(self) -> None:
    """Focus the next editor."""
    if not self.active_container_id or len(self.editors) <= 1:
        return
        
    # Get the list of editor ids
    editor_ids = list(self.editors.keys())
    current_index = editor_ids.index(self.active_container_id)
    next_index = (current_index + 1) % len(editor_ids)
    self.set_active_container(editor_ids[next_index])

def action_quit(self) -> None:
    """Quit the application."""
    self.exit()
```

These methods handle editor navigation and closing:
- Close Editor (Ctrl+W)
- Focus Next Editor (Tab)
- Quit (Ctrl+Q)

## Putting It All Together

Now we need to add a helper method to generate unique IDs for new editors, and a main function to run the application:

```python
def generate_container_id(self) -> str:
    """Generate a unique ID for a new editor container."""
    existing_ids = list(self.editors.keys())
    for i in range(100):  # Reasonable upper limit
        new_id = f"editor-{i}"
        if new_id not in existing_ids:
            return new_id
    return f"editor-{len(existing_ids)}"

async def load_file_to_editor(self, path: str, container_id: str) -> None:
    """Load a file into the specified editor."""
    container = self.query_one(f"#{container_id}", EditorContainer)
    await container.load_file(path)

def main(file_path: Optional[str] = None):
    app = CodeEditorApp(file_path)
    app.run()

if __name__ == "__main__":
    import sys
    file_path = sys.argv[1] if len(sys.argv) > 1 else None
    main(file_path)
```

## Running the Application

With all the code in place, you can run the application with:

```bash
python code_editor.py [optional_file_path]
```

### Keyboard Shortcuts Summary

Here's a summary of all the keyboard shortcuts:

- **Ctrl+N**: Create a new file
- **Ctrl+O**: Open a file
- **Ctrl+S**: Save the current file
- **Ctrl+Shift+S**: Save the current file with a new name
- **Ctrl+V**: Split the view vertically
- **Ctrl+H**: Split the view horizontally
- **Ctrl+W**: Close the current editor
- **Tab**: Switch to the next editor
- **Ctrl+Q**: Quit the application

Within the editor:
- **Arrow keys**: Move the cursor
- **Home/End**: Move to the start/end of the line
- **Backspace/Delete**: Delete characters
- **Enter**: Insert a new line with proper indentation
- **Tab**: Insert spaces (based on tab size)
- **Escape**: Leave the editor focus (to use app-level shortcuts)

## Final Thoughts

You now have a fully functional terminal-based code editor with:
- Syntax highlighting for various languages
- File operations (new, open, save, save as)
- Split view editing (vertical and horizontal)
- Keyboard shortcuts for all operations
- No buttons, keeping the interface clean and keyboard-focused

The editor is highly extensible. You could enhance it further by adding features like:
- Find and replace functionality
- Line numbering
- Code folding
- Themes and color schemes
- Support for multiple cursors
- Auto-completion
- Integration with version control systems

This editor demonstrates the power of Textual for creating sophisticated terminal applications. The library handles terminal rendering, event processing, and UI layout, allowing you to focus on implementing the editor's functionality.