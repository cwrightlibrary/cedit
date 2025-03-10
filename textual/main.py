import re
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Button, Footer, Header, Input, Label, TextArea
from pathlib import Path
from rich.syntax import Syntax
from rich.text import Text


class FileDialog(Container):
    def __init__(self, action="open"):
        super().__init__()
        self.action = action
    
    def compose(self) -> ComposeResult:
        yield Input(placeholder="Enter file path...", id="file_path")
        yield Button("Cancel", variant="error", id="cancel")
        yield Button("OK", variant="success", id="ok")


class SyntaxHighlightedTextArea(TextArea):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.language = "python"
    
    def set_language(self, language):
        self.language = language
        self.highlight_syntax()
    
    def highlight_syntax(self):
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
            self.app.notify(f"Syntax highlighting applied for {self.language}")
        except Exception as e:
            self.app.notify(f"Error highlighting syntax: {e}", severity="error")
    
    def on_text_changed(self, event):
        pass


class StatusBar(Container):
    def compose(self) -> ComposeResult:
        yield Label("Line: 1, Col: 1", id="position")
        yield Label("Python", id="language")
        yield Label("UTF-8", id="encoding")


class cedit(App):
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+s", "save", "Save"),
        Binding("ctrl+o", "open_file", "Open"),
    ]

    def __init__(self):
        super().__init__()
        self.current_file = None
        self.highlighting_enabled = True
    
    def compose(self) -> ComposeResult:
        yield SyntaxHighlightedTextArea(id="editor")
        yield StatusBar()
        # yield TextArea(id="editor")
        yield Footer()
    
    def on_mount(self) -> None:
        self.update_status_bar()
    
    def update_status_bar(self) -> None:
        editor = self.query_one("#editor", SyntaxHighlightedTextArea)
        cursor = editor.cursor_location
        line = cursor[0] + 1
        col = cursor[1] + 1

        position_label = self.query_one("#position", Label)
        position_label.update(f"Line: {line}, Col: {col}")

        if self.current_file:
            extension = Path(self.current_file).suffix.lstrip(".")
            language_map = {
                "py": "Python",
                "js": "JavaScript",
                "html": "HTML",
                "css": "CSS",
                "md": "Markdown",
                "txt": "Plain Text",
            }
            language = language_map.get(extension, "Plain Text")
            language_label = self.query_one("#language", Label)
            language_label.update(language)

            editor.set_language(language.lower())
    
    def action_quit(self) -> None:
        self.exit()
    
    def action_save(self) -> None:
        if self.current_file:
            self._save_file(self.current_file)
        else:
            self.mount(FileDialog(action="save"))
    
    def action_open_file(self) -> None:
        self.mount(FileDialog(action="open"))
    
    def action_toggle_highlighting(self) -> None:
        self.highlighting_enabled = not self.highlighting_enabled
        editor = self.query_one("#editor", SyntaxHighlightedTextArea)

        if self.highlighting_enabled:
            editor.highlight_syntax()
            self.notify("Syntax highlighting enabled")
        else:
            self.notify("Syntax highlighting disabled")
    
    def action_search(self) -> None:
        self.notify("Search not implemented yet")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "cancel":
            self.query_one(FileDialog).remove()
        elif button_id == "ok":
            file_path = self.query_one("#file_path").value
            dialog = self.query_one(FileDialog)

            if dialog.action == "open":
                self._open_file(file_path)
            else:
                self._save_file(file_path)
            
            dialog.remove()
    
    def _open_file(self, file_path):
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
    app = cedit()
    app.run()