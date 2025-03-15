import curses
from curses import wrapper

def main(stdscr):
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    title_win = curses.newwin(1, width, 0, 0)
    title_win.clear()
    stdscr.refresh()

    title_text = "cedit"
    title_left = " " * ((width // 2) - (len(title_text) // 2))
    title_right = " " * (width - len(title_left) - len(title_text))
    title = title_left + title_text + title_right

    title_win.addstr(title, curses.A_STANDOUT)
    title_win.refresh()
    stdscr.getch()

wrapper(main)