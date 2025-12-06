import random

class SnakeGame:
    def __init__(self):
        self.snake = [(10, 10)]
        self.direction = "RIGHT"
        self.food = self._new_food()
        self.score = 0
        self.game_over = False

    def _new_food(self):
        return (random.randint(0, 19), random.randint(0, 19))

    def change_direction(self, d):
        opposites = {"UP":"DOWN","DOWN":"UP","LEFT":"RIGHT","RIGHT":"LEFT"}
        if opposites.get(self.direction) != d:
            self.direction = d

    def step(self):
        if self.game_over:
            return

        head_x, head_y = self.snake[0]

        if self.direction == "UP":
            head_y -= 1
        elif self.direction == "DOWN":
            head_y += 1
        elif self.direction == "LEFT":
            head_x -= 1
        elif self.direction == "RIGHT":
            head_x += 1

        new_head = (head_x, head_y)

        # Wall collision
        if head_x < 0 or head_x > 19 or head_y < 0 or head_y > 19:
            self.game_over = True
            return

        # Self collision
        if new_head in self.snake:
            self.game_over = True
            return

        self.snake.insert(0, new_head)

        # Food collision
        if new_head == self.food:
            self.score += 1
            self.food = self._new_food()
        else:
            self.snake.pop()

    def get_state(self):
        return {
            "snake": self.snake,
            "food": self.food,
            "score": self.score
        }
