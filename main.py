import curses
import time
from abc import abstractmethod
from curses import window, wrapper


class Vector:
    def __init__(self, y: int, x: int):
        self.y = y
        self.x = x

    def __add__(self, other):
        if isinstance(other, Vector):
            y, x = self.y + other.y, self.x + other.x
            if y < 0 or x < 0:
                raise ValueError("Position cannot be negative")

            return Position(y, x)
        else:
            raise TypeError("Can only add Vector objects to a Position")

    def __repr__(self):
        return f"({self.y}, {self.x})"


class Position(Vector):
    pass


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


class Entity:
    def __init__(self, y: int, x: int):
        self.pos = Position(y, x)

    @abstractmethod
    def move(self):
        raise NotImplementedError()

    @abstractmethod
    def iscolliding(self, other):
        raise NotImplementedError()

    @abstractmethod
    def draw(self, screen):
        raise NotImplementedError()


class Wall(Entity):
    height = 1

    def __init__(self, y, x, width):
        super().__init__(y, x)
        self.width = width

    def move(self):
        raise TypeError("Walls don't move")

    def draw(self, screen: window):
        screen.hline(self.pos.y, self.pos.x, curses.ACS_HLINE, self.width)


class Goal(Entity):
    width = 1

    def __init__(self, y, x, height):
        super().__init__(y, x)
        self.height = height

    def move(self):
        raise TypeError("Goals don't move")

    def draw(self, _: window):
        raise TypeError("Goals are invisible")


class Ball(Entity):
    size = 1

    def __init__(self, y: int, x: int):
        super().__init__(y, x)
        self.vel = Vector(-1, 1)

    def draw(self, screen: window):
        screen.addstr(self.pos.y, self.pos.x, "⬤")

    def move(self):
        self.pos += self.vel

    def accelerate(self, dv: int):
        self.vel += dv

    def stop(self):
        self.vel = Vector(0, 0)

    def bouncex(self):
        self.vel.x *= -1

    def bouncey(self):
        self.vel.y *= -1

    def iscolliding(self, other: Entity):
        return (
            self.pos.x <= other.pos.x + other.width
            and self.pos.x + self.size >= other.pos.x
            and self.pos.y <= other.pos.y + other.height
            and self.pos.y + self.size >= other.pos.y
        )


class Character(Entity):
    width = 1
    height = 5

    def __init__(self, y: int, x: int):
        super().__init__(y, x)
        self.score = 0

    def iscolliding(self, other: Entity):
        return (
            self.pos.x <= other.pos.x + other.width
            and self.pos.x + self.width >= other.pos.x
            and self.pos.y <= other.pos.y + other.height
            and self.pos.y + self.height >= other.pos.y
        )

    def move(self, dy: int):
        self.pos.y += dy

    def draw(self, screen: window):
        for i in range(self.height):
            screen.addstr(self.pos.y + i, self.pos.x, "█")


class Player(Character):
    pass


class Enemy(Character):
    def searchball(self, ball: Ball):
        if ball.vel.x < 0:
            return
        if ball.pos.y < self.pos.y:
            if not self.iscolliding(Wall(0, 0, 0)):
                self.move(-1)
        elif ball.pos.y > self.pos.y + self.height:
            if not self.iscolliding(Wall(20, 0, 0)):
                self.move(+1)


class ScoreException(Exception):
    def __init__(self, xpos):
        self.xpos = xpos
        super().__init__("Ball out")


class Game:
    screen: window
    rows: int
    cols: int

    TICK = 1 / 24

    def __init__(self):
        self.running = True

    def init(self):
        curses.curs_set(0)
        self.screen.nodelay(True)

        self.rows, self.cols = self.screen.getmaxyx()
        self.center = Position(self.rows // 2, self.cols // 2)

        self.player = Player(self.center.y - 2, 3)
        self.enemy = Enemy(self.center.y - 2, self.cols - 4)

        self.ball = Ball(self.center.y, 5)

        self.walls = [Wall(0, 0, self.cols), Wall(self.rows - 1, 0, self.cols)]
        self.goals = [
            Goal(1, 0, self.rows - 1),
            Goal(1, self.cols - 1, self.rows - 1),
        ]

        self.scoreboard = {
            "player": Score(2, self.center.x // 2),
            "enemy": Score(2, self.center.x + self.center.x // 2),
        }

    def main(self, stdscr):
        self.screen = stdscr

        self.init()

        while self.running:
            time.sleep(self.TICK)

            ch = self.screen.getch()
            self.procinput(ch)

            self.update()

            self.draw()

    def procinput(self, ch):
        if ch in (ord("q"), ord("Q")):
            self.running = False

        if ch == curses.KEY_UP:
            if self.player.iscolliding(self.walls[0]):
                return
            self.player.move(-1)
        if ch == curses.KEY_DOWN:
            if self.player.iscolliding(self.walls[1]):
                return
            self.player.move(+1)

    def update(self):
        if self.ball.iscolliding(self.goals[0]):
            self.enemy.score += 1
            self.ball = Ball(self.center.y, self.center.x)
            return

        if self.ball.iscolliding(self.goals[1]):
            self.player.score += 1
            self.ball = Ball(self.center.y, self.center.x)
            return

        if any([self.ball.iscolliding(wall) for wall in self.walls]):
            self.ball.bouncey()

        if self.ball.iscolliding(self.player):
            self.ball.bouncex()

        if self.ball.iscolliding(self.enemy):
            self.ball.bouncex()

        self.ball.move()

        self.enemy.searchball(self.ball)

    def draw(self):
        self.screen.clear()

        self.screen.vline(0, self.center.x, curses.ACS_BLOCK, self.rows)

        self.scoreboard["player"].draw(self.screen, self.player.score)
        self.scoreboard["enemy"].draw(self.screen, self.enemy.score)

        for wall in self.walls:
            wall.draw(self.screen)

        self.player.draw(self.screen)

        self.enemy.draw(self.screen)

        self.ball.draw(self.screen)

        self.screen.refresh()


wrapper(Game().main)
