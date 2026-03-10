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
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 760
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
BLUE = (0, 0, 255)
BANANA_YELLOW = (255, 225, 53)

FOOD_COLORS = [RED, ORANGE, YELLOW, PINK, PURPLE, BLUE, BANANA_YELLOW]

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
        self.growth_pending = 0
        self.phasing_timer = 0  # Powerup duration in frames
        self.respawn_queue = []  # List of frame timers for food respawn
        
        # Create multiple food items
        self.foods = []
        for _ in range(6):
            self.spawn_food()
    
    def spawn_food(self):
        """Spawn a food item at a random location not occupied by snake or other food"""
        max_attempts = 100
        for _ in range(max_attempts):
            # Avoid the outermost edges (0 and max-1)
            x = random.randint(1, GRID_WIDTH - 2)
            y = random.randint(1, GRID_HEIGHT - 2)
            
            # Check if position is free
            if (x, y) not in self.snake and not any((x, y) == food[:2] for food in self.foods):
                # RNG System: Regular (R,O,Y,P), Powerups (Purple, Blue), Banana
                # Weights: Regular=20 each (80 total), Purple/Blue=10 each, Banana=5
                weights = [20, 20, 20, 20, 10, 10, 5]
                color = random.choices(FOOD_COLORS, weights=weights)[0]
                self.foods.append((x, y, color))
                break
    
    def handle_input(self):
        """Handle WASD and Arrow key input"""
        keys = pygame.key.get_pressed()
        
        # Up (W or Up Arrow)
        if (keys[pygame.K_w] or keys[pygame.K_UP]) and self.direction != (0, 1):
            self.direction = (0, -1)
        # Down (S or Down Arrow)
        elif (keys[pygame.K_s] or keys[pygame.K_DOWN]) and self.direction != (0, -1):
            self.direction = (0, 1)
        # Left (A or Left Arrow)
        elif (keys[pygame.K_a] or keys[pygame.K_LEFT]) and self.direction != (1, 0):
            self.direction = (-1, 0)
        # Right (D or Right Arrow)
        elif (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and self.direction != (-1, 0):
            self.direction = (1, 0)
    
    def update(self):
        """Update game state"""
        if self.game_over:
            return
        
        # Decrement powerup timer
        if self.phasing_timer > 0:
            self.phasing_timer -= 1

        # Move snake
        head_x, head_y = self.snake[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])
        
        # Permanent wall wrap-around logic
        new_head = (new_head[0] % GRID_WIDTH, new_head[1] % GRID_HEIGHT)
        
        # Check self collision (Disabled if phasing powerup is active)
        if self.phasing_timer == 0:
            if new_head in self.snake:
                self.game_over = True
                return
        
        # Add new head
        self.snake.insert(0, new_head)
        
        # Check food collision
        food_eaten = False
        for i, food in enumerate(self.foods):
            if new_head[0] == food[0] and new_head[1] == food[1]:
                # Powerups
                if food[2] == PURPLE:
                    self.score += 30
                    self.growth_pending += 2
                elif food[2] == BLUE:
                    self.score += 10
                    self.phasing_timer = 150  # 15 seconds at 10 FPS
                elif food[2] == BANANA_YELLOW:
                    # Lose 3 units of length
                    target_len = max(1, (len(self.snake) - 1) - 3)
                    while len(self.snake) > target_len:
                        self.snake.pop()
                    food_eaten = True # Prevent normal growth
                else:
                    self.score += 10
                
                self.foods.pop(i)
                # Delay respawn by 3 seconds (30 frames at 10 FPS)
                self.respawn_queue.append(30)
                food_eaten = True
                break

        # Process respawn queue
        new_respawn_queue = []
        for timer in self.respawn_queue:
            if timer > 1:
                new_respawn_queue.append(timer - 1)
            else:
                self.spawn_food()
        self.respawn_queue = new_respawn_queue

        # Remove tail if no food eaten and no pending growth
        if food_eaten:
            pass # Already grew (or shrunk)
        elif self.growth_pending > 0:
            self.growth_pending -= 1 # Grow by 1 this move
        else:
            self.snake.pop() # Normal move, no growth

    def draw_banana(self, x, y):
        """Draw a more realistic banana shape"""
        px = x * GRID_SIZE
        py = y * GRID_SIZE
        
        # Colors
        body = BANANA_YELLOW
        shadow = (210, 180, 0)
        highlight = (255, 255, 150)
        stem = (100, 70, 30)
        tip = (60, 40, 10)

        # Draw curved segments to give it volume and shape
        # Main body segments
        pygame.draw.ellipse(self.screen, body, (px + 4, py + 6, 12, 9))
        pygame.draw.ellipse(self.screen, body, (px + 2, py + 10, 8, 6))
        
        # Shadow for depth (bottom curve)
        pygame.draw.arc(self.screen, shadow, (px + 2, py + 5, 14, 12), 3.4, 6.0, 3)
        
        # Highlight for shine (top curve)
        pygame.draw.arc(self.screen, highlight, (px + 6, py + 7, 8, 5), 0.5, 3.0, 2)
        
        # Stem (Top end)
        pygame.draw.line(self.screen, stem, (px + 14, py + 7), (px + 17, py + 4), 3)
        pygame.draw.rect(self.screen, tip, (px + 16, py + 3, 2, 2))
        
        # Bottom tip (Flower end)
        pygame.draw.circle(self.screen, tip, (px + 3, py + 14), 2)

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
        
        # Subtle pulsing/flashing logic for phasing powerup (never invisible)
        snake_alpha = 255
        if self.phasing_timer > 0:
            # Last 5 seconds (50 frames) pulse faster
            if self.phasing_timer < 50:
                # Pulse between 100 and 255 alpha
                if (pygame.time.get_ticks() // 100) % 2 == 0:
                    snake_alpha = 150
            else:
                # Pulse slower
                if (pygame.time.get_ticks() // 400) % 2 == 0:
                    snake_alpha = 180

        # Draw snake
        for i, segment in enumerate(self.snake):
            x, y = segment
            pixel_x = x * GRID_SIZE
            pixel_y = y * GRID_SIZE
            
            # Snake head is brighter
            color = GREEN if i == 0 else DARK_GREEN
            
            # If phasing, make it blueish and apply alpha pulsing
            if self.phasing_timer > 0:
                color = (max(0, color[0]-100), max(0, color[1]-100), 255)
                # Simulating alpha by blending with background (BLACK)
                color = tuple(int(c * (snake_alpha / 255)) for c in color)

            pygame.draw.rect(self.screen, color, 
                           (pixel_x, pixel_y, GRID_SIZE-1, GRID_SIZE-1))
        
        # Draw food items with 3D effect
        for food in self.foods:
            x, y, color = food
            if color == BANANA_YELLOW:
                self.draw_banana(x, y)
            else:
                self.draw_3d_food(x, y, color)
        
        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Draw game over
        if self.game_over:
            game_over_text = self.font.render("GAME OVER! Press R to restart", True, WHITE)
            text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            self.screen.blit(game_over_text, text_rect)
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        print("Snake Game Controls: W/A/S/D or Arrows to move, R to restart, ESC to quit")
        print("Game Features: Walls wrap around. Blue fruit lets you pass through your own body!")
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