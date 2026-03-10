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
MAGNET_RED = (255, 0, 0)
MAGNET_BLUE = (0, 0, 255)

FOOD_COLORS = [RED, ORANGE, YELLOW, PINK, PURPLE, BLUE, BANANA_YELLOW, "MAGNET"]

class SnakeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake Game - LLM Workshop Demo")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        
        # Timing for smooth animation
        self.MOVE_TIME = 150  # milliseconds between grid moves
        self.move_timer = 0
        self.next_direction = (1, 0)
        
        self.reset_game()
    
    def reset_game(self):
        # Snake starts in the middle
        self.snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.prev_snake = list(self.snake)  # For interpolation
        self.direction = (1, 0)  # Moving right
        self.next_direction = (1, 0)
        self.score = 0
        self.game_over = False
        self.growth_pending = 0
        self.phasing_timer = 0  # Powerup duration in frames
        self.magnet_timer = 0   # Magnet duration in frames
        self.respawn_queue = []  # List of frame timers for food respawn
        self.move_timer = 0
        
        # Create multiple food items
        self.foods = []
        for _ in range(10):
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
                # RNG System: Regular (R,O,Y,P), Powerups (Purple, Blue), Banana, Magnet
                # Weights: Regular=20 each (80 total), Purple/Blue/Magnet=10 each, Banana=5
                weights = [20, 20, 20, 20, 10, 10, 5, 10]
                color = random.choices(FOOD_COLORS, weights=weights)[0]
                self.foods.append((x, y, color))
                break

    def handle_input(self):
        """Handle WASD and Arrow key input"""
        keys = pygame.key.get_pressed()
        
        # Buffer the next direction to prevent 180-turns during interpolation
        if (keys[pygame.K_w] or keys[pygame.K_UP]) and self.direction != (0, 1):
            self.next_direction = (0, -1)
        elif (keys[pygame.K_s] or keys[pygame.K_DOWN]) and self.direction != (0, -1):
            self.next_direction = (0, 1)
        elif (keys[pygame.K_a] or keys[pygame.K_LEFT]) and self.direction != (1, 0):
            self.next_direction = (-1, 0)
        elif (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and self.direction != (-1, 0):
            self.next_direction = (1, 0)
    
    def logic_step(self):
        """Run one step of game logic (grid move)"""
        if self.game_over:
            return

        self.direction = self.next_direction
        self.prev_snake = list(self.snake)
        
        # Decrement powerup timers
        if self.phasing_timer > 0:
            self.phasing_timer -= 1
        if self.magnet_timer > 0:
            self.magnet_timer -= 1

        # Calculate new head
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
        
        # Check food collision (HITBOX: Entire grid cell of the head)
        foods_eaten_count = 0
        for i in range(len(self.foods) - 1, -1, -1):
            fx, fy, fcolor = self.foods[i]
            # Wall-wrap aware coordinate difference
            dx = abs(new_head[0] - fx)
            dy = abs(new_head[1] - fy)
            if dx > GRID_WIDTH / 2: dx = GRID_WIDTH - dx
            if dy > GRID_HEIGHT / 2: dy = GRID_HEIGHT - dy
            
            # Hitbox check: if fruit center is within 1 grid unit of head center
            if dx < 1.0 and dy < 1.0: 
                self.eat_food(i, fcolor)
                foods_eaten_count += 1
        
        # Handle growth for multiple foods eaten in one step
        if foods_eaten_count > 0:
            # First food grows by 1 (handled by not popping), others add to pending
            self.growth_pending += (foods_eaten_count - 1)
            food_eaten = True
        else:
            food_eaten = False

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
            pass 
        elif self.growth_pending > 0:
            self.growth_pending -= 1
        else:
            self.snake.pop()

    def eat_food(self, index, color):
        """Handle food consumption logic and powerups"""
        if color == PURPLE:
            self.score += 30
            self.growth_pending += 2
        elif color == BLUE:
            self.score += 10
            self.phasing_timer = 100
        elif color == BANANA_YELLOW:
            target_len = max(1, (len(self.snake) - 1) - 3)
            while len(self.snake) > target_len:
                self.snake.pop()
        elif color == "MAGNET":
            self.score += 10
            self.magnet_timer = 133 # Reset timer to 20s
        else:
            self.score += 10
        
        if index < len(self.foods):
            self.foods.pop(index)
            self.respawn_queue.append(20)

    def update(self, dt):
        """Update game state with timing and smooth suction"""
        if self.game_over:
            return
            
        # Smooth Magnet Suction (60 FPS)
        if self.magnet_timer > 0:
            # Current smooth head position
            progress = self.move_timer / self.MOVE_TIME
            head_x = self.prev_snake[0][0] + (self.snake[0][0] - self.prev_snake[0][0]) * progress
            head_y = self.prev_snake[0][1] + (self.snake[0][1] - self.prev_snake[0][1]) * progress
            
            for i in range(len(self.foods)):
                fx, fy, fcolor = self.foods[i]
                dx = head_x - fx
                dy = head_y - fy
                
                # Handle wall wrap-around for suction direction
                if dx > GRID_WIDTH / 2: dx -= GRID_WIDTH
                if dx < -GRID_WIDTH / 2: dx += GRID_WIDTH
                if dy > GRID_HEIGHT / 2: dy -= GRID_HEIGHT
                if dy < -GRID_HEIGHT / 2: dy += GRID_HEIGHT
                
                dist = (dx**2 + dy**2)**0.5
                if dist < 5 and dist > 0.01:
                    # Smoothly glide towards center (head) - faster than snake
                    pull_speed = 0.015 * dt
                    # Limit move distance to avoid overshooting
                    move_dist = min(pull_speed, dist)
                    self.foods[i] = (fx + (dx/dist) * move_dist, 
                                     fy + (dy/dist) * move_dist, fcolor)

        self.move_timer += dt
        while self.move_timer >= self.MOVE_TIME:
            self.logic_step()
            self.move_timer -= self.MOVE_TIME

    def draw_banana_at(self, px, py):
        """Draw realistic banana at pixel position"""
        body = BANANA_YELLOW
        shadow = (210, 180, 0)
        highlight = (255, 255, 150)
        stem = (100, 70, 30)
        tip = (60, 40, 10)
        pygame.draw.ellipse(self.screen, body, (px + 4, py + 6, 12, 9))
        pygame.draw.ellipse(self.screen, body, (px + 2, py + 10, 8, 6))
        pygame.draw.arc(self.screen, shadow, (px + 2, py + 5, 14, 12), 3.4, 6.0, 3)
        pygame.draw.arc(self.screen, highlight, (px + 6, py + 7, 8, 5), 0.5, 3.0, 2)
        pygame.draw.line(self.screen, stem, (px + 14, py + 7), (px + 17, py + 4), 3)
        pygame.draw.rect(self.screen, tip, (px + 16, py + 3, 2, 2))
        pygame.draw.circle(self.screen, tip, (px + 3, py + 14), 2)

    def draw_magnet_at(self, px, py):
        """Draw magnet at pixel position"""
        pygame.draw.rect(self.screen, MAGNET_BLUE, (px + 4, py + 4, 4, 12))
        pygame.draw.rect(self.screen, MAGNET_RED, (px + 12, py + 4, 4, 12))
        pygame.draw.rect(self.screen, MAGNET_BLUE, (px + 4, py + 12, 6, 4))
        pygame.draw.rect(self.screen, MAGNET_RED, (px + 10, py + 12, 6, 4))
        pygame.draw.rect(self.screen, WHITE, (px + 4, py + 4, 4, 2))
        pygame.draw.rect(self.screen, WHITE, (px + 12, py + 4, 4, 2))

    def draw_3d_food_at(self, px, py, color):
        """Draw 3D food at pixel position"""
        shadow_color = tuple(max(0, c - 100) for c in color)
        pygame.draw.circle(self.screen, shadow_color, (px + 12, py + 12), 8)
        pygame.draw.circle(self.screen, color, (px + 10, py + 10), 8)
        highlight_color = tuple(min(255, c + 100) for c in color)
        pygame.draw.circle(self.screen, highlight_color, (px + 7, py + 7), 4)
    
    def render(self):
        """Render the game with smooth interpolation and magnet effects"""
        self.screen.fill(BLACK)
        
        # Interpolation progress (0.0 to 1.0)
        progress = self.move_timer / self.MOVE_TIME
        
        # Powerup effects
        snake_alpha = 255
        if self.phasing_timer > 0:
            if self.phasing_timer < 30: 
                if (pygame.time.get_ticks() // 100) % 2 == 0:
                    snake_alpha = 150
            else:
                if (pygame.time.get_ticks() // 400) % 2 == 0:
                    snake_alpha = 180

        # Draw snake segments with interpolation
        for i in range(len(self.snake)):
            curr = self.snake[i]
            if i < len(self.prev_snake):
                prev = self.prev_snake[i]
            else:
                prev = self.prev_snake[-1]
            
            # Smooth position calculation
            dx = curr[0] - prev[0]
            dy = curr[1] - prev[1]
            
            if abs(dx) > 1: # Wrapped around X
                interp_x = curr[0] if progress > 0.5 else prev[0]
            else:
                interp_x = prev[0] + dx * progress
                
            if abs(dy) > 1: # Wrapped around Y
                interp_y = curr[1] if progress > 0.5 else prev[1]
            else:
                interp_y = prev[1] + dy * progress

            pixel_x = interp_x * GRID_SIZE
            pixel_y = interp_y * GRID_SIZE
            
            # Draw magnet bubble around head
            if i == 0 and self.magnet_timer > 0:
                import math
                center_x = pixel_x + GRID_SIZE // 2
                center_y = pixel_y + GRID_SIZE // 2
                radius = 5 * GRID_SIZE
                angle_offset = pygame.time.get_ticks() / 1000.0 # Much slower rotation
                
                # Flashing logic for last 5 seconds (approx 33 logic steps)
                show_bubble = True
                if self.magnet_timer < 33:
                    if (pygame.time.get_ticks() // 200) % 2 == 0:
                        show_bubble = False
                
                if show_bubble:
                    # Draw dashed spinning circle
                    for a in range(0, 360, 30):
                        start_angle = math.radians(a + angle_offset * 100)
                        end_angle = math.radians(a + 15 + angle_offset * 100)
                        pygame.draw.arc(self.screen, (100, 100, 255), 
                                       (center_x - radius, center_y - radius, radius*2, radius*2), 
                                       start_angle, end_angle, 2)

            color = GREEN if i == 0 else DARK_GREEN
            if self.phasing_timer > 0:
                color = (max(0, color[0]-100), max(0, color[1]-100), 255)
                color = tuple(int(c * (snake_alpha / 255)) for c in color)

            pygame.draw.rect(self.screen, color, 
                           (pixel_x, pixel_y, GRID_SIZE-1, GRID_SIZE-1))
        
        # Draw food items
        for food in self.foods:
            x, y, color = food
            render_x, render_y = x * GRID_SIZE, y * GRID_SIZE

            if color == BANANA_YELLOW:
                self.draw_banana_at(render_x, render_y)
            elif color == "MAGNET":
                self.draw_magnet_at(render_x, render_y)
            else:
                self.draw_3d_food_at(render_x, render_y, color)
        
        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Draw game over
        if self.game_over:
            game_over_text = self.font.render("GAME OVER! Press R to restart", True, WHITE)
            text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            self.screen.blit(game_over_text, text_rect)
        
        pygame.display.flip()

    def draw_banana_at(self, px, py):
        """Draw realistic banana at pixel position"""
        body = BANANA_YELLOW
        shadow = (210, 180, 0)
        highlight = (255, 255, 150)
        stem = (100, 70, 30)
        tip = (60, 40, 10)
        pygame.draw.ellipse(self.screen, body, (px + 4, py + 6, 12, 9))
        pygame.draw.ellipse(self.screen, body, (px + 2, py + 10, 8, 6))
        pygame.draw.arc(self.screen, shadow, (px + 2, py + 5, 14, 12), 3.4, 6.0, 3)
        pygame.draw.arc(self.screen, highlight, (px + 6, py + 7, 8, 5), 0.5, 3.0, 2)
        pygame.draw.line(self.screen, stem, (px + 14, py + 7), (px + 17, py + 4), 3)
        pygame.draw.rect(self.screen, tip, (px + 16, py + 3, 2, 2))
        pygame.draw.circle(self.screen, tip, (px + 3, py + 14), 2)

    def draw_magnet_at(self, px, py):
        """Draw magnet at pixel position"""
        pygame.draw.rect(self.screen, MAGNET_BLUE, (px + 4, py + 4, 4, 12))
        pygame.draw.rect(self.screen, MAGNET_RED, (px + 12, py + 4, 4, 12))
        pygame.draw.rect(self.screen, MAGNET_BLUE, (px + 4, py + 12, 6, 4))
        pygame.draw.rect(self.screen, MAGNET_RED, (px + 10, py + 12, 6, 4))
        pygame.draw.rect(self.screen, WHITE, (px + 4, py + 4, 4, 2))
        pygame.draw.rect(self.screen, WHITE, (px + 12, py + 4, 4, 2))

    def draw_3d_food_at(self, px, py, color):
        """Draw 3D food at pixel position"""
        shadow_color = tuple(max(0, c - 100) for c in color)
        pygame.draw.circle(self.screen, shadow_color, (px + 12, py + 12), 8)
        pygame.draw.circle(self.screen, color, (px + 10, py + 10), 8)
        highlight_color = tuple(min(255, c + 100) for c in color)
        pygame.draw.circle(self.screen, highlight_color, (px + 7, py + 7), 4)
    
    def run(self):
        """Main game loop at 60 FPS for smooth rendering"""
        print("Snake Game Controls: W/A/S/D or Arrows to move, R to restart, ESC to quit")
        print("Game Features: Walls wrap around. Blue fruit lets you pass through your own body!")
        
        running = True
        while running:
            dt = self.clock.tick(60) # 60 FPS
            
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
            
            # Update game logic based on MOVE_TIME
            self.update(dt)
            
            # Render smoothly at 60 FPS
            self.render()
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = SnakeGame()
    game.run()