import pygame
import sys
import random
import neat
import os

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (50,50)
pygame.init()
pygame.display.set_caption('SnakeAI')
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

myFont = pygame.font.SysFont('Arial', 20)
myFontTraining = pygame.font.SysFont('Arial', 30)

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

        self.dead = False

        self.turns = []
        self.directions_for_turns = []
        self.snack_positions = []
        self.permanent_directions_for_turns = []
        self.permanent_turns = []

        self.moves = 30
        self.start_state = 0

        random_start = random.randint(0, 40)
        self.head_start_position = (random.randint(5, rows - 5), random.randint(5, rows-5))


        if random_start > 30:
            self.start_state = 1
            direction_x = 1
            direction_y = 0
            self.head = Cube(self.head_start_position[0], self.head_start_position[1], direction_x, direction_y, BLUE)
            self.body.append(self.head)
            self.body.append(Cube(self.head.position_x - 1, self.head.position_y, direction_x, direction_y))
            self.body.append(Cube(self.head.position_x - 2, self.head.position_y, direction_x, direction_y))

        elif random_start > 20:
            self.start_state = 2
            direction_x = -1
            direction_y = 0
            self.head = Cube(self.head_start_position[0], self.head_start_position[1], direction_x, direction_y, BLUE)
            self.body.append(self.head)
            self.body.append(Cube(self.head.position_x + 1, self.head.position_y, direction_x, direction_y))
            self.body.append(Cube(self.head.position_x + 2, self.head.position_y, direction_x, direction_y))

        elif random_start > 10:
            self.start_state = 3
            direction_x = 0
            direction_y = 1
            self.head = Cube(self.head_start_position[0], self.head_start_position[1], direction_x, direction_y, BLUE)
            self.body.append(self.head)
            self.body.append(Cube(self.head.position_x, self.head.position_y-1, direction_x, direction_y))
            self.body.append(Cube(self.head.position_x, self.head.position_y-2, direction_x, direction_y))

        else:
            self.state = 4
            direction_x = 0
            direction_y = -1
            self.head = Cube(self.head_start_position[0], self.head_start_position[1], direction_x, direction_y, BLUE)
            self.body.append(self.head)
            self.body.append(Cube(self.head.position_x, self.head.position_y+1, direction_x, direction_y))
            self.body.append(Cube(self.head.position_x, self.head.position_y+2, direction_x, direction_y))


        self.tail = self.body[-1]
        self.snack_is_right = 0
        self.snack_is_left = 0
        self.snack_is_down = 0
        self.snack_is_up = 0
        self.wall_distance_x = 0
        self.wall_distance_y = 0
        self.dead_from_wall_hit = False
        self.dead_from_body_hit = False
        self.dead_from_no_moves = False
        self.max_length = 1
        self.BD_U = 1000
        self.BD_D = 1000
        self.BD_R = 1000
        self.BD_L = 1000

    def move(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        for cube in self.body:
            cube.move()
            for i, turn in enumerate(self.turns):
                if (cube.position_x, cube.position_y) == self.turns[i]:
                    cube.direction_x, cube.direction_y = self.directions_for_turns[i]
                    if self.body.index(cube) == len(self.body) - 1:
                        self.turns.pop(i)
                        self.directions_for_turns.pop(i)

    def moveDir(self, direction_x, direction_y):
        self.moves -= 1
        turn_coordinate = (self.head.position_x, self.head.position_y)
        self.turns.append(turn_coordinate)
        self.permanent_turns.append(turn_coordinate)
        self.head.direction_x = direction_x
        self.head.direction_y = direction_y
        self.head.direction = (self.head.direction_x, self.head.direction_y)
        self.directions_for_turns.append(self.head.direction)
        self.permanent_directions_for_turns.append(self.head.direction)

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
            self.max_length += 1
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
                    return -1
            else:
                return -1



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
                    snake.snack_positions.append((self.x, self.y))
                    break

    def draw(self):
        if self.exists:
            pygame.draw.rect(screen, GREEN, (self.x * SIZE + 1, self.y * SIZE + 1, SIZE - 1, SIZE - 1))

class DrawingSnake(object):
    def __init__(self, snake, generation):
        self.body = []
        self.start_state = snake.start_state
        self.dead = False
        self.permanent_turns = snake.permanent_turns
        self.permanent_directions_for_turns = snake.permanent_directions_for_turns
        self.turns = []
        self.directions_for_turns = []
        self.snack_positions = snake.snack_positions
        self.moves = 30
        self.max_length = snake.max_length
        self.generation = generation
        self.snack_position = self.snack_positions.pop(0)
        self.dead_from_wall_hit = False
        self.dead_from_body_hit = False
        self.dead_from_no_moves = False
        self.head_start_position = snake.head_start_position


        if snake.start_state == 1:
            direction_x = 1
            direction_y = 0
            self.head = Cube(self.head_start_position[0], self.head_start_position[1], direction_x, direction_y, BLUE)
            self.body.append(self.head)
            self.body.append(Cube(self.head.position_x - 1, self.head.position_y, direction_x, direction_y))
            self.body.append(Cube(self.head.position_x - 2, self.head.position_y, direction_x, direction_y))

        elif snake.start_state == 2:
            direction_x = -1
            direction_y = 0
            self.head = Cube(self.head_start_position[0], self.head_start_position[1], direction_x, direction_y, BLUE)
            self.body.append(self.head)
            self.body.append(Cube(self.head.position_x+1, self.head.position_y, direction_x, direction_y))
            self.body.append(Cube(self.head.position_x+2, self.head.position_y, direction_x, direction_y))

        elif snake.start_state == 3:
            direction_x = 0
            direction_y = 1
            self.head = Cube(self.head_start_position[0], self.head_start_position[1], direction_x, direction_y, BLUE)
            self.body.append(self.head)
            self.body.append(Cube(self.head.position_x, self.head.position_y-1, direction_x, direction_y))
            self.body.append(Cube(self.head.position_x, self.head.position_y-2, direction_x, direction_y))

        else:
            direction_x = 0
            direction_y = -1
            self.head = Cube(self.head_start_position[0], self.head_start_position[1], direction_x, direction_y, BLUE)
            self.body.append(self.head)
            self.body.append(Cube(self.head.position_x, self.head.position_y+1, direction_x, direction_y))
            self.body.append(Cube(self.head.position_x, self.head.position_y+2, direction_x, direction_y))

        self.tail = self.body[-1]


    def move(self):

        self.moves -= 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()



        #If head gets into the position of next turn

        if (len(self.permanent_turns) > 0 and (self.head.position_x, self.head.position_y) == self.permanent_turns[0]):

            # change the direction of the head and remove that turn
            self.head.direction_x, self.head.direction_y = self.permanent_directions_for_turns.pop(0)
            self.permanent_turns.pop(0)

            # let other parts of body know there is a turn at that place and where to go
            self.turns.append((self.head.position_x, self.head.position_y))
            self.directions_for_turns.append((self.head.direction_x, self.head.direction_y))




        for cube in self.body:
            if cube != self.head:
                for i, turn in enumerate(self.turns):
                    if (cube.position_x, cube.position_y) == self.turns[i]:
                        cube.direction_x, cube.direction_y = self.directions_for_turns[i]
                        if self.body.index(cube) == len(self.body) - 1:
                            self.turns.pop(i)
                            self.directions_for_turns.pop(i)

        for cube in self.body:
            cube.move()

        # id cubes other than head run into a place for turn, change their direction
        # if tail goes over the place for turn, remove that turn


    def stack_collection(self):
        if (self.head.position_x, self.head.position_y) == self.snack_position:
            self.tail = self.body[-1]
            if self.tail.direction_x == 1:
                self.body.append(Cube(self.tail.position_x - 1, self.tail.position_y, 1, 0))
            elif self.tail.direction_x == -1:
                self.body.append(Cube(self.tail.position_x + 1, self.tail.position_y, -1, 0))
            elif self.tail.direction_y == 1:
                self.body.append(Cube(self.tail.position_x, self.tail.position_y - 1, 0, 1))
            elif self.tail.direction_y == -1:
                self.body.append(Cube(self.tail.position_x, self.tail.position_y + 1, 0, -1))
            self.snack_position = self.snack_positions.pop(0)
            self.moves += 30
            return True
        return False

    def draw(self):
        for cube in self.body:
            cube.draw()
        pygame.draw.rect(screen, GREEN, (self.snack_position[0] * SIZE + 1, self.snack_position[1] * SIZE + 1, SIZE - 1, SIZE - 1))

    def bite_or_hit(self):
        if 0 > self.head.position_x or self.head.position_x > rows - 1 or 0 > self.head.position_y or self.head.position_y > rows - 1:
            self.dead_from_wall_hit = True
            self.dead = True
            return
        for i, cube in enumerate(self.body):
            if (self.head.position_x, self.head.position_y) == (cube.position_x, cube.position_y) and i != 0:
                self.dead_from_body_hit = True
                self.dead = True
        if self.moves <= 0:
            self.dead_from_no_moves = True
            self.dead = True





def draw_grid():
    x = 0
    y = 0

    for i in range(rows + 1):
        pygame.draw.line(screen, WHITE, (x, 0), (x, HEIGHT))
        pygame.draw.line(screen, WHITE, (0, y), (WIDTH, y))
        x += SIZE
        y += SIZE


def draw(snake, biggest_length, current_biggest_length, generation, snack = None):

    screen.fill(BLACK)

    if snake != None:
        draw_grid()
        snake.draw()
        text_moves = "Moves left: " + str(snake.moves)
        label_moves = myFont.render(text_moves, 1, WHITE)
        screen.blit(label_moves, (WIDTH + 10, 310))
    else:
        text_training = "Generation " + str(generation + 1) + " is currently training"
        label_training = myFontTraining.render(text_training, 20, WHITE)
        screen.blit(label_training, (0, 20))
        pygame.draw.line(screen, WHITE, (WIDTH, 0), (WIDTH, HEIGHT))

    if snack != None:
        snack.draw()

    text_gen = "Generation: " + str(generation)
    label_gen = myFont.render(text_gen, 1, WHITE)
    screen.blit(label_gen, (WIDTH + 10, 10))

    text_biggest_length = "Biggest length = " + str(biggest_length)
    label_biggest_length = myFont.render(text_biggest_length, 1, WHITE)
    screen.blit(label_biggest_length, (WIDTH + 10, 110))

    text_current_biggest_length = "Best in generation = " + str(current_biggest_length)
    label_current_biggest_length = myFont.render(text_current_biggest_length, 1, WHITE)
    screen.blit(label_current_biggest_length, (WIDTH + 10, 210))

    pygame.display.update()

current_best_snake = None
snakeToDraw = None
best_snakes = []
def main(genomes, config):
    global biggest_length
    global generation
    global current_biggest_length
    global lenghts
    global current_best_snake
    global snakeToDraw
    global best_snakes
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
        #screen.fill(WHITE)
        #pygame.display.update()

        if len(snakes) > 0:
            for i, snake in enumerate(snakes):
                if snake.stack_collection(snacks[i]):
                    ge[i].fitness += 15
                ge[i].fitness += snake.snack_surroundings(snacks[i])
                snacks[i].generator(snake)
                snake.find_snack_and_wall_distance(snacks[i])
                snake.bite_or_hit()

                # ge[i].fitness += 1

                output = nets[i].activate((snake.head.position_x, snake.head.position_y, snake.head.direction_x, snake.head.direction_y, snake.wall_distance_x, snake.wall_distance_y, snake.snack_is_right, snake.snack_is_left, snake.snack_is_up, snake.snack_is_down))

                #draw(snakes[0], biggest_length, current_biggest_length, generation, snacks[0])

                if output[0] >= 0.5:
                    snake.moveDir(1,0)
                elif output[1] >= 0.5:
                    snake.moveDir(-1,0)
                elif output[2] >= 0.5:
                    snake.moveDir(0,-1)
                elif output[3] >= 0.5:
                    snake.moveDir(0,1)

                snake.move()

                if snake.moves <= 0:
                    snake.dead = True
                    snake.dead_from_no_moves = True

                if len(snake.body) > biggest_length:
                    biggest_length = len(snake.body)

                if len(snake.body) > current_biggest_length:
                    current_biggest_length = len(snake.body)
                    current_best_snake = snake




                if snake.dead:
                    if snake.dead_from_wall_hit:
                        ge[i].fitness -= 15
                    if snake.dead_from_body_hit:
                        ge[i].fitness -= 10
                        #if ge[i].fitness > 300:
                        #    ge[i].fitness //= 2
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
            bestSnake = DrawingSnake(current_best_snake, generation)
            if current_best_snake.dead_from_wall_hit:
                print('Generation ' + str(generation) + ' Dead from WALL HIT')
            if current_best_snake.dead_from_body_hit:
                print('Generation ' + str(generation) + ' Dead from BODY HIT')
            if current_best_snake.dead_from_no_moves:
                print('Generation ' + str(generation) + ' Dead from NO MOVES')

            
            best_snakes.append(bestSnake)
            generation += 1
            break

        #pygame.time.delay(50)
        #fps.tick(10)


def run(config_path):
    global lengths
    global biggest_length
    global generation
    global current_biggest_length
    global lenghts
    global current_best_snake
    global snakeToDraw
    global best_snakes
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_path)
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    #winner = \
    population.run(main, 500)
    print(lengths)

    snakeToDraw = None
    generation = 0
    while len(best_snakes) > 0:
        if snakeToDraw == None or snakeToDraw.dead:
            if snakeToDraw == None:
                pass
            else:
                if snakeToDraw.dead_from_wall_hit:
                    print('Generation ' + str(generation) + ' Dead from WALL HIT')
                elif snakeToDraw.dead_from_body_hit:
                    print('Generation ' + str(generation) + ' Dead from BODY HIT')
                elif snakeToDraw.dead_from_no_moves:
                    print('Generation ' + str(generation) + ' Dead from NO MOVES')

            snakeToDraw = best_snakes.pop(0)

            generation += 1
            
        snakeToDraw.stack_collection()
        snakeToDraw.bite_or_hit()
        draw(snakeToDraw, biggest_length, snakeToDraw.max_length, generation)
        snakeToDraw.move()
        pygame.time.delay(50)
        fps.tick(10)









if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-passforward.txt")
    run(config_path)