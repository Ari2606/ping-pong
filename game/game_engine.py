import pygame
from .paddle import Paddle
from .ball import Ball

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Initialize pygame mixer early
pygame.mixer.init()

# Load sounds (ensure these .wav files exist in your assets folder)
paddle_hit_sound = pygame.mixer.Sound("assets/paddle_hit.wav")
wall_bounce_sound = pygame.mixer.Sound("assets/wall_bounce.wav")
score_sound = pygame.mixer.Sound("assets/score.wav")


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.paddle_width = 10
        self.paddle_height = 100

        self.player = Paddle(10, height // 2 - 50, self.paddle_width, self.paddle_height)
        self.ai = Paddle(width - 20, height // 2 - 50, self.paddle_width, self.paddle_height)
        self.ball = Ball(width // 2, height // 2, 7, 7, width, height)

        self.player_score = 0
        self.ai_score = 0
        self.font = pygame.font.SysFont("Arial", 30)
        self.game_over = False
        self.win_target = 5

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.player.move(-10, self.height)
        if keys[pygame.K_s]:
            self.player.move(10, self.height)

    def update(self):
        if self.game_over:
            return

        # Track old velocity before movement
        old_vx, old_vy = self.ball.velocity_x, self.ball.velocity_y

        self.ball.move()

        # --- Paddle collision ---
        ball_rect = self.ball.rect()
        player_rect = self.player.rect()
        ai_rect = self.ai.rect()

        if ball_rect.colliderect(player_rect):
            self.ball.x = player_rect.right + self.ball.radius
            self.ball.velocity_x *= -1
            paddle_hit_sound.play()
        elif ball_rect.colliderect(ai_rect):
            self.ball.x = ai_rect.left - self.ball.radius * 2
            self.ball.velocity_x *= -1
            paddle_hit_sound.play()

        # --- Wall collision (top/bottom) ---
        if self.ball.y <= 0 or self.ball.y + self.ball.radius * 2 >= self.height:
            if self.ball.velocity_y != old_vy:  # Ensure we only play once per bounce
                wall_bounce_sound.play()

        # --- Scoring ---
        if self.ball.x <= 0:
            self.ai_score += 1
            score_sound.play()
            self.ball.reset()
        elif self.ball.x >= self.width:
            self.player_score += 1
            score_sound.play()
            self.ball.reset()

        # --- Game over check ---
        self.check_game_over()

        # --- AI tracking ---
        self.ai.auto_track(self.ball, self.height)

    def check_game_over(self):
        if self.player_score == self.win_target or self.ai_score == self.win_target:
            self.game_over = True
            winner = "Player Wins!" if self.player_score == self.win_target else "AI Wins!"
            self.show_game_over_screen(winner)

    def show_game_over_screen(self, winner_text):
        screen = pygame.display.get_surface()
        font_big = pygame.font.SysFont("Arial", 60, bold=True)
        font_small = pygame.font.SysFont("Arial", 28)

        screen.fill(BLACK)
        title = font_big.render(winner_text, True, WHITE)
        title_rect = title.get_rect(center=(self.width // 2, self.height // 2 - 80))
        screen.blit(title, title_rect)

        options = [
            "Press 3 for Best of 3",
            "Press 5 for Best of 5",
            "Press 7 for Best of 7",
            "Press ESC to Exit"
        ]
        for i, text in enumerate(options):
            txt_surface = font_small.render(text, True, WHITE)
            txt_rect = txt_surface.get_rect(center=(self.width // 2, self.height // 2 + i * 40))
            screen.blit(txt_surface, txt_rect)

        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        exit()
                    elif event.key == pygame.K_3:
                        self.win_target = 3
                        waiting = False
                    elif event.key == pygame.K_5:
                        self.win_target = 5
                        waiting = False
                    elif event.key == pygame.K_7:
                        self.win_target = 7
                        waiting = False

        self.reset_game()

    def reset_game(self):
        self.player_score = 0
        self.ai_score = 0
        self.ball.reset()
        self.player.y = self.height // 2 - self.paddle_height // 2
        self.ai.y = self.height // 2 - self.paddle_height // 2
        self.game_over = False

    def render(self, screen):
        pygame.draw.rect(screen, WHITE, self.player.rect())
        pygame.draw.rect(screen, WHITE, self.ai.rect())
        pygame.draw.ellipse(screen, WHITE, self.ball.rect())
        pygame.draw.aaline(screen, WHITE, (self.width // 2, 0), (self.width // 2, self.height))

        player_text = self.font.render(str(self.player_score), True, WHITE)
        ai_text = self.font.render(str(self.ai_score), True, WHITE)
        screen.blit(player_text, (self.width // 4, 20))
        screen.blit(ai_text, (self.width * 3 // 4, 20))
