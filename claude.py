#!/usr/bin/env python3
import curses
import os
import sys
import pyperclip
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import Terminal256Formatter
from pygments.styles import get_style_by_name

class TextEditor:
    def __init__(self, stdscr, filename=None):
        self.stdscr = stdscr
        self.filename = filename
        self.content = []
        self.cursor_y = 0
        self.cursor_x = 0
        self.scroll_y = 0
        self.scroll_x = 0
        self.height, self.width = stdscr.getmaxyx()
        self.selection_start = None
        self.clipboard = ""
        self.message = ""
        self.message_timeout = 0
        
        # Initialize colors
        curses.start_color()
        curses.use_default_colors()
        for i in range(0, curses.COLORS):
            curses.init_pair(i + 1, i, -1)
            
        # Load file if provided
        if filename:
            self.load_file(filename)
        else:
            self.content = [""]
            
    def load_file(self, filename):
        try:
            with open(filename, 'r') as f:
                self.content = f.read().splitlines()
                if not self.content:
                    self.content = [""]
        except FileNotFoundError:
            self.content = [""]
            self.set_message(f"New file: {filename}")
        except Exception as e:
            self.content = [""]
            self.set_message(f"Error loading file: {str(e)}")
            
    def save_file(self, filename=None):
        if filename:
            self.filename = filename
        
        if not self.filename:
            self.set_message("No filename specified")
            return False
            
        try:
            with open(self.filename, 'w') as f:
                f.write('\n'.join(self.content))
            self.set_message(f"Saved: {self.filename}")
            return True
        except Exception as e:
            self.set_message(f"Error saving file: {str(e)}")
            return False
            
    def set_message(self, message, timeout=50):
        self.message = message
        self.message_timeout = timeout
            
    def new_file(self):
        self.filename = None
        self.content = [""]
        self.cursor_y = 0
        self.cursor_x = 0
        self.scroll_y = 0
        self.scroll_x = 0
        self.set_message("New file")
        
    def prompt_filename(self, action):
        # Save current cursor position
        cursor_y, cursor_x = self.cursor_y, self.cursor_x
        
        # Display prompt
        self.stdscr.move(self.height - 1, 0)
        self.stdscr.clrtoeol()
        prompt = f"{action} file: "
        self.stdscr.addstr(self.height - 1, 0, prompt)
        
        # Get input
        curses.echo()
        filename = self.stdscr.getstr(self.height - 1, len(prompt)).decode('utf-8')
        curses.noecho()
        
        # Restore cursor
        self.cursor_y, self.cursor_x = cursor_y, cursor_x
        
        return filename if filename else None
        
    def handle_input(self, key):
        if key == curses.KEY_RESIZE:
            self.height, self.width = self.stdscr.getmaxyx()
            return
            
        # Standard navigation
        if key == curses.KEY_UP:
            self.move_cursor(-1, 0)
        elif key == curses.KEY_DOWN:
            self.move_cursor(1, 0)
        elif key == curses.KEY_LEFT:
            self.move_cursor(0, -1)
        elif key == curses.KEY_RIGHT:
            self.move_cursor(0, 1)
        elif key == curses.KEY_HOME:
            self.cursor_x = 0
        elif key == curses.KEY_END:
            self.cursor_x = len(self.content[self.cursor_y])
        elif key == curses.KEY_PPAGE:  # Page Up
            self.move_cursor(-self.height + 2, 0)
        elif key == curses.KEY_NPAGE:  # Page Down
            self.move_cursor(self.height - 2, 0)
            
        # Editing
        elif key == 10:  # Enter
            # Split the line at cursor
            current_line = self.content[self.cursor_y]
            self.content[self.cursor_y] = current_line[:self.cursor_x]
            self.content.insert(self.cursor_y + 1, current_line[self.cursor_x:])
            self.cursor_y += 1
            self.cursor_x = 0
        elif key == 9:  # Tab
            # Insert 4 spaces
            self.insert_text("    ")
        elif key == 127 or key == curses.KEY_BACKSPACE:  # Backspace
            if self.cursor_x > 0:
                current_line = self.content[self.cursor_y]
                self.content[self.cursor_y] = current_line[:self.cursor_x-1] + current_line[self.cursor_x:]
                self.cursor_x -= 1
            elif self.cursor_y > 0:
                # Join with previous line
                self.cursor_x = len(self.content[self.cursor_y-1])
                self.content[self.cursor_y-1] += self.content[self.cursor_y]
                self.content.pop(self.cursor_y)
                self.cursor_y -= 1
        elif key == curses.KEY_DC:  # Delete
            if self.cursor_x < len(self.content[self.cursor_y]):
                current_line = self.content[self.cursor_y]
                self.content[self.cursor_y] = current_line[:self.cursor_x] + current_line[self.cursor_x+1:]
            elif self.cursor_y < len(self.content) - 1:
                # Join with next line
                self.content[self.cursor_y] += self.content[self.cursor_y+1]
                self.content.pop(self.cursor_y+1)
        
        # Selection
        elif key == curses.KEY_SR or key == curses.KEY_SF:  # Shift+Up/Down
            if self.selection_start is None:
                self.selection_start = (self.cursor_y, self.cursor_x)
            
            if key == curses.KEY_SR:  # Shift+Up
                self.move_cursor(-1, 0)
            else:  # Shift+Down
                self.move_cursor(1, 0)
                
        # Control commands using control characters
        elif key == 19:  # Ctrl+S
            self.save_file()
        elif key == 15:  # Ctrl+O
            filename = self.prompt_filename("Open")
            if filename:
                self.filename = filename
                self.load_file(filename)
        elif key == 14:  # Ctrl+N
            self.new_file()
        elif key == 3:  # Ctrl+C
            self.copy_text()
        elif key == 22:  # Ctrl+V
            self.paste_text()
        elif key == 27:  # Escape
            self.selection_start = None
            
        # Default - insert character
        elif 32 <= key <= 126:  # Printable characters
            self.insert_text(chr(key))
            
    def insert_text(self, text):
        current_line = self.content[self.cursor_y]
        self.content[self.cursor_y] = current_line[:self.cursor_x] + text + current_line[self.cursor_x:]
        self.cursor_x += len(text)
            
    def move_cursor(self, dy, dx):
        if dy != 0:
            # Move up/down
            new_y = max(0, min(len(self.content) - 1, self.cursor_y + dy))
            if new_y != self.cursor_y:
                self.cursor_y = new_y
                self.cursor_x = min(self.cursor_x, len(self.content[self.cursor_y]))
                
        if dx != 0:
            # Move left/right
            if dx < 0 and self.cursor_x == 0 and self.cursor_y > 0:
                # Move to end of previous line
                self.cursor_y -= 1
                self.cursor_x = len(self.content[self.cursor_y])
            elif dx > 0 and self.cursor_x == len(self.content[self.cursor_y]) and self.cursor_y < len(self.content) - 1:
                # Move to start of next line
                self.cursor_y += 1
                self.cursor_x = 0
            else:
                # Move within line
                self.cursor_x = max(0, min(len(self.content[self.cursor_y]), self.cursor_x + dx))
                
        # Update scroll if needed
        self.update_scroll()
        
    def update_scroll(self):
        # Vertical scrolling
        if self.cursor_y < self.scroll_y:
            self.scroll_y = self.cursor_y
        elif self.cursor_y >= self.scroll_y + self.height - 2:
            self.scroll_y = self.cursor_y - self.height + 3
            
        # Horizontal scrolling
        if self.cursor_x < self.scroll_x:
            self.scroll_x = self.cursor_x
        elif self.cursor_x >= self.scroll_x + self.width - 2:
            self.scroll_x = self.cursor_x - self.width + 3
            
    def get_selected_text(self):
        if self.selection_start is None:
            return ""
            
        start_y, start_x = self.selection_start
        end_y, end_x = self.cursor_y, self.cursor_x
        
        # Ensure start is before end
        if start_y > end_y or (start_y == end_y and start_x > end_x):
            start_y, start_x, end_y, end_x = end_y, end_x, start_y, start_x
        
        selected_text = []
        for y in range(start_y, end_y + 1):
            line = self.content[y]
            if start_y == end_y:
                selected_text.append(line[start_x:end_x])
            elif y == start_y:
                selected_text.append(line[start_x:])
            elif y == end_y:
                selected_text.append(line[:end_x])
            else:
                selected_text.append(line)
                
        return '\n'.join(selected_text)
        
    def copy_text(self):
        selected_text = self.get_selected_text()
        if selected_text:
            try:
                pyperclip.copy(selected_text)
                self.set_message("Text copied to clipboard")
            except Exception as e:
                self.set_message(f"Failed to copy: {str(e)}")
                
    def paste_text(self):
        try:
            text = pyperclip.paste()
            if text:
                lines = text.split('\n')
                if len(lines) == 1:
                    self.insert_text(text)
                else:
                    # Handle multi-line paste
                    current_line = self.content[self.cursor_y]
                    first_part = current_line[:self.cursor_x]
                    last_part = current_line[self.cursor_x:]
                    
                    # Replace current line with first line of pasted text
                    self.content[self.cursor_y] = first_part + lines[0]
                    
                    # Insert middle lines
                    for i, line in enumerate(lines[1:-1], 1):
                        self.content.insert(self.cursor_y + i, line)
                        
                    # Add last line of pasted text + remainder of current line
                    self.content.insert(self.cursor_y + len(lines) - 1, lines[-1] + last_part)
                    
                    # Update cursor position
                    self.cursor_y += len(lines) - 1
                    self.cursor_x = len(lines[-1])
                self.set_message("Text pasted from clipboard")
        except Exception as e:
            self.set_message(f"Failed to paste: {str(e)}")
                
    def render(self):
        self.stdscr.clear()
        
        # Calculate visible lines
        visible_lines = min(self.height - 2, len(self.content) - self.scroll_y)
        
        # Combine all visible lines for syntax highlighting
        visible_content = '\n'.join(self.content[self.scroll_y:self.scroll_y + visible_lines])
        
        # Apply syntax highlighting
        if self.filename and self.filename.endswith('.py'):
            try:
                # Apply Python syntax highlighting
                style = get_style_by_name('monokai')
                formatter = Terminal256Formatter(style=style)
                highlighted = highlight(visible_content, PythonLexer(), formatter)
                highlighted_lines = highlighted.splitlines()
            except Exception:
                # Fall back to no highlighting on error
                highlighted_lines = visible_content.splitlines()
        else:
            # No syntax highlighting for non-Python files
            highlighted_lines = visible_content.splitlines()
            
        # Display lines with highlighting
        for i, line in enumerate(highlighted_lines):
            if i < visible_lines:
                try:
                    self.stdscr.addstr(i, 0, line[self.scroll_x:self.scroll_x + self.width - 1])
                except curses.error:
                    # End of screen reached
                    pass
        
        # Display status line
        status = f" {self.filename or 'Untitled'} - {len(self.content)} lines | Ln {self.cursor_y + 1}, Col {self.cursor_x + 1} "
        status = status + " " * (self.width - len(status) - 1)
        
        try:
            self.stdscr.attron(curses.A_REVERSE)
            self.stdscr.addstr(self.height - 2, 0, status[:self.width-1])
            self.stdscr.attroff(curses.A_REVERSE)
        except curses.error:
            # Handle potential errors when terminal is resized
            pass
            
        # Display message if any
        if self.message and self.message_timeout > 0:
            try:
                self.stdscr.addstr(self.height - 1, 0, self.message[:self.width-1])
                self.message_timeout -= 1
            except curses.error:
                pass
                
        # Position cursor
        try:
            self.stdscr.move(self.cursor_y - self.scroll_y, min(self.width - 1, self.cursor_x - self.scroll_x))
        except curses.error:
            # Handle potential errors when terminal is resized
            pass
            
        self.stdscr.refresh()
        
    def run(self):
        curses.curs_set(1)  # Show cursor
        curses.noecho()     # Don't echo keypresses
        self.stdscr.keypad(True)  # Enable special keys
        
        while True:
            self.render()
            
            try:
                key = self.stdscr.getch()
                
                # Check for exit (Ctrl+Q)
                if key == 17:  # Ctrl+Q
                    break
                    
                self.handle_input(key)
            except KeyboardInterrupt:
                break
                
def main(stdscr):
    # Setup terminal
    curses.raw()
    
    # Get filename from command line if provided
    filename = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Create and run editor
    editor = TextEditor(stdscr, filename)
    editor.run()

if __name__ == "__main__":
    try:
        # Initialize curses
        curses.wrapper(main)
    except Exception as e:
        # Clean up terminal in case of error
        curses.endwin()
        print(f"Error: {str(e)}")
        sys.exit(1)