import pygame
import random
import math

class PongWarsGame:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = 1460, 900
        self.win = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Pong Wars")
        self.init_colors()
        self.init_game_variables()

    def init_colors(self):
        self.colors = {
            'ArcticPowder': (241, 246, 244),
            'MysticMint': (217, 232, 227),
            'Forsythia': (255, 200, 1),
            'DeepSaffron': (255, 153, 50),
            'NocturnalExpedition': (17, 76, 90),
            'OceanicNoir': (23, 43, 54)
        }

    def init_game_variables(self):
        self.SQUARE_SIZE = 56
        self.numSquaresX, self.numSquaresY = self.WIDTH // self.SQUARE_SIZE, self.HEIGHT // self.SQUARE_SIZE
        self.squares = [[self.colors['MysticMint'] if i < self.numSquaresX / 2 else self.colors['NocturnalExpedition'] for j in range(self.numSquaresY)] for i in range(self.numSquaresX)]
        self.total_squares = self.numSquaresX * self.numSquaresY
        self.MIN_SPEED, self.MAX_SPEED = 1, 30
        self.init_balls()
        self.day_score = sum(row.count(self.colors['MysticMint']) for row in self.squares)
        self.night_score = sum(row.count(self.colors['NocturnalExpedition']) for row in self.squares)

    def init_balls(self):
        self.BALL_RADIUS = self.SQUARE_SIZE // 2
        self.x1, self.y1 = (self.WIDTH + random.randrange(0, self.WIDTH / 4)) // 4, (self.HEIGHT + random.randrange(0, self.HEIGHT / 4)) // 2
        self.dx1, self.dy1 = 12.5, -12.5
        self.x2, self.y2 = 3 * (self.WIDTH + random.randrange(0, self.WIDTH / 4)) // 4, (self.HEIGHT + random.randrange(0, self.HEIGHT / 4)) // 2
        self.dx2, self.dy2 = -12.5, 12.5

    def run(self):
        running = True
        clock = pygame.time.Clock()
        while running:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.update_game_state()
            self.draw_game()
            pygame.display.flip()
        pygame.quit()

    def update_game_state(self):
        self.update_speeds()
        self.update_ball_positions_and_check_collisions()

    def update_speeds(self):
        # Calculate and update speeds based on current scores
        day_speed = self.calculate_speed(self.day_score, self.total_squares)
        night_speed = self.calculate_speed(self.night_score, self.total_squares)
        self.dx1, self.dy1 = self.adjust_speed(self.dx1, self.dy1, day_speed)
        self.dx2, self.dy2 = self.adjust_speed(self.dx2, self.dy2, night_speed)

    def adjust_speed(self, dx, dy, speed):
        direction = math.hypot(dx, dy)
        if direction != 0:
            dx = (dx / direction) * speed
            dy = (dy / direction) * speed
        return dx, dy

    def update_ball_positions_and_check_collisions(self):
        # Update ball positions and check for color change collisions
        self.dx1, self.dy1 = self.update_color_and_score(self.x1, self.y1, self.colors['MysticMint'], self.dx1, self.dy1)
        self.dx2, self.dy2 = self.update_color_and_score(self.x2, self.y2, self.colors['NocturnalExpedition'], self.dx2, self.dy2)
        self.x1 += self.dx1
        self.y1 += self.dy1
        self.x2 += self.dx2
        self.y2 += self.dy2
        self.dx1, self.dy1 = self.check_collision(self.x1, self.y1, self.dx1, self.dy1)
        self.dx2, self.dy2 = self.check_collision(self.x2, self.y2, self.dx2, self.dy2)

    def calculate_speed(self, score, total_squares):
        # Calculate the percentage of squares controlled
        percentage = score / total_squares
        # Map the percentage to a speed between MIN_SPEED and MAX_SPEED
        speed = self.MIN_SPEED + percentage * (self.MAX_SPEED - self.MIN_SPEED)
        return speed

    def is_opposite_color(self, ball_color, square_color):
        return (ball_color == self.colors['MysticMint'] and square_color == self.colors['NocturnalExpedition']) or \
            (ball_color == self.colors['NocturnalExpedition'] and square_color == self.colors['MysticMint'])

    def update_color_and_score(self, x, y, ball_color, dx, dy):
        global day_score, night_score
        x += dx
        y += dy
        left_edge = x - self.BALL_RADIUS
        right_edge = x + self.BALL_RADIUS
        top_edge = y - self.BALL_RADIUS
        bottom_edge = y + self.BALL_RADIUS

        squares_changed = False
        for i in range(int(left_edge // self.SQUARE_SIZE), int(math.ceil(right_edge / self.SQUARE_SIZE))):
            for j in range(int(top_edge // self.SQUARE_SIZE), int(math.ceil(bottom_edge / self.SQUARE_SIZE))):
                if 0 <= i < self.numSquaresX and 0 <= j < self.numSquaresY:
                    square_color = self.squares[i][j]
                    if self.is_opposite_color(ball_color, square_color):
                        self.squares[i][j] = ball_color
                        squares_changed = True
                        if ball_color == self.colors['MysticMint']:
                            self.day_score += 1
                            self.night_score -= 1
                        else:
                            self.night_score += 1
                            self.day_score -= 1
                        pygame.draw.rect(self.win, ball_color, (
                        i * self.SQUARE_SIZE, j * self.SQUARE_SIZE, self.SQUARE_SIZE, self.SQUARE_SIZE))

        if squares_changed:
            speed = math.hypot(dx, dy)
            angle = math.atan2(-dy, -dx) + random.uniform(-math.pi / 8, math.pi / 8)
            dx = speed * math.cos(angle)
            dy = speed * math.sin(angle)
        return dx, dy

    def check_collision(self, x, y, dx, dy):
        if x + dx > self.WIDTH - self.BALL_RADIUS or x + dx < self.BALL_RADIUS:
            dx = -dx
        if y + dy > self.HEIGHT - self.BALL_RADIUS or y + dy < self.BALL_RADIUS:
            dy = -dy
        return dx, dy

    def draw_game(self):
        self.win.fill(self.colors['OceanicNoir'])
        self.draw_squares()
        self.draw_balls()
        self.draw_score()

    def draw_squares(self):
        for i in range(self.numSquaresX):
            for j in range(self.numSquaresY):
                pygame.draw.rect(self.win, self.squares[i][j], (i * self.SQUARE_SIZE, j * self.SQUARE_SIZE, self.SQUARE_SIZE, self.SQUARE_SIZE))

    def draw_balls(self):
        pygame.draw.circle(self.win, self.colors['OceanicNoir'], (int(self.x1), int(self.y1)), self.BALL_RADIUS)
        pygame.draw.circle(self.win, self.colors['MysticMint'], (int(self.x2), int(self.y2)), self.BALL_RADIUS)

    def draw_score(self):
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f'Day: {self.day_score} | Night: {self.night_score}', True, (0, 0, 0))
        self.win.blit(score_text, (20, 20))

# Run the game
if __name__ == "__main__":
    game = PongWarsGame()
    game.run()
