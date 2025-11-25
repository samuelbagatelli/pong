import curses
import time
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
            raise TypeError("Can only add Vector objects to a Position")


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

    def move(self, y: int, lbnd: int):
        if self.pos.y + y < 0:
            self.pos.y = 0
        elif self.pos.y + y + self.LENGTH > lbnd:
            self.pos.y = lbnd - self.LENGTH
        else:
            self.pos.y += y

    def draw(self, screen: window):
        for i in range(self.LENGTH):
            screen.addstr(self.pos.y + i, self.pos.x, "█")


class Player(Character):
    pass


class ScoreException(Exception):
    def __init__(self, xpos):
        self.xpos = xpos
        super().__init__("Ball out")


def iswall(pos: Position, rows: int):
    return pos.y == 0 or pos.y == rows


class Ball:
    def __init__(self, y: int, x: int):
        self.pos = Position(y, x)
        self.vel = Vector(-1, 1)

    def draw(self, screen: window):
        screen.addstr(self.pos.y, self.pos.x, "⬤")

    def move(self, rows: int):
        new = self.pos + self.vel
        if iswall(new, rows):
            self.bounce()
        else:
            try:
                self.pos = new
            except curses.error:
                raise ScoreException(self.pos.x)

    def accelerate(self, velocity: int):
        self.vel += velocity

    def stop(self):
        self.vel = 0

    def bounce(self):
        self.vel.y *= -1


class Game:
    screen: window
    rows: int
    cols: int

    def __init__(self):
        self.running = True

    def init(self):
        curses.curs_set(0)
        self.screen.nodelay(True)

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
            time.sleep(1 / 10)

            self.draw()
            try:
                self.ball.move(self.rows)
            except ScoreException:
                pass

            ch = self.screen.getch()
            self.procinput(ch)

    def procinput(self, ch):
        if ch in (ord("q"), ord("Q")):
            self.running = False

        if ch == curses.KEY_UP:
            self.player.move(-1, self.rows)
        if ch == curses.KEY_DOWN:
            self.player.move(+1, self.rows)


wrapper(Game().main)
