import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1000, 1000
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong Wars")

# Colors
ArcticPowder = (241, 246, 244)
MysticMint = (217, 232, 227)
Forsythia = (255, 200, 1)
DeepSaffron = (255, 153, 50)
NocturnalExpedition = (17, 76, 90)
OceanicNoir = (23, 43, 54)

# Game variables
SQUARE_SIZE = 40
numSquaresX, numSquaresY = WIDTH // SQUARE_SIZE, HEIGHT // SQUARE_SIZE
squares = [[MysticMint if i < numSquaresX / 2 else NocturnalExpedition for j in range(numSquaresY)] for i in range(numSquaresX)]
total_squares = numSquaresX * numSquaresY

# Constants for minimum and maximum speeds
MIN_SPEED = 1
MAX_SPEED = 30

# Ball properties
x1, y1 = (WIDTH + random.randrange(0, WIDTH / 4)) // 4, (HEIGHT + random.randrange(0, HEIGHT / 4)) // 2
dx1, dy1 = 12.5, -12.5
x2, y2 = 3 * (WIDTH + random.randrange(0, WIDTH / 4)) // 4, (HEIGHT + random.randrange(0, HEIGHT / 4)) // 2
dx2, dy2 = -12.5, 12.5
BALL_RADIUS = SQUARE_SIZE // 2


# Main game loop
running = True
clock = pygame.time.Clock()

# Initialize scores based on the starting layout
day_score = sum(row.count(MysticMint) for row in squares)
night_score = sum(row.count(NocturnalExpedition) for row in squares)


def scale_value(value, original_min, original_max, new_min, new_max):
    # Compute the ratio of the difference between the value and original min to the size of the original range
    ratio = (value - original_min) / (original_max - original_min)

    # Apply this ratio to the new range
    new_value = new_min + (ratio * (new_max - new_min))

    return new_value


def calculate_speed(score, total_squares):
    # Calculate the percentage of squares controlled
    percentage = (score / total_squares)
    # Map the percentage to a speed between MIN_SPEED and MAX_SPEED
    speed = percentage * MAX_SPEED
    return speed


def is_opposite_color(ball_color, square_color):
    return (ball_color == MysticMint and square_color == NocturnalExpedition) or \
           (ball_color == NocturnalExpedition and square_color == MysticMint)


def update_color_and_score(x, y, ball_color, dx, dy):
    global day_score, night_score
    # Adjust x, y to point to the ball's center for accurate collision checking
    x += dx
    y += dy
    # Calculate ball edges
    left_edge = x - BALL_RADIUS
    right_edge = x + BALL_RADIUS
    top_edge = y - BALL_RADIUS
    bottom_edge = y + BALL_RADIUS

    # Check all squares the ball overlaps with
    squares_changed = False
    for i in range(int(left_edge // SQUARE_SIZE), int(math.ceil(right_edge / SQUARE_SIZE))):
        for j in range(int(top_edge // SQUARE_SIZE), int(math.ceil(bottom_edge / SQUARE_SIZE))):
            if 0 <= i < numSquaresX and 0 <= j < numSquaresY:
                square_color = squares[i][j]
                if is_opposite_color(ball_color, square_color):
                    # Change the color of the square
                    squares[i][j] = ball_color
                    squares_changed = True
                    # Update the score
                    if ball_color == MysticMint:
                        day_score += 1
                        night_score -= 1
                    else:
                        night_score += 1
                        day_score -= 1
                    # Draw only the square that has changed
                    pygame.draw.rect(win, ball_color, (i * SQUARE_SIZE, j * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    # If any squares changed, calculate new speed and direction
    if squares_changed:
        speed = math.hypot(dx, dy)
        angle = math.atan2(-dy, -dx) + random.uniform(-math.pi/8, math.pi/8)
        dx = speed * math.cos(angle)
        dy = speed * math.sin(angle)

    return dx, dy



def check_collision(x, y, dx, dy):
    if x + dx > WIDTH - BALL_RADIUS or x + dx < BALL_RADIUS:
        dx = -dx
    if y + dy > HEIGHT - BALL_RADIUS or y + dy < BALL_RADIUS:
        dy = -dy
    return dx, dy


while running:
    clock.tick(60)  # 60 frames per second
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update speeds based on the current scores
    day_speed = calculate_speed(day_score, total_squares)
    night_speed = calculate_speed(night_score, total_squares)

    # Normalize the direction vectors and scale them by the new speeds
    day_direction = math.hypot(dx1, dy1)
    night_direction = math.hypot(dx2, dy2)

    # Avoid division by zero in case of no movement
    if day_direction != 0:
        dx1 = (dx1 / day_direction) * day_speed
        dy1 = (dy1 / day_direction) * day_speed

    if night_direction != 0:
        dx2 = (dx2 / night_direction) * night_speed
        dy2 = (dy2 / night_direction) * night_speed

    # Inside the main loop
    dx1, dy1 = update_color_and_score(x1, y1, MysticMint, dx1, dy1)
    dx2, dy2 = update_color_and_score(x2, y2, NocturnalExpedition, dx2, dy2)

    # Now apply the updated velocities to the ball positions
    x1 += dx1
    y1 += dy1
    x2 += dx2
    y2 += dy2

    # Collision with walls
    dx1, dy1 = check_collision(x1, y1, dx1, dy1)
    dx2, dy2 = check_collision(x2, y2, dx2, dy2)

    # Drawing the game
    win.fill(OceanicNoir)
    for i in range(numSquaresX):
        for j in range(numSquaresY):
            pygame.draw.rect(win, squares[i][j], (i*SQUARE_SIZE, j*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    # Draw balls
    pygame.draw.circle(win, OceanicNoir, (int(x1), int(y1)), BALL_RADIUS)
    pygame.draw.circle(win, MysticMint, (int(x2), int(y2)), BALL_RADIUS)

    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f'Day: {day_score} | Night: {night_score}', True, (0, 0, 0))
    win.blit(score_text, (20, 20))

    # Update the display once per frame
    pygame.display.flip()

pygame.quit()
