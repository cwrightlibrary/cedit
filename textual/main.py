from textual.app import App
from textual.widgets import Header, Footer


class CodeEditorApp(App):
    BINDINGS = [
        ("ctrl+q", "quit", "Quit"),
        ("ctrl+s", "save", "Save"),
    ]

    def compose(self):
        yield Header(show_clock=True)
        yield Footer()
    
    def action_quit(self):
        self.exit()
    
    def action_save(self):
        self.notify("Save functionality will be implemented later")


if __name__ == "__main__":
    app = CodeEditorApp()
    app.run()