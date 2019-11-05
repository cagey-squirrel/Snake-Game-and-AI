import pygame
import sys
import random


pygame.init()
WIDTH = 500
HEIGHT = 500
rows = 20
SIZE = WIDTH // rows
screen = pygame.display.set_mode((WIDTH, HEIGHT))
fps = pygame.time.Clock()
RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
run = True

class Cube(object):

    def __init__(self, position_x, position_y, direction_x, direction_y, color = RED):
        self.position_x = position_x
        self.position_y = position_y
        self.direction_x = direction_x
        self.direction_y = direction_y
        self.color = color

    def move(self):
        self.position_x, self.position_y = self.position_x + self.direction_x, self.position_y + self.direction_y

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.position_x * SIZE + 1, self.position_y * SIZE + 1, SIZE - 1, SIZE - 1))



class Snake(object):
    turns = []
    directions_for_turns = []

    def __init__(self):
        self.head = Cube(rows//2, rows//2, 1, 0, BLUE)
        self.body = []
        self.body.append(self.head)
        self.body.append(Cube(self.head.position_x - 1, self.head.position_y, 1, 0))
        self.body.append(Cube(self.head.position_x - 2, self.head.position_y, 1, 0))
        self.tail = self.body[-2]
        self.dead = False

    def move(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                sys.exit()

        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT]:
            turn_coordinate = (self.head.position_x, self.head.position_y)
            self.turns.append(turn_coordinate)
            self.head.direction_x = 1
            self.head.direction_y = 0
            self.head.direction = (self.head.direction_x, self.head.direction_y)
            self.directions_for_turns.append(self.head.direction)
        elif keys[pygame.K_LEFT]:
            turn_coordinate = (self.head.position_x, self.head.position_y)
            self.turns.append(turn_coordinate)
            self.head.direction_x = -1
            self.head.direction_y = 0
            self.head.direction = (self.head.direction_x, self.head.direction_y)
            self.directions_for_turns.append(self.head.direction)
        elif keys[pygame.K_UP]:
            turn_coordinate = (self.head.position_x, self.head.position_y)
            self.turns.append(turn_coordinate)
            self.head.direction_x = 0
            self.head.direction_y = -1
            self.head.direction = (self.head.direction_x, self.head.direction_y)
            self.directions_for_turns.append(self.head.direction)
        elif keys[pygame.K_DOWN]:
            turn_coordinate = (self.head.position_x, self.head.position_y)
            self.turns.append(turn_coordinate)
            self.head.direction_x = 0
            self.head.direction_y = 1
            self.head.direction = (self.head.direction_x, self.head.direction_y)
            self.directions_for_turns.append(self.head.direction)

        # print(self.turns)
        # print(self.directions_for_turns)
        
        for cube in self.body:
            cube.move()
            for i, turn in enumerate(self.turns):
                if (cube.position_x, cube.position_y) == self.turns[i]:
                    cube.direction_x, cube.direction_y = self.directions_for_turns[i]
                    if self.body.index(cube) == len(self.body) - 1:
                        self.turns.pop(i)
                        self.directions_for_turns.pop(i)



    def draw(self):
        for cube in self.body:
            cube.draw()

    def stack_collection(self, snack):
        if (self.head.position_x, self.head.position_y) == (snack.x, snack.y):
            self.tail = self.body[-1]
            if self.tail.direction_x == 1:
                self.body.append(Cube(self.tail.position_x - 1, self.tail.position_y, 1, 0))
            if self.tail.direction_x == -1:
                self.body.append(Cube(self.tail.position_x + 1, self.tail.position_y, -1, 0))
            if self.tail.direction_y == 1:
                self.body.append(Cube(self.tail.position_x, self.tail.position_y - 1, 0, 1))
            if self.tail.direction_y == -1:
                self.body.append(Cube(self.tail.position_x, self.tail.position_y + 1, 0, -1))
            snack.exists = False

    def bite_or_hit(self):
        if 0 > self.head.position_x or self.head.position_x > rows - 1 or 0 > self.head.position_y or self.head.position_y > rows - 1:
            self.dead = True
        for i, cube in enumerate(self.body):
            if (self.head.position_x, self.head.position_y) == (cube.position_x, cube.position_y) and i != 0:
                self.dead = True




class Snack(object):

    def __init__(self):
        self.x = 0
        self.y = 0
        self.exists = False
        self.matching = False


    def generator(self):
        if not self.exists:
            while True:
                self.x = random.randint(0, rows - 1)
                self.y = random.randint(0, rows - 1)
                for cube in snake.body:
                    if (self.x, self.y) == (cube.position_x, cube.position_y):
                        self.matching = True
                        break
                    else:
                        self.matching = False
                if self.matching:
                    continue
                else:
                    self.exists = True
                    break


    def draw(self):
        if self.exists:
            pygame.draw.rect(screen, GREEN, (self.x * SIZE + 1, self.y * SIZE + 1, SIZE - 1, SIZE - 1))

snack = Snack()
snake = Snake()

def draw_grid():
    x = 0
    y = 0
    for i in range(rows):
        x += SIZE
        y += SIZE

        pygame.draw.line(screen, WHITE, (x, 0), (x, HEIGHT))
        pygame.draw.line(screen, WHITE, (0, y), (WIDTH, y))

def draw(snake, snack):
    screen.fill(BLACK)
    draw_grid()
    snack.draw()
    snake.draw()

    pygame.display.update()

while run:

    snake.stack_collection(snack)
    snack.generator()
    snake.move()
    snake.bite_or_hit()
    



    if snake.dead:
        snake.directions_for_turns.clear()
        snake.turns.clear()
        snake = Snake()

    draw(snake, snack)
    pygame.time.delay(50)
    fps.tick(10)
