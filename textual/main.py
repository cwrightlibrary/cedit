import os
import pathlib
from rich.syntax import Syntax
from rich.text import Text
from textual import events
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Input, Static


class Editor(Static):
    COMPONENT_CLASSES = {"editor", "editor--cursor"}
    CSS_PATH = "stylesheet.tcss"

    def __init__(
            self,
            text: str="",
            language: str="python",
            tab_size: int=4,
            path: str=None,
            name: str=None,
            id: str=None,
            classes: str=None,
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
    
    def update_syntax(self) -> None:
        content = self.query_one("#editor-content", Static)

        if self.path and os.path.exists(self.path):
            extension = pathlib.Path(self.path).suffix.lstrip(".")
            if extension:
                self.language = extension
        
        text = "\n".join(self.lines)

        syntax = Syntax(
            text,
            self.language,
            theme="monokai",
            line_numbers=True,
            word_wrap=True,
            tab_size=self.tab_size,
        )

        content.update(syntax)

        app = self.app
        if isinstance(app, Cedit):
            modified_indicator = "*" if self.is_modified else ""
            path_display = self.path if self.path else "Untitled"
            app.sub_title = f"{path_display}{modified_indicator}"
    
    def insert_text(self, text: str) -> None:
        current_line = self.lines[self.cursor_row]

        if text == "\t":
            text = " " * self.tab_size
        
        new_line = current_line[:self.cursor_col] + text + current_line[self.cursor_col:]
        self.linse[self.cursor_row] = new_line
        self.cursor_col += len(text)

        self.is_modified = True
        self.update_syntax()
    
    def delete_character(self) -> None:
        if self.cursor_col > 0:
            current_line = self.lines[self.cursor_row]
            new_line = current_line[:self.cursor_col - 1] + current_line[self.cursor_col:]
            self.lines[self.cursor_row] = new_line
            self.cursor_col -= 1
            self.is_modified = True
        elif self.cursor_row > 0:
            current_line = self.lines.pop(self.cursor_row)
            self.cursor_row -= 1
            self.cursor_col = len(self.lines[self.cursor_col])
            self.lines[self.cursor_row] += current_line
            self.is_modified = True
        
        self.update_syntax()
    
    def handle_enter(self) -> None:
        current_line = self.lines[self.cursor_row]

        indent = len(current_line) - len(current_line.lstrip())
        indentation = " " * indent

        before_cursor = current_line[:self.cursor_col]
        after_cursor = current_line[self.cursor_col:]

        self.lines[self.cursor_row] = before_cursor
        self.lines.insert(self.cursor_row + 1, indentation + after_cursor)

        self.cursor_row += 1
        self.cursor_col = len(indentation)

        self.is_modified = True
        self.update_syntax()

    def move_cursor(self, rows: int = 0, cols: int = 0) -> None:
        new_row = max(0, min(len(self.lines) - 1, self.cursor_row + rows))

        if new_row != self.cursor_row:
            self.cursor_row = new_row
            self.cursor_col = min(self.cursor_col, len(self.lines[self.cursor_row]))

        self.cursor_col = max(0, min(len(self.lines[self.cursor_row]), self.cursor_col + cols))

        self.update_syntax()
    
    def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            self.screen.focus_next()
            return
        
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
        elif event.key == "enter":
            self.handle_enter()
        elif event.key == "backspace":
            self.delete_character()
        elif event.key == "delete":
            if self.cursor_col < len(self.lines[self.cursor_row]):
                self.move_cursor(cols=1)
                self.delete_character()
        elif len(event.key) == 1 or event.key == "tab":
            self.insert_text(event.key)


class FialDialog(Screen):
    CSS_PATH = "stylesheet.tcss"

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "confirm", "Confirm"),
    ]

    def __init__(self, title: str, default_path: str="", action: str="open"):
        super().__init__()
        self.title = title
        self.default_path = default_path
        self.action = action
    
    def compose(self) -> ComposeResult:
        with Container(id="dialog-container"):
            yield Static(self.title, id="dialog-title")
            yield Input(value=self.default_path, placeholder="Enter file path ... ", id="file-path")
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value)
    
    def action_cancel(self) -> None:
        self.dismiss(None)
    
    def action_confirm(self) -> None:
        file_path = self.query_one("#file-path").value
        self.dismiss(file_path)


class EditorContainer(Container):
    def __init__(
            self,
            text: str="",
            language: str="python",
            path: str=None,
            name: str=None,
            id: str=None,
            classes: str=None,
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
    
    async def save_file(self, path: str=None) -> bool:
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

class Cedit(App):
    pass