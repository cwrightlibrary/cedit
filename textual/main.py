from textual.app import App, ComposeResult
from textual.widgets import Static


class Cedit(App):
    CSS_PATH = "stylesheet.tcss"
    def compose(self) -> ComposeResult:
        self.cedit_title_widget = Static("cedit", id="cedit-title")
        yield self.widget


if __name__ == "__main__":
    app = Cedit()
    app.run()