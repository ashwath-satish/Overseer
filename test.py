import pygame
import random
import math

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60
SURVIVAL_TIME = 60000

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

LIGHT_BLUE = (150, 200, 255)
BLUE = (100, 150, 255)

GREEN = (100, 255, 100)

LIGHT_RED = (255, 150, 150)
RED = (255, 100, 100)

YELLOW = (255, 255, 100)
BROWN = (139, 69, 19)
PURPLE = (200, 100, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

class Character:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.size = 30
        self.happiness = 100
        self.perfect_temp = 60
        self.perfect_humidity = 50

    def update(self, temperature, humidity):
        temperature_diff = abs(temperature - self.perfect_temp)
        humidity_diff = abs(humidity - self.perfect_humidity)

        tolerance = 0.7  # degrees or % allowed before punishment

        temp_penalty = max(0, temperature_diff - tolerance)
        hum_penalty = max(0, humidity_diff - tolerance)
        
        if temp_penalty == 0 and hum_penalty == 0:
            self.happiness = min(100, self.happiness + 0.05)
        else:
            happiness_change = temp_penalty + hum_penalty
            self.happiness = max(0, self.happiness - 0.25 * happiness_change)

    def draw(self, screen):
        # Character color based on happiness
        if self.happiness >= 100:
            color = (0, 255, 0)  # Bright green for 100% happiness
        elif self.happiness >= 90:
            color = GREEN  # Regular green for 90%+ happiness
        elif self.happiness > 80:
            color = YELLOW
        elif self.happiness > 60:
            color = (255, 200, 100)
        elif self.happiness > 40:
            color = (255, 150, 100)
        elif self.happiness > 20:
            color = (255, 100, 100)
        else:
            color = RED

        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.size, 2)

        # Draw simple face
        eye_offset = 8
        pygame.draw.circle(screen, BLACK, (int(self.x - eye_offset), int(self.y - 5)), 3)
        pygame.draw.circle(screen, BLACK, (int(self.x + eye_offset), int(self.y - 5)), 3)

        # Mouth based on happiness
        if self.happiness >= 90:
            # Super happy face for 90%+ happiness
            pygame.draw.arc(screen, BLACK, (int(self.x - 10), int(self.y), 20, 15), 0, math.pi, 3)
        elif self.happiness > 60:
            # Happy mouth
            pygame.draw.arc(screen, BLACK, (int(self.x - 8), int(self.y), 16, 12), 0, math.pi, 2)
        elif self.happiness > 40:
            # Neutral mouth
            pygame.draw.line(screen, BLACK, (int(self.x - 8), int(self.y + 8)), (int(self.x + 8), int(self.y + 8)), 2)
        else:
            # Sad mouth
            pygame.draw.arc(screen, BLACK, (int(self.x - 8), int(self.y + 2), 16, 12), math.pi, 2 * math.pi, 2)
    
