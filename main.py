import curses
import time
from curses import window, wrapper


def drawscore(stdscr: window, y: int, x: int, score: int):
    rep = [
        ("███", "█ █", "█ █", "█ █", "███"),
        ("  █", "  █", "  █", "  █", "  █"),
        ("███", "  █", "███", "█  ", "███"),
        ("███", "  █", "███", "  █", "███"),
        ("█ █", "█ █", "███", "  █", "  █"),
        ("███", "█  ", "███", "  █", "███"),
        ("███", "█  ", "███", "█ █", "███"),
        ("███", "  █", "  █", "  █", "  █"),
        ("███", "█ █", "███", "█ █", "███"),
        ("███", "█ █", "███", "  █", "███"),
    ]

    for idx, seg in enumerate(rep[score]):
        stdscr.addstr(y + idx, x, seg)

    stdscr.refresh()


def drawplyr(stdscr: window, y: int, x: int):
    for i in range(5):
        stdscr.addstr(y + i, x, "█")
    stdscr.refresh()


def drawsetup(stdscr: window, y: int, x: int):
    stdscr.clear()
    rows, cols = stdscr.getmaxyx()

    stdscr.border()

    # ==== scoreboard ====
    n = 0
    drawscore(stdscr, 1, cols // 4, n)
    drawscore(stdscr, 1, cols // 2 + cols // 4, n)

    # ==== middle div ====
    stdscr.vline(0, cols // 2, curses.ACS_BLOCK, rows)
    stdscr.refresh

    # ==== player ====
    drawplyr(stdscr, y, x)

    # ==== enemy ====
    drawplyr(stdscr, rows // 2 - 2, cols - 3)


def main(stdscr: window):
    curses.curs_set(0)

    rows, _ = stdscr.getmaxyx()
    y, x = rows // 2 - 2, 3

    while True:
        drawsetup(stdscr, y, x)

        ch = stdscr.getch()
        if ch in (ord("q"), ord("Q")):
            break
        if ch == curses.KEY_UP:
            y -= 1
        if ch == curses.KEY_DOWN:
            y += 1

        drawplyr(stdscr, y, x)


wrapper(main)
