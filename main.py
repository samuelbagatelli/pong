import curses
from curses import window, wrapper


class Vector:
    def __init__(self, y: int, x: int):
        self.y = y
        self.x = x


class Position(Vector):
    def __add__(self, other):
        if isinstance(other, Vector):
            y, x = self.y + other.y, self.x + other.x
            if y < 0 or x < 0:
                raise ValueError("Position cannot be negative")

            return Position(y, x)
        else:
            raise TypeError(
                "Can only add Vector objects (and it's children) to a Position"
            )


class Score:
    NUMS = [
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

    def __init__(self, y: int, x: int):
        self.pos = Vector(y, x)

    def draw(self, screen: window, score: int):
        if 9 < score < 0:
            raise ValueError("Score must be between 0 and 9")

        for idx, seg in enumerate(self.NUMS[score]):
            screen.addstr(self.pos.y + idx, self.pos.x, seg)


class Character:
    LENGTH = 5

    def __init__(self, y: int, x: int):
        self.pos = Vector(y, x)
        self.score = 0

    def move(self, y: int):
        self.pos.y += y

    def draw(self, screen: window):
        for i in range(self.LENGTH):
            screen.addstr(self.pos.y + i, self.pos.x, "█")


class Player(Character):
    pass


class OutOfBoundsError(Exception):
    def __init__(self, message="Ball is out of bounds"):
        super().__init__(message)


class Ball:
    def __init__(self, y: int, x: int):
        self.pos = Position(y, x)
        self.vel = Vector(0, 0)

    def draw(self, screen: window):
        screen.addstr(self.pos.y, self.pos.x, "⬤")

    def move(self):
        try:
            self.pos += self.vel
        except ValueError:
            raise OutOfBoundsError()


class Game:
    screen: window
    rows: int
    cols: int

    def __init__(self):
        self.running = True

    def init(self):
        curses.curs_set(0)

        self.rows, self.cols = self.screen.getmaxyx()

        self.center = Vector(self.rows // 2, self.cols // 2)

        self.player = Player(self.center.y - 2, 3)
        self.ball = Ball(self.center.y, 5)

        self.scoreboard = [
            Score(3, self.center.x // 2),
            Score(3, self.center.x + self.center.x // 2),
        ]

    def draw(self):
        self.screen.clear()

        # ===== player =====
        self.player.draw(self.screen)

        # ===== scoreboard =====
        self.scoreboard[0].draw(self.screen, self.player.score)
        self.scoreboard[1].draw(self.screen, self.player.score)

        # ===== divider =====
        self.screen.vline(0, self.center.x, curses.ACS_BLOCK, self.rows)

        # ===== ball =====
        self.ball.draw(self.screen)

        self.screen.refresh()

    def main(self, stdscr):
        self.screen = stdscr

        self.init()

        while self.running:
            self.draw()

            ch = self.screen.getch()
            self.procinput(ch)

    def procinput(self, ch):
        if ch in (ord("q"), ord("Q")):
            self.running = False

        if ch == curses.KEY_UP:
            self.player.move(-1)
        if ch == curses.KEY_DOWN:
            self.player.move(+1)


wrapper(Game().main)