class Environment:
    def __init__(self):
        self.temperature = 60
        self.humidity = 50
        self.temp_drift = 0.5
        self.humidity_drift = 0.5
        self.last_fluctuation_time = pygame.time.get_ticks()
        self.fluctuation_interval = 500
        self.devices = {
            "temp_up_device": pygame.Rect(700,80,60,40),
            "temp_down_device": pygame.Rect(700,130,60,40),
            "hum_up_device": pygame.Rect(50, 400, 60, 40),
            "hum_down_device": pygame.Rect(50, 450, 60, 40)
        }
    
    def fluctuate(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_fluctuation_time >= self.fluctuation_interval:
            self.temperature += random.uniform(-self.temp_drift, self.temp_drift)
            self.humidity += random.uniform(-self.humidity_drift, self.humidity_drift)

            self.temperature = max(0, min(150, self.temperature))
            self.humidity = max(0, min(100, self.humidity))

            self.last_fluctuation_time = current_time

    def interact(self, pos):
        if self.devices["temp_up_device"].collidepoint(pos):
            self.temperature += 1
        elif self.devices["temp_down_device"].collidepoint(pos):
            self.temperature -= 1
        elif self.devices["hum_up_device"].collidepoint(pos):
            self.humidity += 1
        elif self.devices["hum_down_device"].collidepoint(pos):
            self.humidity -= 1

        self.temperature = max(0, min(150, self.temperature))
        self.humidity = max(0, min(100, self.humidity))

    def draw(self, screen):
        pygame.draw.rect(screen, LIGHT_RED, self.devices["temp_up_device"])
        pygame.draw.rect(screen, RED, self.devices["temp_down_device"])
        pygame.draw.rect(screen, LIGHT_BLUE, self.devices["hum_up_device"])
        pygame.draw.rect(screen, BLUE, self.devices["hum_down_device"])

        label_font = pygame.font.Font(None, 24)

        screen.blit(label_font.render("Temp +", True, BLACK), (self.devices["temp_up_device"].x + 5, self.devices["temp_up_device"].y + 10))
        screen.blit(label_font.render("Temp -", True, BLACK), (self.devices["temp_down_device"].x + 5, self.devices["temp_down_device"].y + 10))
        screen.blit(label_font.render("Hum +", True, BLACK), (self.devices["hum_up_device"].x + 5, self.devices["hum_up_device"].y + 10))
        screen.blit(label_font.render("Hum -", True, BLACK), (self.devices["hum_down_device"].x + 5, self.devices["hum_down_device"].y + 10))

class Game:
    def __init__(self):

        # Initialize Pygame
        pygame.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Overseer")
        self.clock = pygame.time.Clock()
        self.character = Character()
        self.environment = Environment()
        self.font = pygame.font.Font(None, 36)
        self.larger_font = pygame.font.Font(None, 64)
        self.smaller_font = pygame.font.Font(None, 24)
        self.start_time = pygame.time.get_ticks()
        self.gameWon = False
        self.gameLost = False
        self.running = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.gameWon or self.gameLost:
                    self.__init__()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.environment.interact(event.pos)

    def update(self):
        if not self.gameWon:
            self.environment.fluctuate()
            self.character.update(self.environment.temperature, self.environment.humidity)

            if self.character.happiness <= 0:
                self.gameLost = True
            
            elapsed = pygame.time.get_ticks() - self.start_time
            if elapsed >= SURVIVAL_TIME:
                self.gameWon = True

    def draw(self):
        self.screen.fill(WHITE)
        self.environment.draw(self.screen)
        self.character.draw(self.screen)
        self.draw_ui()

        if self.gameWon:
            self.draw_win()

        if self.gameLost:
            self.draw_loss()

        pygame.display.flip()
            
    def draw_ui(self):
        temp_text = self.font.render(f"Temp: {int(self.environment.temperature)}°", True, BLACK)
        hum_text = self.font.render(f"Humidity: {int(self.environment.humidity)}%", True, BLACK)
        happiness_text = self.font.render(f"Happiness: {int(self.character.happiness)}", True, BLACK)
        self.screen.blit(temp_text, (20,20))
        self.screen.blit(hum_text, (20,60))
        self.screen.blit(happiness_text, (20,100))

        elapsed = pygame.time.get_ticks() - self.start_time
        time_left = max(0, (SURVIVAL_TIME - elapsed)//1000)
        timer_text = self.font.render(f"Time Left: {time_left} seconds", True, BLACK)
        self.screen.blit(timer_text, (SCREEN_WIDTH - 320, 20))

        instructions1 = "Instructions:"
        instructions2 = "Help the character complete the game by adjusting the temperature and humidity."
        instructions3 = "Click on the +/- buttons to make the different factors go up or down."
        
        text1 = self.smaller_font.render(instructions1, True, DARK_GRAY)
        self.screen.blit(text1, (20, 600 ))

        text2 = self.smaller_font.render(instructions2, True, DARK_GRAY)
        self.screen.blit(text2, (20, 620 ))

        text3 = self.smaller_font.render(instructions3, True, DARK_GRAY)
        self.screen.blit(text3, (20, 640 ))

    def draw_win(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0,0))

        win_text = self.larger_font.render("You Win!", True, GREEN)
        restart_text = self.font.render("Press 'R' to restart the game", True, WHITE)

        self.screen.blit(win_text, win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20 )))
        self.screen.blit(restart_text, restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)))

    def draw_loss(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0,0))

        loss_text = self.larger_font.render("You Lost!", True, RED)
        restart_text = self.font.render("Press 'R' to restart the game", True, WHITE)

        self.screen.blit(loss_text, loss_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20)))
        self.screen.blit(restart_text, restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)))
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()

if __name__ == "__main__":
    Game().run()