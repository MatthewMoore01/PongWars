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
        self.temporary_squares = []  # Store temporary squares and their remaining time

    def handle_mouse_click(self, x, y):
        # Add a 4x4 square at mouse click position
        # Each square will be stored as ((left, top), time_remaining)
        square_size = 4 * self.SQUARE_SIZE
        left = x - square_size // 2
        top = y - square_size // 2
        self.temporary_squares.append(((left, top), 30 * 60))  # 30 seconds at 60 FPS

    def init_colors(self):
        self.colors = {
            'ArcticPowder': (241, 246, 244),
            'MysticMint': (217, 232, 227),
            'Forsythia': (255, 200, 150),
            'DeepSaffron': (255, 153, 50),
            'NocturnalExpedition': (17, 76, 90),
            'OceanicNoir': (23, 43, 54)
        }

    def init_game_variables(self):
        self.SQUARE_SIZE = 56
        self.numSquaresX, self.numSquaresY = self.WIDTH // self.SQUARE_SIZE, self.HEIGHT // self.SQUARE_SIZE
        self.squares = [[self.colors['MysticMint'] if i < self.numSquaresX / 2 else self.colors['OceanicNoir'] for j in range(self.numSquaresY)] for i in range(self.numSquaresX)]
        self.total_squares = self.numSquaresX * self.numSquaresY
        self.MIN_SPEED, self.MAX_SPEED = 1, 30
        self.init_balls()
        self.day_score = sum(row.count(self.colors['MysticMint']) for row in self.squares)
        self.night_score = sum(row.count(self.colors['OceanicNoir']) for row in self.squares)

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
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    self.handle_mouse_click(mouse_x, mouse_y)

            self.update_game_state()
            self.draw_game()
            pygame.display.flip()
        pygame.quit()

    def update_game_state(self):
        self.update_speeds()
        self.update_ball_positions_and_check_collisions()
        self.update_temporary_squares()

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
        self.dx2, self.dy2 = self.update_color_and_score(self.x2, self.y2, self.colors['OceanicNoir'], self.dx2, self.dy2)
        self.x1 += self.dx1
        self.y1 += self.dy1
        self.x2 += self.dx2
        self.y2 += self.dy2
        self.dx1, self.dy1 = self.check_collision(self.x1, self.y1, self.dx1, self.dy1)
        self.dx2, self.dy2 = self.check_collision(self.x2, self.y2, self.dx2, self.dy2)

    def calculate_speed(self, score, total_squares):
        # Calculate the percentage of squares controlled
        percentage = score / total_squares
        # Apply a sigmoid-like function for speed adjustment
        # This ensures a more gradual increase at the start and a tapering off towards the end
        adjusted_percentage = 1 / (1 + math.exp(-10 * (percentage - 0.5)))

        # Map the adjusted percentage to a speed between MIN_SPEED and MAX_SPEED
        speed = self.MIN_SPEED + adjusted_percentage * (self.MAX_SPEED - self.MIN_SPEED)
        return speed

    def is_opposite_color(self, ball_color, square_color):
        return (ball_color == self.colors['MysticMint'] and square_color == self.colors['OceanicNoir']) or \
            (ball_color == self.colors['OceanicNoir'] and square_color == self.colors['MysticMint'])

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

    def update_temporary_squares(self):
        # Update the remaining time for each square and remove expired ones
        self.temporary_squares = [((left, top), time - 1) for (left, top), time in self.temporary_squares if time > 1]

        # Check for ball collisions with temporary squares
        for (left, top), _ in self.temporary_squares:
            square_rect = pygame.Rect(left, top, 4 * self.SQUARE_SIZE, 4 * self.SQUARE_SIZE)
            if square_rect.colliderect(pygame.Rect(self.x1 - self.BALL_RADIUS, self.y1 - self.BALL_RADIUS, self.BALL_RADIUS * 2, self.BALL_RADIUS * 2)):
                self.dx1, self.dy1 = self.bounce_off_square(self.x1, self.y1, self.dx1, self.dy1, square_rect)
            if square_rect.colliderect(pygame.Rect(self.x2 - self.BALL_RADIUS, self.y2 - self.BALL_RADIUS, self.BALL_RADIUS * 2, self.BALL_RADIUS * 2)):
                self.dx2, self.dy2 = self.bounce_off_square(self.x2, self.y2, self.dx2, self.dy2, square_rect)


    def bounce_off_square(self, x, y, dx, dy, square_rect):
        # Check which side of the square the ball collided with and reverse the appropriate velocity component
        if x < square_rect.left or x > square_rect.right:
            dx = -dx
        if y < square_rect.top or y > square_rect.bottom:
            dy = -dy
        return dx, dy

    def draw_game(self):
        self.win.fill(self.colors['OceanicNoir'])
        self.draw_squares()
        self.draw_balls()
        self.draw_score()
        self.draw_temporary_squares()

    def draw_temporary_squares(self):
        # Draw each temporary square
        for (left, top), _ in self.temporary_squares:
            pygame.draw.rect(self.win, self.colors['ArcticPowder'],
                             (left, top, 4 * self.SQUARE_SIZE, 4 * self.SQUARE_SIZE))

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
