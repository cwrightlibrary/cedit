from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Button, Footer, Header, Input, TextArea
from pathlib import Path


class FileDialog(Container):
    def __init__(self, action="open"):
        super().__init__()
        self.action = action
    
    def compose(self) -> ComposeResult:
        yield Input(placeholder="Enter file path...", id="file_path")
        yield Button("Cancel", variant="error", id="cancel")
        yield Button("OK", variant="success", id="ok")


class TextEditor(App):
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+s", "save", "Save"),
        Binding("ctrl+o", "open_file", "Open"),
    ]

    def __init__(self):
        super().__init__()
        self.current_file = None
    
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield TextArea(id="editor")
        yield Footer()
    
    def action_quit(self) -> None:
        self.exit()
    
    def action_save(self) -> None:
        if self.current_file:
            self._save_file(self.current_file)
        else:
            self.mount(FileDialog(action="save"))
    
    def action_open_file(self) -> None:
        self.mount(FileDialog(action="open"))
    
    


if __name__ == "__main__":
    app = TextEditor()
    app.run()