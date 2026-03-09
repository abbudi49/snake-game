#!/usr/bin/env python3
"""
Snake Game - Backup Demo Version
Simple, reliable implementation for workshop demos
"""

import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 400
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 200, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
PINK = (255, 20, 147)
PURPLE = (148, 0, 211)

FOOD_COLORS = [RED, ORANGE, YELLOW, PINK, PURPLE]

class SnakeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake Game - LLM Workshop Demo")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        
        self.reset_game()
    
    def reset_game(self):
        # Snake starts in the middle
        self.snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0)  # Moving right
        self.score = 0
        self.game_over = False
        
        # Create multiple food items
        self.foods = []
        self.spawn_food()
        self.spawn_food()
        self.spawn_food()
    
    def spawn_food(self):
        """Spawn a food item at a random location not occupied by snake or other food"""
        max_attempts = 100
        for _ in range(max_attempts):
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            
            # Check if position is free
            if (x, y) not in self.snake and not any((x, y) == food[:2] for food in self.foods):
                color = random.choice(FOOD_COLORS)
                self.foods.append((x, y, color))
                break
    
    def handle_input(self):
        """Handle WASD key input"""
        keys = pygame.key.get_pressed()
        
        # WASD controls
        if keys[pygame.K_w] and self.direction != (0, 1):  # W - up
            self.direction = (0, -1)
        elif keys[pygame.K_s] and self.direction != (0, -1):  # S - down
            self.direction = (0, 1)
        elif keys[pygame.K_a] and self.direction != (1, 0):  # A - left
            self.direction = (-1, 0)
        elif keys[pygame.K_d] and self.direction != (-1, 0):  # D - right
            self.direction = (1, 0)
    
    def update(self):
        """Update game state"""
        if self.game_over:
            return
        
        # Move snake
        head_x, head_y = self.snake[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])
        
        # Check wall collision
        if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or 
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT):
            self.game_over = True
            return
        
        # Check self collision
        if new_head in self.snake:
            self.game_over = True
            return
        
        # Add new head
        self.snake.insert(0, new_head)
        
        # Check food collision
        food_eaten = False
        for i, food in enumerate(self.foods):
            if new_head[0] == food[0] and new_head[1] == food[1]:
                self.score += 10
                self.foods.pop(i)
                self.spawn_food()  # Spawn new food
                food_eaten = True
                break
        
        # Remove tail if no food eaten
        if not food_eaten:
            self.snake.pop()
    
    def draw_3d_food(self, x, y, color):
        """Draw food with 3D effect"""
        pixel_x = x * GRID_SIZE
        pixel_y = y * GRID_SIZE
        
        # Create shadow
        shadow_color = tuple(max(0, c - 100) for c in color)
        pygame.draw.circle(self.screen, shadow_color, 
                         (pixel_x + GRID_SIZE//2 + 2, pixel_y + GRID_SIZE//2 + 2), 
                         GRID_SIZE//2 - 2)
        
        # Main food circle
        pygame.draw.circle(self.screen, color, 
                         (pixel_x + GRID_SIZE//2, pixel_y + GRID_SIZE//2), 
                         GRID_SIZE//2 - 2)
        
        # Highlight
        highlight_color = tuple(min(255, c + 100) for c in color)
        pygame.draw.circle(self.screen, highlight_color, 
                         (pixel_x + GRID_SIZE//2 - 3, pixel_y + GRID_SIZE//2 - 3), 
                         GRID_SIZE//4)
    
    def render(self):
        """Render the game"""
        self.screen.fill(BLACK)
        
        # Draw snake
        for i, segment in enumerate(self.snake):
            x, y = segment
            pixel_x = x * GRID_SIZE
            pixel_y = y * GRID_SIZE
            
            # Snake head is brighter
            color = GREEN if i == 0 else DARK_GREEN
            pygame.draw.rect(self.screen, color, 
                           (pixel_x, pixel_y, GRID_SIZE-1, GRID_SIZE-1))
        
        # Draw food items with 3D effect
        for food in self.foods:
            x, y, color = food
            self.draw_3d_food(x, y, color)
        
        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Draw food count
        food_count_text = self.font.render(f"Food Items: {len(self.foods)}", True, WHITE)
        self.screen.blit(food_count_text, (10, 50))
        
        # Draw game over
        if self.game_over:
            game_over_text = self.font.render("GAME OVER! Press R to restart", True, WHITE)
            text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            self.screen.blit(game_over_text, text_rect)
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        print("Snake Game Controls: W/A/S/D to move, R to restart, ESC to quit")
        print("Collect the colorful food items to grow and increase your score!")
        
        running = True
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:  # Restart
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:  # Quit
                        running = False
            
            # Handle continuous input
            self.handle_input()
            
            # Update game
            self.update()
            
            # Render
            self.render()
            
            # Control game speed
            self.clock.tick(10)  # 10 FPS for smooth movement
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = SnakeGame()
    game.run()