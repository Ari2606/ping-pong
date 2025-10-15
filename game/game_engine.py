import pygame
from .paddle import Paddle
from .ball import Ball

# Game Engine

WHITE = (255, 255, 255)

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

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.player.move(-10, self.height)
        if keys[pygame.K_s]:
            self.player.move(10, self.height)

   def update(self):
    # Move the ball first
    self.ball.move()

    # --- New collision logic ---
    ball_rect = self.ball.rect()
    player_rect = self.player.rect()
    ai_rect = self.ai.rect()

    # Check for paddle collisions
    if ball_rect.colliderect(player_rect):
        self.ball.x = player_rect.right + self.ball.radius  # Prevent overlap
        self.ball.velocity_x *= -1

    elif ball_rect.colliderect(ai_rect):
        self.ball.x = ai_rect.left - self.ball.radius * 2
        self.ball.velocity_x *= -1
    # ----------------------------

    # Wall scoring logic
    if self.ball.x <= 0:
        self.ai_score += 1
        self.ball.reset()
    elif self.ball.x >= self.width:
        self.player_score += 1
        self.ball.reset()

    # AI tracking
    self.ai.auto_track(self.ball, self.height)

    def render(self, screen):
        # Draw paddles and ball
        pygame.draw.rect(screen, WHITE, self.player.rect())
        pygame.draw.rect(screen, WHITE, self.ai.rect())
        pygame.draw.ellipse(screen, WHITE, self.ball.rect())
        pygame.draw.aaline(screen, WHITE, (self.width//2, 0), (self.width//2, self.height))

        # Draw score
        player_text = self.font.render(str(self.player_score), True, WHITE)
        ai_text = self.font.render(str(self.ai_score), True, WHITE)
        screen.blit(player_text, (self.width//4, 20))
        screen.blit(ai_text, (self.width * 3//4, 20))
