import curses
import time
from abc import ABC, abstractmethod
from curses import window, wrapper


class Vector:
    """Represents a 2D vector or point."""

    def __init__(self, y: int, x: int):
        self.y = y
        self.x = x

    def __add__(self, other):
        if isinstance(other, Vector):
            return Vector(self.y + other.y, self.x + other.x)
        else:
            raise TypeError("Can only add Vector objects")


class Position(Vector):
    """Represents a position in 2D space."""

    pass


class Score:
    """Displays a single-digit score at a given position."""

    NUMS = [
        ("███", "█ █", "█ █", "█ █", "███"),  # 0
        ("  █", "  █", "  █", "  █", "  █"),  # 1
        ("███", "  █", "███", "█  ", "███"),  # 2
        ("███", "  █", "███", "  █", "███"),  # 3
        ("█ █", "█ █", "███", "  █", "  █"),  # 4
        ("███", "█  ", "███", "  █", "███"),  # 5
        ("███", "█  ", "███", "█ █", "███"),  # 6
        ("███", "  █", "  █", "  █", "  █"),  # 7
        ("███", "█ █", "███", "█ █", "███"),  # 8
        ("███", "█ █", "███", "  █", "███"),  # 9
    ]

    def __init__(self, y: int, x: int):
        self.pos = Position(y, x)

    def draw(self, screen: window, score: int):
        if score < 0 or score > 9:
            score = 9

        for idx, seg in enumerate(self.NUMS[score]):
            try:
                screen.addstr(self.pos.y + idx, self.pos.x, seg)
            except curses.error:
                pass


class Entity(ABC):
    """Abstract base class for all game entities."""

    def __init__(self, y: int, x: int):
        self.pos = Position(y, x)

    @abstractmethod
    def draw(self, screen: window):
        """Draw the entity on the given screen."""
        pass

    def iscolliding(self, other: "Entity") -> bool:
        """Checks collision AABB (Axis-Aligned Bounding Box)"""
        return (
            self.pos.x < other.pos.x + other.width
            and self.pos.x + self.width > other.pos.x
            and self.pos.y < other.pos.y + other.height
            and self.pos.y + self.height > other.pos.y
        )


class Wall(Entity):
    """Horizontal wall on top or bottom of the screen."""

    height = 1

    def __init__(self, y: int, x: int, width: int):
        super().__init__(y, x)
        self.width = width

    def draw(self, screen: window):
        try:
            screen.hline(self.pos.y, self.pos.x, curses.ACS_HLINE, self.width)
        except curses.error:
            pass


class Goal(Entity):
    """Goal area (invisible) on left or right side of the screen."""

    width = 1

    def __init__(self, y: int, x: int, height: int):
        super().__init__(y, x)
        self.height = height

    def draw(self, _: window):
        pass


class Ball(Entity):
    """Game ball"""

    width = 1
    height = 1

    def __init__(self, y: int, x: int):
        super().__init__(y, x)
        self.vel = Vector(-1, 1)

    def draw(self, screen: window):
        try:
            screen.addstr(self.pos.y, self.pos.x, "⬤")
        except curses.error:
            pass

    def move(self):
        """Move the ball according to its velocity."""
        self.pos += self.vel

    def bouncex(self):
        """Invert the x component of the velocity."""
        self.vel.x *= -1

    def bouncey(self):
        """Invert the y component of the velocity."""
        self.vel.y *= -1


class Character(Entity):
    """Base class for player and enemy characters."""

    width = 1
    height = 5

    def __init__(self, y: int, x: int):
        super().__init__(y, x)
        self.score = 0

    def move(self, dy: int):
        """Move the character vertically."""
        self.pos.y += dy

    def draw(self, screen: window):
        for i in range(self.height):
            try:
                screen.addstr(self.pos.y + i, self.pos.x, "█")
            except curses.error:
                pass


class Player(Character):
    """Player character controlled by the user."""

    pass


class Enemy(Character):
    def searchball(self, ball: Ball, twall: Wall, bwall: Wall):
        if ball.vel.x < 0:
            return
        if ball.pos.y < self.pos.y:
            if not self.iscolliding(twall):
                self.move(-1)
        elif ball.pos.y > self.pos.y + self.height:
            if not self.iscolliding(bwall):
                self.move(+1)


class Game:
    """Main game class."""

    screen: window

    FPS = 30
    TICK = 1 / FPS

    def __init__(self):
        self.running = True
        self.rows = 0
        self.cols = 0

    def init(self):
        """Initializes the game state."""
        curses.curs_set(0)  # Hide cursor
        self.screen.nodelay(True)  # Non-blocking input

        self.rows, self.cols = self.screen.getmaxyx()
        self.center = Position(self.rows // 2, self.cols // 2)

        self.player = Player(self.center.y - 2, 3)
        self.enemy = Enemy(self.center.y - 2, self.cols - 4)

        self.ball = Ball(self.center.y, self.center.x)

        self.walls = [
            Wall(0, 0, self.cols),  # Top wall
            Wall(self.rows - 1, 0, self.cols),  # Bottom wall
        ]

        self.goals = [
            Goal(1, 0, self.rows - 1),  # Left goal
            Goal(1, self.cols - 1, self.rows - 1),  # Right goal
        ]

        self.scoreboard = {
            "player": Score(2, self.center.x // 2),
            "enemy": Score(2, self.center.x + self.center.x // 2),
        }

    def main(self, stdscr: window):
        """Main game loop."""
        self.screen = stdscr
        self.init()

        while self.running:
            time.sleep(self.TICK)

            # 1. Process Input
            ch = self.screen.getch()
            self.procinput(ch)

            # 2. Update Game State
            self.update()

            # 3. Render
            self.draw()

    def procinput(self, ch: int):
        """Process user input."""
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

    def resetball(self):
        """Resets the ball to the center of the screen."""
        self.ball = Ball(self.center.y, self.center.x)

    def update(self):
        """Update the game state."""
        if self.ball.iscolliding(self.goals[0]):
            self.enemy.score += 1
            self.ball = Ball(self.center.y, self.center.x)
            return

        if self.ball.iscolliding(self.goals[1]):
            self.player.score += 1
            self.ball = Ball(self.center.y, self.center.x)
            return

        if any(self.ball.iscolliding(wall) for wall in self.walls):
            self.ball.bouncey()

        if self.ball.iscolliding(self.player):
            self.ball.bouncex()

        if self.ball.iscolliding(self.enemy):
            self.ball.bouncex()

        self.ball.move()

        self.enemy.searchball(self.ball, self.walls[0], self.walls[1])

    def draw(self):
        """Render the game state to the screen."""
        self.screen.erase()

        try:
            self.screen.vline(0, self.center.x, curses.ACS_BLOCK, self.rows)
        except curses.error:
            pass

        self.scoreboard["player"].draw(self.screen, self.player.score)
        self.scoreboard["enemy"].draw(self.screen, self.enemy.score)

        for wall in self.walls:
            wall.draw(self.screen)

        self.player.draw(self.screen)
        self.enemy.draw(self.screen)

        self.ball.draw(self.screen)

        self.screen.refresh()


if __name__ == "__main__":
    wrapper(Game().main)
