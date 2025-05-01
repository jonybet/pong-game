import pygame
import sys

# Initialize pygame
pygame.init()

# Constant variables 
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
PADDLE_WIDTH, PADDLE_HEIGHT = 15, 100
BALL_SIZE = 20
PADDLE_SPEED = 7
BALL_SPEED_X, BALL_SPEED_Y = 5, 5
WINNING_SCORE = 5

# Window and fonts
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong")
FONT = pygame.font.SysFont("comicsans", 40)
BIG_FONT = pygame.font.SysFont("comicsans", 60)


# Button for the menu 
def draw_button(surface, rect, text, font, bg_color, text_color):
    pygame.draw.rect(surface, bg_color, rect, border_radius=10)
    label = font.render(text, True, text_color)
    surface.blit(
        label,
        (rect.centerx - label.get_width() // 2, rect.centery - label.get_height() // 2)
    )


def is_button_clicked(rect, mouse_pos):
    return rect.collidepoint(mouse_pos)


# Paddle class
class Paddle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.speed = PADDLE_SPEED

    def move(self, up=True):
        if up and self.rect.top > 0:
            self.rect.y -= self.speed
        elif not up and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed

    def draw(self, window):
        pygame.draw.rect(window, WHITE, self.rect)


# Ball class
class Ball:
    def __init__(self):
        self.rect = pygame.Rect(
            (WIDTH - BALL_SIZE) // 2,
            (HEIGHT - BALL_SIZE) // 2,
            BALL_SIZE, BALL_SIZE
        )
        self.speed_x = BALL_SPEED_X
        self.speed_y = BALL_SPEED_Y

    def move(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

    def check_collision(self, left_paddle, right_paddle):
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.speed_y *= -1

        if self.rect.colliderect(left_paddle.rect) or self.rect.colliderect(right_paddle.rect):
            self.speed_x *= -1
            self.hit_count += 1  # Increase hit count on paddle hit

            # Gradually increase speed after a few hits (for example, after 5 hits)
            if self.hit_count >= 3:  # Start increasing speed after 5 hits
                self.speed_x *= 1.15
                self.speed_y *= 1.15
                self.hit_count = 0  # Reset hit count after increasing speed

        # Cap the speed to prevent it from getting too fast
        max_speed = 12
        self.speed_x = max(-max_speed, min(self.speed_x, max_speed))
        self.speed_y = max(-max_speed, min(self.speed_y, max_speed))

    def reset(self):
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.speed_x = BALL_SPEED_X * (-1 if self.speed_x > 0 else 1)
        self.speed_y = BALL_SPEED_Y * (-1 if self.speed_y > 0 else 1)
        self.hit_count = 0  # Reset hit count when the game restarts

    def draw(self, window):
        pygame.draw.ellipse(window, WHITE, self.rect)


# Game class
class Game:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.left_paddle = Paddle(10, (HEIGHT - PADDLE_HEIGHT) // 2)
        self.right_paddle = Paddle(WIDTH - 25, (HEIGHT - PADDLE_HEIGHT) // 2)
        self.ball = Ball()
        self.left_score = 0
        self.right_score = 0
        self.state = "start"
        self.mode = None
        self.winner = ""
        self.single_button = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 60, 300, 60)
        self.multi_button = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 20, 300, 60)

    def draw_play(self):
        WINDOW.fill(BLACK)
        pygame.draw.aaline(WINDOW, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))
        self.left_paddle.draw(WINDOW)
        self.right_paddle.draw(WINDOW)
        self.ball.draw(WINDOW)

        left_text = FONT.render(f"{self.left_score}", True, WHITE)
        right_text = FONT.render(f"{self.right_score}", True, WHITE)
        WINDOW.blit(left_text, (WIDTH // 4 - left_text.get_width() // 2, 20))
        WINDOW.blit(right_text, (WIDTH * 3 // 4 - right_text.get_width() // 2, 20))

        mode_text = FONT.render(f"Mode: {'1P vs AI' if self.mode == 'single' else '2P'}", True, WHITE)
        WINDOW.blit(mode_text, (WIDTH // 2 - mode_text.get_width() // 2, HEIGHT - 40))

    def draw_start_screen(self):
        WINDOW.fill(BLACK)
        title = BIG_FONT.render("PONG", True, WHITE)
        WINDOW.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 5))

        mouse_pos = pygame.mouse.get_pos()

        # Button hover colors
        single_color = GRAY if self.single_button.collidepoint(mouse_pos) else WHITE
        multi_color = GRAY if self.multi_button.collidepoint(mouse_pos) else WHITE

        draw_button(WINDOW, self.single_button, "Single Player", FONT, single_color, BLACK)
        draw_button(WINDOW, self.multi_button, "Two Player", FONT, multi_color, BLACK)

        pygame.display.flip()

    def draw_game_over(self):
        WINDOW.fill(BLACK)
        result = BIG_FONT.render(self.winner, True, WHITE)
        instruction = FONT.render("Press any key to return to menu", True, WHITE)
        WINDOW.blit(result, (WIDTH // 2 - result.get_width() // 2, HEIGHT // 3))
        WINDOW.blit(instruction, (WIDTH // 2 - instruction.get_width() // 2, HEIGHT // 2))
        pygame.display.flip()

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.left_paddle.move(True)
        if keys[pygame.K_s]:
            self.left_paddle.move(False)

        if self.mode == "multi":
            if keys[pygame.K_UP]:
                self.right_paddle.move(True)
            if keys[pygame.K_DOWN]:
                self.right_paddle.move(False)

    def move_ai(self):
        if self.ball.rect.centery < self.right_paddle.rect.centery and self.right_paddle.rect.top > 0:
            self.right_paddle.rect.y -= min(PADDLE_SPEED, abs(self.ball.rect.centery - self.right_paddle.rect.centery))
        elif self.ball.rect.centery > self.right_paddle.rect.centery and self.right_paddle.rect.bottom < HEIGHT:
            self.right_paddle.rect.y += min(PADDLE_SPEED, abs(self.ball.rect.centery - self.right_paddle.rect.centery))

    def check_score(self):
        if self.ball.rect.left <= 0:
            self.right_score += 1
            self.ball.reset()
        elif self.ball.rect.right >= WIDTH:
            self.left_score += 1
            self.ball.reset()

        if self.left_score >= WINNING_SCORE:
            self.winner = "Left Player Wins!"
            self.state = "game_over"
        elif self.right_score >= WINNING_SCORE:
            self.winner = "Right Player Wins!" if self.mode == "multi" else "You Lose!"
            self.state = "game_over"

    def reset_game(self):
        self.left_score = 0
        self.right_score = 0
        self.ball.reset()
        self.left_paddle.rect.y = (HEIGHT - PADDLE_HEIGHT) // 2
        self.right_paddle.rect.y = (HEIGHT - PADDLE_HEIGHT) // 2

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if self.state == "start":
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mouse_pos = pygame.mouse.get_pos()
                        if self.single_button.collidepoint(mouse_pos):
                            self.mode = "single"
                            self.reset_game()
                            self.state = "play"
                        elif self.multi_button.collidepoint(mouse_pos):
                            self.mode = "multi"
                            self.reset_game()
                            self.state = "play"

                elif self.state == "game_over":
                    if event.type == pygame.KEYDOWN:
                        self.state = "start"

            if self.state == "start":
                self.draw_start_screen()

            elif self.state == "play":
                self.handle_input()
                if self.mode == "single":
                    self.move_ai()
                self.ball.move()
                self.ball.check_collision(self.left_paddle, self.right_paddle)
                self.check_score()
                self.draw_play()
                pygame.display.flip()

            elif self.state == "game_over":
                self.draw_game_over()

            self.clock.tick(60)


# Run the game
if __name__ == "__main__":
    Game().run()
