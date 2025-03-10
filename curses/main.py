#!/usr/bin/env python3
import curses
import os
import pyperclip
import sys
from curses.textpad import Textbox, rectangle
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import Terminal256Formatter
from pygments.styles import get_style_by_name


class Cedit:
    def __init__(self, stdscr, filename="example.py"):
        self.filepath = filename

        self.content = []
        self.cursor_x = 0
        self.cursor_y = 0
        self.scroll_y = 0
        self.scroll_x = 0
        self.height, self.width = stdscr.getmaxyx()
        self.selection_start = None
        self.clipboard = ""
        self.message = ""
        self.message_timeout = 0

        curses.start_color()
        curses.use_default_colors()
        for i in range(0, curses.COLORS):
            curses.init_pair(i + 1, i - 1)
        
        if filename:
            self.load_file(filename)
        else:
            self.content = [""]
    
    def load_file(self, filename):
        try:
            with open(filename, "r") as f:
                self.content = f.read().splitlines()
                if not self.content:
                    self.content = [""]
        except FileNotFoundError:
            self.content = [""]
            self.set_message(f"New file: {filename}")
        except Exception as e:
            self.content = [""]
            self.set_message(f"Error loading file: {str(e)}")
    
    def save_file(self, filename="example.py"):
        if filename:
            self.filename = filename
        
        if not self.filename:
            self.set_message("No filename specified")
            return False
        
        try:
            with open(self.filename, "w") as f:
                f.write("\n".join(self.content))
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
        cursor_y, cursor_x = self.cursor_y, self.cursor_x

        self.stdscr.move(self.height - 1, 0)
        self.stdscr.clrtoeol()
        prompt = f"{action} file: "
        self.stdscr.addstr(self.height - 1, 0, prompt)

        curses.echo()
        filename = self.stdscr.getstr(self.height - 1, len(prompt)).decode("utf-8")
        curses.noecho()

        self.cursor_y, self.cursor_x = cursor_y, cursor_x

        return filename if filename else None
    
    def handle_input(self, key):
        if key == curses.KEY_RESIZE:
            self.height, self.width = self.stdscr.getmaxyx()
            return
        
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
        elif key == curses.KEY_PPAGE:
            self.move_cursor(-self.height + 2, 0)
        elif key == curses.KEY_NPAGE:
            self.move_cursor(self.height - 2, 0)
        elif key == 10:
            current_line = self.content[self.cursor_y]
            self.content[self.cursor_y] = current_line[:self.cursor_x]
            self.content.insert(self.cursor_y + 1, current_line[self.cursor_x:])
            self.cursor_y += 1
            self.cursor_x = 0
        elif key == 9:
            self.insert_text("  ")
        elif key == 127 or key == curses.KEY_BACKSPACE:
            if self.cursor_x > 0:
                current_line = self.content[self.cursor_y]
                self.content[self.cursor_y] = current_line[:self.cursor_x - 1] + current_line[self.cursor_x:]
                self.cursor_x -= 1
            elif self.cursor_y > 0:
                self.cursor_x = len(self.content[self.cursor_y - 1])
                self.content[self.cursor_y - 1] += self.content[self.cursor_y]
                self.content.pop(self.cursor_y)
                self.cursor_y -= 1
        elif key == curses.KEY_DC:
            if self.cursor_x < len(self.content[self.cursor_y]):
                current_line = self.content[self.cursor_y]
                self.content[self.cursor_y] = current_line[:self.cursor_x] + current_line[self.cursor_x + 1:]
            elif self.cursor_y < len(self.content) - 1:
                self.content[self.cursor_y] += self.content[self.cursor_y + 1]
                self.content.pop(self.cursor_y + 1)
        elif key == curses.KEY_SR or key == curses.KEY_SF:
            if self.selection_start is None:
                self.selection_start = (self.cursor_y, self.cursor_x)
            if key == curses.KEY_SR:
                self.move_cursor(-1, 0)
            else:
                self.move_cursor(1, 0)
        elif key == 19:
            self.save_file()
        elif key == 15:
            filename = self.prompt_filename("Open")
            if filename:
                self.filename = filename
                self.load_file(filename)
        elif key == 14:
            self.new_file()
        elif key == 3:
            self.copy_text()
        elif key == 22:
            self.paste_text()
        elif key == 27:
            self.selection_start = None
        elif 32 <= key <= 126:
            self.insert_text(chr(key))
    
    def insert_text(self, text):
        current_line = self.content[self.cursor_y]
        self.content[self.cursor_y] = current_line[:self.cursor_x] + text + current_line[self.cursor_x:]
        self.cursor_x += len(text)
    
    def move_cursor(self, dy, dx):
        if dy != 0:
            new_y = max(0, min(len(self.content) - 1, self.cursor_y + dy))
            if new_y != self.cursor_y:
                self.cursor_y = new_y
                self.cursor_x = min(self.cursor_x, len(self.content[self.cursor_y]))
        if dx != 0:
            if dx < 0 and self.cursor_x == 0 and self.cursor_y > 0:
                self.cursor_y -= 1
                self.cursor_x = len(self.content[self.cursor_y])
            elif dx > 0 and self.cursor_x == len(self.content[self.cursor_y]) and self.cursor_y < len(self.content) - 1:
                self.cursor_y += 1
                self.cursor_x = 0
            else:
                self.cursor_x = max(0, min(len(self.content[self.cursor_y]), self.cursor_x + dx))
        self.update_scroll()
    
    def update_scroll(self):
        if self.cursor_y < self.scroll_y:
            self.scroll_y = self.cursor_y
        elif self.cursor_y >= self.scroll_y + self.height - 2:
            self.scroll_y = self.cursor_y - self.height + 3

    def main(self, stdscr):
        stdscr.clear()

        height, width = stdscr.getmaxyx()

        title = "cedit"
        half_t = len(title) // 2
        half_w = width // 2
        new_title = " " * (half_w - half_t)
        new_title += title
        new_title += " " * (half_w + half_t - 5)

        curses.start_color()
        if curses.can_change_color():
            curses.init_color(10, 407, 0, 141)
        
        curses.init_pair(1, 10, curses.COLOR_WHITE)
        stdscr.addstr(0, 0, new_title, curses.color_pair(1) | curses.A_STANDOUT)

        pady, padx = 2, 2
        winh, winw, winy, winx = height-6, width -4, 4, 2

        editwin = curses.newwin(winh, winw, winy, winx)
        rectangle(stdscr, winy-1, winx-1, winy+winh, winx+winw)

        rectangle(stdscr, 1, 1, 3, len(self.filepath) + 4)
        stdscr.addstr(2, 3, f"{self.filepath}", curses.A_ITALIC)

        stdscr.addstr(height - 1, 0, "ctrl-n (new file)    ctrl-o (open file)    ctrl-s (save file)", curses.A_DIM)

        stdscr.refresh()

        box = Textbox(editwin)

        editwin.addstr(f"w={width}, h={height}")
        editwin.refresh()

        box.edit()

    def run(self):
        curses.wrapper(self.main)


if __name__ == "__main__":
    cedit = Cedit()
    cedit.run()
