import pygame
import sys
import random
import neat
import os

pygame.init()
width = 800
WIDTH = 600
HEIGHT = 600
rows = 20
SIZE = WIDTH // rows
screen = pygame.display.set_mode((width, HEIGHT))
fps = pygame.time.Clock()
RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
biggest_length = 0
current_biggest_length = 0
generation = 0
lengths = []
myfont = pygame.font.SysFont('Calisto MT', 20)

class Cube(object):

    def __init__(self, position_x, position_y, direction_x, direction_y, color=RED):
        self.position_x = position_x
        self.position_y = position_y
        self.direction_x = direction_x
        self.direction_y = direction_y
        self.color = color

    def move(self):
        self.position_x, self.position_y = self.position_x + self.direction_x, self.position_y + self.direction_y

    def draw(self):
        pygame.draw.rect(screen, self.color,
                         (self.position_x * SIZE + 1, self.position_y * SIZE + 1, SIZE - 1, SIZE - 1))


class Snake(object):

    def __init__(self):
        self.body = []

        self.direction_x = random.randint(0, 40)
        if self.direction_x > 30:
            self.direction_x = 1
            self.direction_y = 0
            self.head = Cube(random.randint(2, rows - 5), random.randint(0, rows), self.direction_x, self.direction_y,
                             BLUE)
            self.body.append(self.head)
            self.body.append(Cube(self.head.position_x - 1, self.head.position_y, self.direction_x, self.direction_y))
            self.body.append(Cube(self.head.position_x - 2, self.head.position_y, self.direction_x, self.direction_y))

        elif self.direction_x > 20:
            self.direction_x = -1
            self.direction_y = 0
            self.head = Cube(random.randint(2, rows - 5), random.randint(0, rows), self.direction_x, self.direction_y,
                             BLUE)
            self.body.append(self.head)
            self.body.append(Cube(self.head.position_x + 1, self.head.position_y, self.direction_x, self.direction_y))
            self.body.append(Cube(self.head.position_x + 2, self.head.position_y, self.direction_x, self.direction_y))

        elif self.direction_x > 10:
            self.direction_y = 1
            self.direction_x = 0
            self.head = Cube(random.randint(2, rows - 5), random.randint(0, rows), self.direction_x, self.direction_y,
                             BLUE)
            self.body.append(self.head)
            self.body.append(Cube(self.head.position_x, self.head.position_y - 1, self.direction_x, self.direction_y))
            self.body.append(Cube(self.head.position_x, self.head.position_y - 2, self.direction_x, self.direction_y))
        else:
            self.direction_y = -1
            self.direction_x = 0
            self.head = Cube(random.randint(2, rows - 5), random.randint(0, rows), self.direction_x, self.direction_y,
                             BLUE)
            self.body.append(self.head)
            self.body.append(Cube(self.head.position_x, self.head.position_y + 1, self.direction_x, self.direction_y))
            self.body.append(Cube(self.head.position_x, self.head.position_y + 2, self.direction_x, self.direction_y))

        # self.head = Cube(random.randint(2, rows - 5), random.randint(0, rows), self.direction_x, self.direction_y, BLUE)
        # self.body.append(self.head)
        # self.body.append(Cube(self.head.position_x - 1 , self.head.position_y, self.direction_x, self.direction_y))
        # self.body.append(Cube(self.head.position_x - 2, self.head.position_y, self.direction_x, self.direction_y))
        # self.body.append(Cube(self.head.position_x - 3, self.head.position_y, 1, 0))
        # self.body.append(Cube(self.head.position_x - 4, self.head.position_y, 1, 0))
        self.tail = self.body[-1]
        self.dead = False
        self.turns = []
        self.directions_for_turns = []
        self.moves = 30
        self.snack_is_right = 0
        self.snack_is_left = 0
        self.snack_is_down = 0
        self.snack_is_up = 0
        self.wall_distance_x = 0
        self.wall_distance_y = 0
        self.dead_from_wall_hit = False
        self.dead_from_body_hit = False
        self.dead_from_no_moves = False
        self.BD_U = 1000
        self.BD_D = 1000
        self.BD_R = 1000
        self.BD_L = 1000

    def move(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                #run = False
                sys.exit()
        for cube in self.body:
            cube.move()
            for i, turn in enumerate(self.turns):
                if (cube.position_x, cube.position_y) == self.turns[i]:
                    cube.direction_x, cube.direction_y = self.directions_for_turns[i]
                    if self.body.index(cube) == len(self.body) - 1:
                        self.turns.pop(i)
                        self.directions_for_turns.pop(i)

    def move_right(self):
        turn_coordinate = (self.head.position_x, self.head.position_y)
        self.turns.append(turn_coordinate)
        self.head.direction_x = 1
        self.head.direction_y = 0
        self.head.direction = (self.head.direction_x, self.head.direction_y)
        self.directions_for_turns.append(self.head.direction)

    def move_left(self):
        turn_coordinate = (self.head.position_x, self.head.position_y)
        self.turns.append(turn_coordinate)
        self.head.direction_x = -1
        self.head.direction_y = 0
        self.head.direction = (self.head.direction_x, self.head.direction_y)
        self.directions_for_turns.append(self.head.direction)

    def move_up(self):
        turn_coordinate = (self.head.position_x, self.head.position_y)
        self.turns.append(turn_coordinate)
        self.head.direction_x = 0
        self.head.direction_y = -1
        self.head.direction = (self.head.direction_x, self.head.direction_y)
        self.directions_for_turns.append(self.head.direction)

    def move_down(self):
        turn_coordinate = (self.head.position_x, self.head.position_y)
        self.turns.append(turn_coordinate)
        self.head.direction_x = 0
        self.head.direction_y = 1
        self.head.direction = (self.head.direction_x, self.head.direction_y)
        self.directions_for_turns.append(self.head.direction)

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
            self.moves += 30
            return True
        return False

    def bite_or_hit(self):
        if 0 > self.head.position_x or self.head.position_x > rows - 1 or 0 > self.head.position_y or self.head.position_y > rows - 1:
            self.dead = True
            self.dead_from_wall_hit = True
        for i, cube in enumerate(self.body):
            if (self.head.position_x, self.head.position_y) == (cube.position_x, cube.position_y) and i != 0:
                self.dead = True
                self.dead_from_body_hit = True

    def find_snack_and_wall_distance(self, snack):

        if self.head.position_x < snack.x:
            self.snack_is_right = 1
            self.snack_is_left = -1
        elif self.head.position_x > snack.x:
            self.snack_is_right = -1
            self.snack_is_left = 1

        else:
            self.snack_is_right = 0
            self.snack_is_left = 0

        if self.head.position_y < snack.y:
            self.snack_is_down = 1
            self.snack_is_up = 0

        elif self.head.position_y > snack.y:
            self.snack_is_down = -1
            self.snack_is_up = 1

        else:
            self.snack_is_up = 0
            self.snack_is_down = 0

        if self.head.direction_x == 1:
            self.wall_distance_x = rows - self.head.position_x - 1
        elif self.head.direction_x == -1:
            self.wall_distance_x = self.head.position_x
        if self.head.direction_y == 1:
            self.wall_distance_y = rows - self.head.position_y - 1
        elif self.head.direction_y == -1:
            self.wall_distance_y = self.head.position_y

    def find_distance_from_body(self):

        self.BD_U = 1000
        self.BD_D = 1000
        self.BD_R = 1000
        self.BD_L = 1000

        for i, cube in enumerate(self.body):
            if self.head.position_y == cube.position_y and i != 0:
                distance_x = self.head.position_x - cube.position_x
                if distance_x > 0:
                    if self.BD_L == 1000:
                        self.BD_L = distance_x
                else:
                    if self.BD_R == 1000:
                        self.BD_R = abs(distance_x)

            if self.head.position_x == cube.position_x and i != 0:
                distance_y = self.head.position_y - cube.position_y
                if distance_y > 0:
                    if self.BD_U == 1000:
                        self.BD_U = distance_y
                else:
                    if self.BD_D == 1000:
                        self.BD_D = abs(distance_y)
                if self.BD_U != 1000 and self.BD_D != 1000 and self.BD_L != 1000 and self.BD_R != 1000:
                    break

    def snack_surroundings(self, snack):
        for i in range(4):
            if (
                    self.head.position_x == snack.x - i or self.head.position_x == snack.x + i or self.head.position_x == snack.x):
                if (
                        self.head.position_y == snack.y or self.head.position_y == snack.y - i or self.head.position_y == snack.y + i):
                    if i == 0:
                        return 15
                    if i == 1:
                        return 10
                    if i == 2:
                        return 5
                    if i == 3:
                        return 3
                else:
                    return -0.1
            else:
                return -0.1
    def moving_towards_body(self):
        if self.head.direction_x == 1 and self.BD_R != 1000:
            return 10
        elif self.head.direction_x == -1 and self.BD_L != 1000:
            return 10
        elif self.head.direction_y == 1 and self.BD_D != 1000:
            return 10
        elif self.head.direction_y == -1 and self.BD_U != 1000:
            return 10
        else:
            return 0


class Snack(object):

    def __init__(self):
        self.x = 0
        self.y = 0
        self.exists = False
        self.matching = False
        self.surroundings = []

    def generator(self, snake):
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


def draw_grid():
    x = 0
    y = 0
    for i in range(rows):
        x += SIZE
        y += SIZE

        pygame.draw.line(screen, WHITE, (x, 0), (x, HEIGHT))
        pygame.draw.line(screen, WHITE, (0, y), (WIDTH, y))


def draw(snake, snack, generation, biggest_length, current_biggest_length, num_of_snakes):
    screen.fill(BLACK)
    draw_grid()
    snack.draw()
    snake.draw()

    text_gen = "Generation: " + str(generation)
    label_gen = myfont.render(text_gen, 1, WHITE)
    screen.blit(label_gen, (WIDTH + 10, 10))

    text_biggest_length = "Biggest length = " + str(biggest_length)
    label_biggest_length = myfont.render(text_biggest_length, 1, WHITE)
    screen.blit(label_biggest_length, (WIDTH + 10, 110))

    text_current_biggest_length = "Current biggest length = " + str(current_biggest_length)
    label_current_biggest_length = myfont.render(text_current_biggest_length, 1, WHITE)
    screen.blit(label_current_biggest_length, (WIDTH + 10, 210))

    text_num_of_snakes = "Number of snakes = " + str(num_of_snakes)
    label_num_of_snakes = myfont.render(text_num_of_snakes, 1, WHITE)
    screen.blit(label_num_of_snakes, (WIDTH + 10, 310))

    pygame.display.update()


def main(genomes, config):
    global biggest_length
    global generation
    global current_biggest_length
    global lenghts
    nets = []
    ge = []
    snakes = []
    snacks = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        snakes.append(Snake())
        snacks.append(Snack())
        g.fitness = 0
        ge.append(g)

    run = True

    while run:
        if len(snakes) > 0:
            for i, snake in enumerate(snakes):
                if snake.stack_collection(snacks[i]):
                    ge[i].fitness += 15
                ge[i].fitness += snake.snack_surroundings(snacks[i])
                ge[i].fitness -= snake.moving_towards_body()
                snacks[i].generator(snake)
                snake.find_snack_and_wall_distance(snacks[i])
                snake.find_distance_from_body()
                snake.bite_or_hit()

                # ge[i].fitness += 1

                output = nets[i].activate((snake.head.position_x, snake.head.position_y, snake.head.direction_x,
                                           snake.head.direction_y, snake.wall_distance_x, snake.wall_distance_y,
                                           snake.snack_is_right, snake.snack_is_left, snake.snack_is_up,
                                           snake.snack_is_down, snake.BD_L, snake.BD_R, snake.BD_U, snake.BD_D))

                if output[0] >= 0.5:
                    snake.move_right()
                    snake.moves -= 1
                elif output[1] >= 0.5:
                    snake.move_left()
                    snake.moves -= 1
                elif output[2] >= 0.5:
                    snake.move_up()
                    snake.moves -= 1
                elif output[3] >= 0.5:
                    snake.move_down()
                    snake.moves -= 1

                snake.move()
                if snake.moves <= 0:
                    snake.dead = True
                    snake.dead_from_no_moves = True

                if len(snake.body) > biggest_length:
                    biggest_length = len(snake.body)

                if len(snake.body) > current_biggest_length:
                    current_biggest_length = len(snake.body)


                draw(snakes[0], snacks[0], generation, biggest_length, current_biggest_length, len(snakes))

                if snake.dead:
                    if snake.dead_from_wall_hit:
                        ge[i].fitness -= 15
                    if snake.dead_from_body_hit:
                        ge[i].fitness -= 10
                        if ge[i].fitness > 300:
                            ge[i].fitness //= 2
                    if snake.dead_from_no_moves:
                        ge[i].fitness -= 5
                    snake.directions_for_turns.clear()
                    snake.turns.clear()
                    snakes.pop(i)
                    snacks.pop(i)
                    ge.pop(i)
                    nets.pop(i)

        else:
            lengths.append(current_biggest_length)
            current_biggest_length = 0
            generation += 1
            #print('Biggest Length = ' + str(biggest_length))
            break

       #pygame.time.delay(50)
       #fps.tick(10)


def run(config_path):
    global lengths
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_path)
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    winner = population.run(main, 500)
    print(lengths)



if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-passforward.txt")
    run(config_path)


