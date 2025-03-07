import curses
from curses.textpad import Textbox, rectangle


class Cedit:
    def __init__(self):
        self.filepath = "example.txt"
        self.filepath_text = open(self.filepath, "r", encoding="utf-8").read()

        self.shortcuts = {
            19: "Ctrl-S pressed",
        }

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
