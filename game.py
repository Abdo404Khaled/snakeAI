import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()
font = pygame.font.Font('Graphics/arial.ttf', 25)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4


Point = namedtuple('Point', 'x, y')

# rgb colors
GREEN = (173, 204, 96)
DARK_GREEN = (43, 51, 24)
GRAY = (128, 128, 128)

BLOCK_SIZE = 20
SPEED = 40

OFFSET = 75  # Offset for the frame

FOOD_SURFACE = pygame.transform.scale(pygame.image.load("Graphics/apple.png"), (BLOCK_SIZE, BLOCK_SIZE))

class SnakeGameAI:

    def __init__(self, w=640, h=480):
        self.w = w + 2 * OFFSET  # Adding offset to width
        self.h = h + 2 * OFFSET  # Adding offset to height
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        # init game state
        self.direction = Direction.RIGHT

        self.head = Point(self.w / 2, self.h / 2)
        self.snake = [self.head,
                      Point(self.head.x - BLOCK_SIZE, self.head.y),
                      Point(self.head.x - (2 * BLOCK_SIZE), self.head.y)]

        self.score = 0
        self.food = None
        self._place_food()
        self.frame_iteration = 0

    def _place_food(self):
        x = random.randint(0, (self.w - 2 * OFFSET - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE + OFFSET
        y = random.randint(0, (self.h - 2 * OFFSET - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE + OFFSET
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()

    def play_step(self, action):
        self.frame_iteration += 1
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # 2. move
        self._move(action)  # update the head
        self.snake.insert(0, self.head)

        # 3. check if game over
        reward = 0
        game_over = False
        if self.is_collision() or self.frame_iteration > 100 * len(self.snake):
            game_over = True
            reward = -10
            return reward, game_over, self.score

        # 4. place new food or just move
        if self.head == self.food:
            self.score += 1
            reward = 10
            self._place_food()
        else:
            self.snake.pop()

        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)
        # 6. return game over and score
        return reward, game_over, self.score

    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head
        # hits boundary
        if pt.x >= self.w - OFFSET or pt.x < OFFSET or pt.y >= self.h - OFFSET or pt.y < OFFSET:
            return True
        # hits itself
        if pt in self.snake[1:]:
            return True

        return False

    def _update_ui(self):
        self.display.fill(GREEN)
        FRAME_SIZE = (OFFSET - 5, OFFSET - 5, (BLOCK_SIZE * ((self.w - 2 * OFFSET)//BLOCK_SIZE)) + 10, (BLOCK_SIZE * ((self.h - 2 * OFFSET)//BLOCK_SIZE)) + 10)
        pygame.draw.rect(self.display, DARK_GREEN, FRAME_SIZE, 5)

        segment_rect = pygame.Rect(self.snake[0].x, self.snake[0].y, BLOCK_SIZE, BLOCK_SIZE)
        pygame.draw.rect(self.display, DARK_GREEN, segment_rect, 0, 10)

        for segment in self.snake[1:]:
            segment_rect = pygame.Rect(segment.x, segment.y, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(self.display, DARK_GREEN, segment_rect, 0, 7)

        for x in range(OFFSET, self.w - OFFSET, BLOCK_SIZE):
            for y in range(OFFSET, self.h - OFFSET, BLOCK_SIZE):
                rect = pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE)
                pygame.draw.rect(self.display, GRAY, rect, 1)

        self.display.blit(FOOD_SURFACE, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))

        text = font.render("Retro Snake", True, DARK_GREEN)
        self.display.blit(text, (OFFSET - 5, 40))

        text = font.render("Score: " + str(self.score), True, DARK_GREEN)
        self.display.blit(text, (OFFSET - 5, OFFSET + BLOCK_SIZE * ((self.h - (2 * OFFSET)) // BLOCK_SIZE) + 10))
        pygame.display.flip()

    def _move(self, action):
        # [straight, right, left]
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx]  # no change
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx]  # right turn r -> d -> l -> u
        else:  # [0, 0, 1]
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx]  # left turn r -> u -> l -> d

        self.direction = new_dir

        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head = Point(x, y)