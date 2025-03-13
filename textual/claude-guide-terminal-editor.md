# Building a Terminal-Based Code Editor with Python and Textual

In this guide, I'll walk you through creating a minimal yet functional terminal-based code editor using Python and the Textual library. Textual is a TUI (Text User Interface) framework that makes building rich terminal applications surprisingly straightforward.

## Step 1: Setting Up the Environment

### Objective & Explanation
Before we start coding, we need to set up our development environment and install the necessary dependencies. Textual is a modern Python library designed for creating sophisticated terminal user interfaces with features like responsive layouts, event handling, and styling.

### Code Snippets
First, create a virtual environment and install the required packages:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment (Linux/macOS)
source venv/bin/activate

# Activate the virtual environment (Windows)
# venv\Scripts\activate

# Install textual
pip install textual
```

### Detailed Functionality Discussion
Textual is built upon the `rich` library, which provides advanced terminal formatting. Together, they allow us to create applications with:
- Responsive layouts
- Event-driven architecture
- CSS-like styling
- Unicode and emoji support
- Support for mouse events and keyboard input

## Step 2: Creating the Basic Application Structure

### Objective & Explanation
In this step, we'll create the basic structure of our editor application. We'll define the main application class that will hold our editor's components and handle the overall application lifecycle.

### Code Snippets

```python
from textual.app import App
from textual.widgets import Header, Footer

class CodeEditorApp(App):
    """A simple terminal-based code editor."""
    
    BINDINGS = [
        ("ctrl+q", "quit", "Quit"),
        ("ctrl+s", "save", "Save"),
    ]
    
    def compose(self):
        """Compose the UI layout."""
        yield Header(show_clock=True)
        # We'll add the editor component here in the next step
        yield Footer()
    
    def action_quit(self):
        """Quit the application."""
        self.exit()
    
    def action_save(self):
        """Save the current file."""
        self.notify("Save functionality will be implemented later.")

if __name__ == "__main__":
    app = CodeEditorApp()
    app.run()
```

### Detailed Functionality Discussion
- **App**: The main application class from Textual that manages the application lifecycle and rendering.
- **Header/Footer**: Built-in widgets that provide a consistent UI for your application with useful information like the current time.
- **BINDINGS**: A list of key bindings that map keyboard shortcuts to actions. Each binding is a tuple containing the key combination, the action name, and a description.
- **compose**: This method defines the UI layout by yielding widgets that will be displayed in the application.
- **action_***: Methods prefixed with `action_` are automatically connected to the corresponding binding. For example, `action_quit` is called when the user presses Ctrl+Q.

This basic structure provides the skeleton of our editor, with a header displaying the time and a footer showing available keyboard shortcuts.

## Step 3: Adding a Text Editing Area

### Objective & Explanation
Now we'll add the main component of our editor: a widget for editing text. We'll use Textual's `TextArea` widget, which provides rich text editing capabilities.

### Code Snippets

```python
from textual.app import App
from textual.widgets import Header, Footer, TextArea
from textual.binding import Binding

class CodeEditorApp(App):
    """A simple terminal-based code editor."""
    
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+s", "save", "Save"),
        Binding("ctrl+o", "open", "Open"),
    ]
    
    def compose(self):
        """Compose the UI layout."""
        yield Header(show_clock=True)
        yield TextArea(language="python")
        yield Footer()
    
    def on_mount(self):
        """Called when the app is mounted."""
        # Focus the text area when the app starts
        self.query_one(TextArea).focus()
    
    def action_quit(self):
        """Quit the application."""
        self.exit()
    
    def action_save(self):
        """Save the current file."""
        self.notify("Save functionality will be implemented later.")
    
    def action_open(self):
        """Open a file."""
        self.notify("Open functionality will be implemented later.")

if __name__ == "__main__":
    app = CodeEditorApp()
    app.run()
