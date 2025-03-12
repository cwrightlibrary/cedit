import os
import pathlib
from rich.syntax import Syntax
from rich.text import Text
from textual import events
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, Static
from typing import Dict, Optional


class Editor(Static):
    COMPONENT_CLASSES = {"editor", "editor--cursor"}
    CSS_PATH = "stylesheet.tcss"

    def __init__(
            self,
            text: str="",
            language: str="python",
            tab_size: int=4,
            path: Optional[str]=None,
            name: Optional[str]=None,
            id: Optional[str]=None,
            classes: Optional[str]=None,
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


class FileDialog(Screen):
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
            path: Optional[str]=None,
            name: Optional[str]=None,
            id: Optional[str]=None,
            classes: Optional[str]=None,
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
    TITLE = "cedit"
    SUB_TITLE = "Untitled"

    BINDINGS = [
        Binding("ctrl+n", "new_file", "New File"),
        Binding("ctrl+o", "open_file", "Open"),
        Binding("ctrl+s", "save_file", "Save"),
        Binding("ctrl+shift+s", "save_as", "Save As"),
        Binding("ctrl+]", "split_vertical", "Split Vertical"),
        Binding("ctrl+[", "split_horizontal", "Split Horizontal"),
        Binding("ctrl+w", "close_editor", "Close Editor"),
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+\\", "focus_next", "Next Editor"),
    ]

    def __init__(self, path: Optional[str]=None):
        super().__init__()
        self.initial_path = path
        self.editors: Dict[str, EditorContainer] = {}
        self.active_container_id = None
    
    def compose(self) -> ComposeResult:
        yield Header()

        with Horizontal(id="main-container"):
            editor_id = "editor-0"
            container = EditorContainer(id=editor_id)
            self.editors[editor_id] = container
            self.active_container_id = editor_id
            yield container
        
        yield Static("Ready", classes="status-bar", id="status-bar")
        yield Footer()
    
    def on_mount(self) -> None:
        if self.initial_path and os.path.exists(self.initial_path):
            self.load_file_to_editor(self.initial_path, self.active_container_id)
    
    def get_active_container(self) -> Optional[Editor]:
        if not self.active_container_id:
            return None
        
        container = self.query_one(f"#{self.active_container_id}", EditorContainer)
        return container.query_one(Editor)
    
    def set_active_container(self, container_id: str) -> None:
        self.active_container_id = container_id

        container = self.get_active_container()
        if container:
            editor = container.query_one(Editor)
            path_display = editor.path if editor.path else "Untitled"
            status = self.query_one("#status-bar", Static)
            status.update(f"{path_display} | Line: {editor.cursor_row + 1}, Col: {editor.cursor_col + 1}")
    
    def action_split_vertical(self) -> None:
        if not self.active_container_id:
            return
        
        main_container = self.query_one("#main-container", Horizontal)
        active_container = self.get_active_container()

        new_id = self.generate_container_id()
        new_container = EditorContainer(id=new_id)
        self.editors[new_id] = new_container

        main_container.main(new_container)

        self.set_active_container(new_id)
    
    def action_split_horizontal(self) -> None:
        if not self.active_container_id:
            return
        
        main_container = self.query_one("#main-container", Horizontal)
        active_container = self.get_active_container()
        active_index = list(self.editors.keys()).index(self.active_container_id)

        vertical_container = Vertical()

        active_container.remove()
        vertical_container.mount(active_container)

        new_id = self.generate_container_id()
        new_container = EditorContainer(id=new_id)
        self.editors[new_id] = new_container
        vertical_container.mount(new_container)

        main_container.mount(vertical_container)
        
        self.set_active_container(new_id)
    
    async def action_new_file(self) -> None:
        container_id = self.active_container_id
        if container_id:
            container = self.get_active_container()
            editor = container.query_one(Editor)

            if editor.is_modified:
                result = await self.push_screen(
                    FileDialog("Save changes?", editor.path or "", "save"),
                )
                if result:
                    await container.save_file(result)
            
            editor.text_content = ""
            editor.lines = [""]
            editor.path = None
            editor.cursor_row = 0
            editor.cursor_col = 0
            editor.is_modified = False
            editor.update_syntax()
    
    async def action_open_file(self) -> None:
        result = await self.push_screen(
            FileDialog("Open File", "", "open"),
        )

        if result and os.path.exists(result):
            container = self.get_active_container()
            if container:
                await container.load_file(result)
    
    async def action_save_file(self) -> None:
        container = self.get_active_container()
        if not container:
            return
        
        editor = container.query_one(Editor)

        if not editor.path:
            await self.action_save_as()
            return
        
        await container.save_file()
    
    async def action_save_as(self) -> None:
        container = self.get_active_container()
        if not container:
            return
        
        editor = container.query_one(Editor)

        result = await self.push_screen(
            FileDialog("Save As", editor.path or "", "save"),
        )

        if result:
            await container.save_file(result)
    
    def action_close_editor(self) -> None:
        if not self.active_container_id or len(self.editors) <= 1:
            return
        
        container = self.get_active_container()
        container_id = self.active_container_id

        del self.editors[container_id]

        new_active_id = next(iter(self.editors.keys()))
        self.set_active_container(new_active_id)

        container.remove()
    
    def action_focus_next(self) -> None:
        if not self.active_container_id or len(self.editors) <= 1:
            return
        
        editor_ids = list(self.editors.keys())
        current_index = editor_ids.index(self.active_container_id)
        next_index = (current_index + 1) % len(editor_ids)
        self.set_active_container(editor_ids[next_index])
    
    def action_quit(self) -> None:
        self.exit()
    
    def generate_container_id(self) -> str:
        existing_ids = list(self.editors.keys())
        for i in range(100):
            new_id = f"editor-{i}"
            if new_id not in existing_ids:
                return new_id
        return f"editor-{len(existing_ids)}"

    async def load_file_to_editor(self, path: str, container_id: str) -> None:
        container = self.query_one(f"#{container_id}", EditorContainer)
        await container.load_file(path)
    

def main(file_path: Optional[str]=None):
    app = Cedit(file_path)
    app.run()

if __name__ == "__main__":
    import sys
    file_path = sys.argv[1] if len(sys.argv) > 1 else None
    main(file_path)