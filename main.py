import curses
from curses import window, wrapper


def drawbox(stdscr: window):
    rows, cols = stdscr.getmaxyx()
    top, bottom, left, right = 0, rows - 1, 0, cols - 1

    # ===== draw lines =====
    stdscr.hline(top, left + 1, curses.ACS_HLINE, cols - 2)
    stdscr.hline(bottom, left + 1, curses.ACS_HLINE, cols - 2)

    stdscr.vline(top + 1, left, curses.ACS_VLINE, rows - 2)
    stdscr.vline(top + 1, right, curses.ACS_VLINE, rows - 2)

    # ===== draw corners =====
    stdscr.addch(top, left, curses.ACS_ULCORNER)
    stdscr.addch(bottom, left, curses.ACS_LLCORNER)

    try:
        stdscr.addch(top, right, curses.ACS_URCORNER)
        stdscr.addch(bottom, right, curses.ACS_LRCORNER)
    except curses.error:
        pass

    stdscr.refresh()


def main(stdscr: window):
    stdscr.clear()
    curses.curs_set(0)

    drawbox(stdscr)

    while True:
        ch = stdscr.getch()
        if ch in (ord("q"), ord("Q")):
            break


wrapper(main)