```

### Detailed Functionality Discussion
- **TextArea**: A built-in widget that provides text editing capabilities, including syntax highlighting for various programming languages.
- **on_mount**: This method is called when the application is fully loaded. We use it to focus the text area, so the user can start typing immediately.
- **query_one**: A method that allows you to query for a specific widget in your application. In this case, we're getting the TextArea to focus it.

The `TextArea` widget is perfect for our code editor as it already has features like:
- Syntax highlighting (via the `language` parameter)
- Line numbers
- Cursor movement
- Text selection
- Basic editing operations (insert, delete, etc.)

## Step 4: Implementing File Operations

### Objective & Explanation
A code editor needs to be able to open and save files. In this step, we'll implement these basic file operations using Python's standard file handling capabilities integrated with our Textual app.

### Code Snippets

```python
from textual.app import App
from textual.widgets import Header, Footer, TextArea, Input, Label
from textual.binding import Binding
from textual.containers import Container
import os

class FileInputDialog(Container):
    """A dialog for file input (open/save)."""
    
    def __init__(self, title, action, default_path="", **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.action = action
        self.default_path = default_path
    
    def compose(self):
        yield Label(self.title)
        yield Input(value=self.default_path, id="file_path")
    
    def on_input_submitted(self, event):
        """Handle the input submission."""
        self.app.file_operation(self.action, event.value)
        self.remove()

class CodeEditorApp(App):
    """A simple terminal-based code editor."""
    
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+s", "save", "Save"),
        Binding("ctrl+o", "open", "Open"),
        Binding("escape", "cancel", "Cancel"),
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_file = None
    
    def compose(self):
        """Compose the UI layout."""
        yield Header(show_clock=True)
        yield TextArea(language="python", id="editor")
        yield Footer()
    
    def on_mount(self):
        """Called when the app is mounted."""
        # Focus the text area when the app starts
        self.query_one(TextArea).focus()
    
    def action_quit(self):
        """Quit the application."""
        self.exit()
    
    def action_save(self):
        """Save the current file."""
        if self.current_file:
            self.file_operation("save", self.current_file)
        else:
            dialog = FileInputDialog("Save file as:", "save", default_path="untitled.py")
            self.mount(dialog)
    
    def action_open(self):
        """Open a file."""
        dialog = FileInputDialog("Open file:", "open")
        self.mount(dialog)
    
    def action_cancel(self):
        """Cancel current dialog."""
        try:
            dialog = self.query_one(FileInputDialog)
            dialog.remove()
        except:
            pass
    
    def file_operation(self, action, file_path):
        """Handle file operations."""
        editor = self.query_one("#editor", TextArea)
        
        if action == "open":
            try:
                with open(file_path, "r") as f:
                    content = f.read()
                editor.text = content
                self.current_file = file_path
                self.notify(f"Opened {file_path}")
            except Exception as e:
                self.notify(f"Error opening file: {e}", severity="error")
        
        elif action == "save":
            try:
                with open(file_path, "w") as f:
                    f.write(editor.text)
                self.current_file = file_path
                self.notify(f"Saved {file_path}")
            except Exception as e:
                self.notify(f"Error saving file: {e}", severity="error")

if __name__ == "__main__":
    app = CodeEditorApp()
    app.run()
```

### Detailed Functionality Discussion
- **FileInputDialog**: A custom container that includes a label and an input field for entering file paths.
- **Input**: A widget that allows users to enter text. We use it for entering file paths.
- **Container**: A base class for containers in Textual, which can hold other widgets.
- **mount**: A method that adds a widget to the application at runtime.
- **query_one**: We're now using it with an ID selector (`#editor`) to get specific widgets.
- **notify**: A method that shows a notification to the user, useful for displaying success or error messages.

This implementation provides basic file operations with a simple dialog for entering file paths. When opening a file, we read its contents and update the text area. When saving, we write the text area's contents to the specified file.

## Step 5: Enhancing the Editor with Line Numbers and Syntax Highlighting

### Objective & Explanation
Let's enhance our editor with more advanced features like line numbers and improved syntax highlighting. Textual's `TextArea` already supports these features, but we'll customize them to make our editor more powerful.

### Code Snippets

```python
from textual.app import App
from textual.widgets import Header, Footer, TextArea, Input, Label, Select
from textual.binding import Binding
from textual.containers import Container, Horizontal
import os

class FileInputDialog(Container):
    """A dialog for file input (open/save)."""
    
    def __init__(self, title, action, default_path="", **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.action = action
        self.default_path = default_path
    
    def compose(self):
        yield Label(self.title)
        yield Input(value=self.default_path, id="file_path")
    
    def on_input_submitted(self, event):
        """Handle the input submission."""
        self.app.file_operation(self.action, event.value)
        self.remove()

class LanguageSelector(Container):
    """A dialog for selecting a programming language."""
    
    def compose(self):
        yield Label("Select language:")
        yield Select(
            [
                ("Python", "python"),
                ("JavaScript", "javascript"),
                ("HTML", "html"),
                ("CSS", "css"),
                ("Markdown", "markdown"),
                ("Plain Text", ""),
            ],
            id="language_select",
        )
    
    def on_select_changed(self, event):
        """Handle the language selection."""
        self.app.set_language(event.value)
        self.remove()

class CodeEditorApp(App):
    """A simple terminal-based code editor."""
    
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+s", "save", "Save"),
        Binding("ctrl+o", "open", "Open"),
        Binding("ctrl+l", "language", "Language"),
        Binding("escape", "cancel", "Cancel"),
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_file = None
    
    def compose(self):
        """Compose the UI layout."""
        yield Header(show_clock=True)
        
        # Create a text area with line numbers and syntax highlighting
        yield TextArea(
            language="python",
            id="editor",
            show_line_numbers=True,
            theme="monokai"
        )
        
        yield Footer()
    
    def on_mount(self):
        """Called when the app is mounted."""
        # Focus the text area when the app starts
        self.query_one(TextArea).focus()
    
    def action_quit(self):
        """Quit the application."""
        self.exit()
    
    def action_save(self):
        """Save the current file."""
        if self.current_file:
            self.file_operation("save", self.current_file)
        else:
            dialog = FileInputDialog("Save file as:", "save", default_path="untitled.py")
            self.mount(dialog)
    
    def action_open(self):
        """Open a file."""
        dialog = FileInputDialog("Open file:", "open")
        self.mount(dialog)
    
    def action_language(self):
        """Change the programming language."""
        selector = LanguageSelector()
        self.mount(selector)
    
    def action_cancel(self):
        """Cancel current dialog."""
        for dialog_class in [FileInputDialog, LanguageSelector]:
            try:
                dialog = self.query_one(dialog_class)
                dialog.remove()
                return
            except:
                pass
    
    def file_operation(self, action, file_path):
        """Handle file operations."""
        editor = self.query_one("#editor", TextArea)
        
        if action == "open":
            try:
                with open(file_path, "r") as f:
                    content = f.read()
                editor.text = content
                self.current_file = file_path
                
                # Try to detect language from file extension
                _, ext = os.path.splitext(file_path)
                ext = ext.lower().lstrip(".")
                language_map = {
                    "py": "python",
                    "js": "javascript",
                    "html": "html",
                    "css": "css",
                    "md": "markdown",
                }
                if ext in language_map:
                    editor.language = language_map[ext]
                
                self.notify(f"Opened {file_path}")
            except Exception as e:
                self.notify(f"Error opening file: {e}", severity="error")
        
        elif action == "save":
            try:
                with open(file_path, "w") as f:
                    f.write(editor.text)
                self.current_file = file_path
                self.notify(f"Saved {file_path}")
            except Exception as e:
                self.notify(f"Error saving file: {e}", severity="error")
    
    def set_language(self, language):
        """Set the editor language."""
        editor = self.query_one("#editor", TextArea)
        editor.language = language
        self.notify(f"Language set to: {language or 'Plain Text'}")

if __name__ == "__main__":
    app = CodeEditorApp()
    app.run()
```

### Detailed Functionality Discussion
- **Select**: A widget that provides a dropdown menu for selecting options. We use it for language selection.
- **TextArea Parameters**:
  - `show_line_numbers=True`: Enables line numbers in the editor.
  - `theme="monokai"`: Sets a syntax highlighting theme, in this case, the popular Monokai theme.
  - `language="python"`: Sets the initial language for syntax highlighting.
- **LanguageSelector**: A custom container that includes a label and a select widget for choosing a programming language.
- **Language Detection**: When opening a file, we attempt to detect the language based on the file extension to set the appropriate syntax highlighting.

These enhancements make our editor more useful for coding by providing visual cues like line numbers and syntax highlighting, with the ability to change the language as needed.

## Step 6: Adding Status Information and Path Display

### Objective & Explanation
In this step, we'll add a status bar to display information about the current file, cursor position, and other useful details. This gives users important context about their work and the state of the editor.

### Code Snippets

```python
from textual.app import App
from textual.widgets import Header, Footer, TextArea, Input, Label, Select, Static
from textual.binding import Binding
from textual.containers import Container, Horizontal
from rich.text import Text
import os

class StatusBar(Static):
    """A status bar to display file and cursor information."""
    
    def __init__(self, **kwargs):
        super().__init__("", **kwargs)
        self.update_status()
    
    def update_status(self, file_path=None, cursor_position=(1, 1), language=None):
        """Update the status bar content."""
        file_info = f"File: {file_path or 'Untitled'}"
        position_info = f"Line: {cursor_position[0]}, Column: {cursor_position[1]}"
        lang_info = f"Language: {language or 'Plain Text'}"
        
        text = Text()
        text.append(file_info, style="bold green")
        text.append(" | ")
        text.append(position_info, style="bold blue")
        text.append(" | ")
        text.append(lang_info, style="bold magenta")
        
        self.update(text)

class FileInputDialog(Container):
    """A dialog for file input (open/save)."""
    
    DEFAULT_CSS = """
    FileInputDialog {
        background: $surface;
        padding: 1 2;
        border: tall $primary;
        width: 60;
        height: 5;
    }
    """
    
    def __init__(self, title, action, default_path="", **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.action = action
        self.default_path = default_path
    
    def compose(self):
        yield Label(self.title)
        yield Input(value=self.default_path, id="file_path")
    
    def on_input_submitted(self, event):
        """Handle the input submission."""
        self.app.file_operation(self.action, event.value)
        self.remove()

class LanguageSelector(Container):
    """A dialog for selecting a programming language."""
    
    DEFAULT_CSS = """
    LanguageSelector {
        background: $surface;
        padding: 1 2;
        border: tall $primary;
        width: 60;
        height: 8;
    }
    """
    
    def compose(self):
        yield Label("Select language:")
        yield Select(
            [
                ("Python", "python"),
                ("JavaScript", "javascript"),
                ("HTML", "html"),
                ("CSS", "css"),
                ("Markdown", "markdown"),
                ("Plain Text", ""),
            ],
            id="language_select",
        )
    
    def on_select_changed(self, event):
        """Handle the language selection."""
        self.app.set_language(event.value)
        self.remove()

class CodeEditorApp(App):
    """A simple terminal-based code editor."""
    
    CSS = """
    TextArea {
        border: none;
    }
    
    StatusBar {
        height: 1;
        padding: 0 1;
        background: $surface;
    }
    """
    
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+s", "save", "Save"),
        Binding("ctrl+o", "open", "Open"),
        Binding("ctrl+l", "language", "Language"),
        Binding("escape", "cancel", "Cancel"),
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_file = None
    
    def compose(self):
        """Compose the UI layout."""
        yield Header(show_clock=True)
        
        # Create a text area with line numbers and syntax highlighting
        yield TextArea(
            language="python",
            id="editor",
            show_line_numbers=True,
            theme="monokai"
        )
        
        yield StatusBar(id="status_bar")
        yield Footer()
    
    def on_mount(self):
        """Called when the app is mounted."""
        # Focus the text area when the app starts
        self.query_one(TextArea).focus()
        # Update status bar
        self.update_status_bar()
    
    def on_text_area_cursor_moved(self, event):
        """Handle cursor movement in the text area."""
        self.update_status_bar(cursor_position=event.cursor)
    
    def update_status_bar(self, cursor_position=None):
        """Update the status bar with current information."""
        editor = self.query_one("#editor", TextArea)
        status_bar = self.query_one("#status_bar", StatusBar)
        
        if cursor_position is None:
            cursor_position = editor.cursor_location
        
        status_bar.update_status(
            file_path=self.current_file,
            cursor_position=cursor_position,
            language=editor.language or "Plain Text"
        )
    
    def action_quit(self):
        """Quit the application."""
        self.exit()
    
    def action_save(self):
        """Save the current file."""
        if self.current_file:
            self.file_operation("save", self.current_file)
        else:
            dialog = FileInputDialog("Save file as:", "save", default_path="untitled.py")
            self.mount(dialog)
    
    def action_open(self):
        """Open a file."""
        dialog = FileInputDialog("Open file:", "open")
        self.mount(dialog)
    
    def action_language(self):
        """Change the programming language."""
        selector = LanguageSelector()
        self.mount(selector)
    
    def action_cancel(self):
        """Cancel current dialog."""
        for dialog_class in [FileInputDialog, LanguageSelector]:
            try:
                dialog = self.query_one(dialog_class)
                dialog.remove()
                return
            except:
                pass
    
    def file_operation(self, action, file_path):
        """Handle file operations."""
        editor = self.query_one("#editor", TextArea)
        
        if action == "open":
            try:
                with open(file_path, "r") as f:
                    content = f.read()
                editor.text = content
                self.current_file = file_path
                
                # Try to detect language from file extension
                _, ext = os.path.splitext(file_path)
                ext = ext.lower().lstrip(".")
                language_map = {
                    "py": "python",
                    "js": "javascript",
                    "html": "html",
                    "css": "css",
                    "md": "markdown",
                }
                if ext in language_map:
                    editor.language = language_map[ext]
                
                self.update_status_bar()
                self.notify(f"Opened {file_path}")
            except Exception as e:
                self.notify(f"Error opening file: {e}", severity="error")
        
        elif action == "save":
            try:
                with open(file_path, "w") as f:
                    f.write(editor.text)
                self.current_file = file_path
                self.update_status_bar()
                self.notify(f"Saved {file_path}")
            except Exception as e:
                self.notify(f"Error saving file: {e}", severity="error")
    
    def set_language(self, language):
        """Set the editor language."""
        editor = self.query_one("#editor", TextArea)
        editor.language = language
        self.update_status_bar()
        self.notify(f"Language set to: {language or 'Plain Text'}")

if __name__ == "__main__":
    app = CodeEditorApp()
    app.run()
```

### Detailed Functionality Discussion
- **Static**: A base widget for displaying text content. We extend it to create our StatusBar.
- **CSS Styling**: We're now using Textual's CSS-like styling capabilities to customize the appearance of our widgets.
  - `DEFAULT_CSS`: Class-specific styling directly in the widget class.
  - `CSS`: App-level styling for all widgets.
- **Rich Text**: We use Rich's Text class to create styled text with different colors for different parts of the status bar.
- **Event Handling**:
  - `on_text_area_cursor_moved`: A method that responds to cursor movements in the text area, allowing us to update the cursor position in the status bar.
- **update_status_bar**: A method that updates the status bar with current file, cursor, and language information.

The status bar provides valuable context to the user about their current editing session, including file path, cursor position, and active language for syntax highlighting.

## Step 7: Final Code - Complete Terminal-Based Code Editor

### Objective & Explanation
Now, let's combine all the pieces to create our complete terminal-based code editor. This final version includes all the features we've built: text editing, file operations, syntax highlighting, line numbers, and status information.

### Final Minimal Code

```python
from textual.app import App
from textual.widgets import Header, Footer, TextArea, Input, Label, Select, Static
from textual.binding import Binding
from textual.containers import Container, Horizontal
from rich.text import Text
import os

class StatusBar(Static):
    """A status bar to display file and cursor information."""
    
    def __init__(self, **kwargs):
        super().__init__("", **kwargs)
        self.update_status()
    
    def update_status(self, file_path=None, cursor_position=(1, 1), language=None):
        """Update the status bar content."""
        file_info = f"File: {file_path or 'Untitled'}"
        position_info = f"Line: {cursor_position[0]}, Column: {cursor_position[1]}"
        lang_info = f"Language: {language or 'Plain Text'}"
        
        text = Text()
        text.append(file_info, style="bold green")
        text.append(" | ")
        text.append(position_info, style="bold blue")
        text.append(" | ")
        text.append(lang_info, style="bold magenta")
        
        self.update(text)

class FileInputDialog(Container):
    """A dialog for file input (open/save)."""
    
    DEFAULT_CSS = """
    FileInputDialog {
        background: $surface;
        padding: 1 2;
        border: tall $primary;
        width: 60;
        height: 5;
    }
    """
    
    def __init__(self, title, action, default_path="", **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.action = action
        self.default_path = default_path
    
    def compose(self):
        yield Label(self.title)
        yield Input(value=self.default_path, id="file_path")
    
    def on_input_submitted(self, event):
        """Handle the input submission."""
        self.app.file_operation(self.action, event.value)
        self.remove()

class LanguageSelector(Container):
    """A dialog for selecting a programming language."""
    
    DEFAULT_CSS = """
    LanguageSelector {
        background: $surface;
        padding: 1 2;
        border: tall $primary;
        width: 60;
        height: 8;
    }
    """
    
    def compose(self):
        yield Label("Select language:")
        yield Select(
            [
                ("Python", "python"),
                ("JavaScript", "javascript"),
                ("HTML", "html"),
                ("CSS", "css"),
                ("Markdown", "markdown"),
                ("Plain Text", ""),
            ],
            id="language_select",
        )
    
    def on_select_changed(self, event):
        """Handle the language selection."""
        self.app.set_language(event.value)
        self.remove()

class CodeEditorApp(App):
    """A simple terminal-based code editor."""
    
    CSS = """
    TextArea {
        border: none;
    }
    
    StatusBar {
        height: 1;
        padding: 0 1;
        background: $surface;
    }
    """
    
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+s", "save", "Save"),
        Binding("ctrl+o", "open", "Open"),
        Binding("ctrl+l", "language", "Language"),
        Binding("escape", "cancel", "Cancel"),
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_file = None
    
    def compose(self):
        """Compose the UI layout."""
        yield Header(show_clock=True)
        
        # Create a text area with line numbers and syntax highlighting
        yield TextArea(
            language="python",
            id="editor",
            show_line_numbers=True,
            theme="monokai"
        )
        
        yield StatusBar(id="status_bar")
        yield Footer()
    
    def on_mount(self):
        """Called when the app is mounted."""
        # Focus the text area when the app starts
        self.query_one(TextArea).focus()
        # Update status bar
        self.update_status_bar()
    
    def on_text_area_cursor_moved(self, event):
        """Handle cursor movement in the text area."""
        self.update_status_bar(cursor_position=event.cursor)
    
    def update_status_bar(self, cursor_position=None):
        """Update the status bar with current information."""
        editor = self.query_one("#editor", TextArea)
        status_bar = self.query_one("#status_bar", StatusBar)
        
        if cursor_position is None:
            cursor_position = editor.cursor_location
        
        status_bar.update_status(
            file_path=self.current_file,
            cursor_position=cursor_position,
            language=editor.language or "Plain Text"
        )
    
    def action_quit(self):
        """Quit the application."""
        self.exit()
    
    def action_save(self):
        """Save the current file."""
        if self.current_file:
            self.file_operation("save", self.current_file)
        else:
            dialog = FileInputDialog("Save file as:", "save", default_path="untitled.py")
            self.mount(dialog)
    
    def action_open(self):
        """Open a file."""
        dialog = FileInputDialog("Open file:", "open")
        self.mount(dialog)
    
    def action_language(self):
        """Change the programming language."""
        selector = LanguageSelector()
        self.mount(selector)
    
    def action_cancel(self):
        """Cancel current dialog."""
        for dialog_class in [FileInputDialog, LanguageSelector]:
            try:
                dialog = self.query_one(dialog_class)
                dialog.remove()
                return
            except:
                pass
    
    def file_operation(self, action, file_path):
        """Handle file operations."""
        editor = self.query_one("#editor", TextArea)
        
        if action == "open":
            try:
                with open(file_path, "r") as f:
                    content = f.read()
                editor.text = content
                self.current_file = file_path
                
                # Try to detect language from file extension
                _, ext = os.path.splitext(file_path)
                ext = ext.lower().lstrip(".")
                language_map = {
                    "py": "python",
                    "js": "javascript",
                    "html": "html",
                    "css": "css",
                    "md": "markdown",
                }
                if ext in language_map:
                    editor.language = language_map[ext]
                
                self.update_status_bar()
                self.notify(f"Opened {file_path}")
            except Exception as e:
                self.notify(f"Error opening file: {e}", severity="error")
        
        elif action == "save":
            try:
                with open(file_path, "w") as f:
                    f.write(editor.text)
                self.current_file = file_path
                self.update_status_bar()
                self.notify(f"Saved {file_path}")
            except Exception as e:
                self.notify(f"Error saving file: {e}", severity="error")
    
    def set_language(self, language):
        """Set the editor language."""
        editor = self.query_one("#editor", TextArea)
        editor.language = language
        self.update_status_bar()
        self.notify(f"Language set to: {language or 'Plain Text'}")

if __name__ == "__main__":
    app = CodeEditorApp()
    app.run()
```
