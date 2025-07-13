import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (100, 150, 255)
GREEN = (100, 255, 100)
RED = (255, 100, 100)
YELLOW = (255, 255, 100)
BROWN = (139, 69, 19)
PURPLE = (200, 100, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

class Character:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.size = 20
        self.happiness = 50  # 0-100 scale
        self.max_happiness = 100
        self.speed = 2
        self.preferred_temp = 70  # Preferred temperature
        self.preferred_humidity = 60  # Preferred humidity
        self.last_move_time = 0
        self.move_interval = 1000  # milliseconds

    def update(self, environment):
        current_time = pygame.time.get_ticks()

        # AI movement - character tries to find better conditions
        if current_time - self.last_move_time > self.move_interval:
            self.ai_move(environment)
            self.last_move_time = current_time

        # Apply velocity
        self.x += self.vx
        self.y += self.vy

        # Apply friction
        self.vx *= 0.95
        self.vy *= 0.95

        # Boundary checking
        if self.x < self.size:
            self.x = self.size
            self.vx = 0
        elif self.x > SCREEN_WIDTH - self.size:
            self.x = SCREEN_WIDTH - self.size
            self.vx = 0

        if self.y < self.size:
            self.y = self.size
            self.vy = 0
        elif self.y > SCREEN_HEIGHT - self.size:
            self.y = SCREEN_HEIGHT - self.size
            self.vy = 0

        # Update happiness based on environment
        self.update_happiness(environment)

    def ai_move(self, environment):
        # Simple AI: move towards better conditions
        best_x, best_y = self.x, self.y
        best_score = self.evaluate_position(self.x, self.y, environment)

        # Check nearby positions
        for dx in [-50, 0, 50]:
            for dy in [-50, 0, 50]:
                if dx == 0 and dy == 0:
                    continue
                test_x = max(self.size, min(SCREEN_WIDTH - self.size, self.x + dx))
                test_y = max(self.size, min(SCREEN_HEIGHT - self.size, self.y + dy))
                score = self.evaluate_position(test_x, test_y, environment)
                if score > best_score:
                    best_score = score
                    best_x, best_y = test_x, test_y

        # Move towards better position
        if best_x != self.x or best_y != self.y:
            dx = best_x - self.x
            dy = best_y - self.y
            distance = math.sqrt(dx*dx + dy*dy)
            if distance > 0:
                self.vx += (dx / distance) * self.speed
                self.vy += (dy / distance) * self.speed

    def evaluate_position(self, x, y, environment):
        temp = environment.get_temperature(x, y)
        humidity = environment.get_humidity(x, y)

        temp_score = 100 - abs(temp - self.preferred_temp)
        humidity_score = 100 - abs(humidity - self.preferred_humidity)

        return temp_score + humidity_score

    def update_happiness(self, environment):
        temp = environment.get_temperature(self.x, self.y)
        humidity = environment.get_humidity(self.x, self.y)

        # Calculate happiness based on how close conditions are to preferred
        temp_happiness = max(0, 100 - abs(temp - self.preferred_temp) * 2)
        humidity_happiness = max(0, 100 - abs(humidity - self.preferred_humidity) * 2)

        target_happiness = (temp_happiness + humidity_happiness) / 2

        # Gradually adjust happiness
        if target_happiness > self.happiness:
            self.happiness = min(self.max_happiness, self.happiness + 0.5)
        else:
            self.happiness = max(0, self.happiness - 0.3)

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
        self.temperature_map = [[random.randint(20, 100) for _ in range(50)] for _ in range(35)]
        self.humidity_map = [[random.randint(20, 100) for _ in range(50)] for _ in range(35)]
        self.heat_sources = []
        self.cooling_sources = []
        self.humidifiers = []
        self.dehumidifiers = []

    def get_temperature(self, x, y):
        # Base temperature from map
        map_x = int(x / (SCREEN_WIDTH / 50))
        map_y = int(y / (SCREEN_HEIGHT / 35))
        map_x = max(0, min(49, map_x))
        map_y = max(0, min(34, map_y))

        base_temp = self.temperature_map[map_y][map_x]

        # Add effects from heat/cooling sources
        for source in self.heat_sources:
            distance = math.sqrt((x - source[0])**2 + (y - source[1])**2)
            if distance < 100:
                base_temp += (100 - distance) * 0.3

        for source in self.cooling_sources:
            distance = math.sqrt((x - source[0])**2 + (y - source[1])**2)
            if distance < 100:
                base_temp -= (100 - distance) * 0.3

        return max(0, min(150, base_temp))

    def get_humidity(self, x, y):
        # Base humidity from map
        map_x = int(x / (SCREEN_WIDTH / 50))
        map_y = int(y / (SCREEN_HEIGHT / 35))
        map_x = max(0, min(49, map_x))
        map_y = max(0, min(34, map_y))

        base_humidity = self.humidity_map[map_y][map_x]

        # Add effects from humidifiers/dehumidifiers
        for source in self.humidifiers:
            distance = math.sqrt((x - source[0])**2 + (y - source[1])**2)
            if distance < 100:
                base_humidity += (100 - distance) * 0.2

        for source in self.dehumidifiers:
            distance = math.sqrt((x - source[0])**2 + (y - source[1])**2)
            if distance < 100:
                base_humidity -= (100 - distance) * 0.2

        return max(0, min(100, base_humidity))

    def add_heat_source(self, x, y):
        self.heat_sources.append((x, y))

    def add_cooling_source(self, x, y):
        self.cooling_sources.append((x, y))

    def add_humidifier(self, x, y):
        self.humidifiers.append((x, y))

    def add_dehumidifier(self, x, y):
        self.dehumidifiers.append((x, y))

    def remove_source_at(self, x, y, radius=30):
        # Remove sources within radius
        self.heat_sources = [s for s in self.heat_sources if math.sqrt((s[0] - x)**2 + (s[1] - y)**2) > radius]
        self.cooling_sources = [s for s in self.cooling_sources if math.sqrt((s[0] - x)**2 + (s[1] - y)**2) > radius]
        self.humidifiers = [s for s in self.humidifiers if math.sqrt((s[0] - x)**2 + (s[1] - y)**2) > radius]
        self.dehumidifiers = [s for s in self.dehumidifiers if math.sqrt((s[0] - x)**2 + (s[1] - y)**2) > radius]

    def draw(self, screen):
        # Draw temperature map as background
        for y in range(35):
            for x in range(50):
                temp = self.temperature_map[y][x]
                color_intensity = int((temp / 100) * 255)
                color = (color_intensity, 0, 255 - color_intensity)
                rect = pygame.Rect(x * 20, y * 20, 20, 20)
                pygame.draw.rect(screen, color, rect)

        # Draw sources
        for source in self.heat_sources:
            pygame.draw.circle(screen, RED, source, 20)
            pygame.draw.circle(screen, BLACK, source, 20, 2)

        for source in self.cooling_sources:
            pygame.draw.circle(screen, BLUE, source, 20)
            pygame.draw.circle(screen, BLACK, source, 20, 2)

        for source in self.humidifiers:
            pygame.draw.circle(screen, GREEN, source, 15)
            pygame.draw.circle(screen, BLACK, source, 15, 2)

        for source in self.dehumidifiers:
            pygame.draw.circle(screen, BROWN, source, 15)
            pygame.draw.circle(screen, BLACK, source, 15, 2)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Environmental Happiness Game")
        self.clock = pygame.time.Clock()

        self.character = Character(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.environment = Environment()
        self.current_tool = "heat"  # heat, cool, humidify, dehumidify, remove
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        self.game_won = False
        self.win_time = 0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game_won:
                    # Restart game
                    self.character = Character(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                    self.environment = Environment()
                    self.game_won = False
                    self.win_time = 0
                elif event.key == pygame.K_1:
                    self.current_tool = "heat"
                elif event.key == pygame.K_2:
                    self.current_tool = "cool"
                elif event.key == pygame.K_3:
                    self.current_tool = "humidify"
                elif event.key == pygame.K_4:
                    self.current_tool = "dehumidify"
                elif event.key == pygame.K_5:
                    self.current_tool = "remove"

            if event.type == pygame.MOUSEBUTTONDOWN and not self.game_won:
                if event.button == 1:  # Left click
                    x, y = event.pos
                    if self.current_tool == "heat":
                        self.environment.add_heat_source(x, y)
                    elif self.current_tool == "cool":
                        self.environment.add_cooling_source(x, y)
                    elif self.current_tool == "humidify":
                        self.environment.add_humidifier(x, y)
                    elif self.current_tool == "dehumidify":
                        self.environment.add_dehumidifier(x, y)
                    elif self.current_tool == "remove":
                        self.environment.remove_source_at(x, y)

        return True

    def update(self):
        self.character.update(self.environment)

        # Check for win condition
        if self.character.happiness >= 100 and not self.game_won:
            self.game_won = True
            self.win_time = pygame.time.get_ticks()

    def draw(self):
        self.screen.fill(WHITE)

        # Draw environment
        self.environment.draw(self.screen)

        # Draw character
        self.character.draw(self.screen)

        # Draw UI
        self.draw_ui()

        # Draw win message if game is won
        if self.game_won:
            self.draw_win_message()

        pygame.display.flip()

    def draw_ui(self):
        # Happiness bar
        bar_width = 200
        bar_height = 20
        bar_x = 10
        bar_y = 10

        # Background
        pygame.draw.rect(self.screen, GRAY, (bar_x, bar_y, bar_width, bar_height))

        # Happiness fill
        fill_width = int((self.character.happiness / 100) * bar_width)
        if self.character.happiness > 80:
            fill_color = GREEN
        elif self.character.happiness > 60:
            fill_color = YELLOW
        elif self.character.happiness > 40:
            fill_color = (255, 200, 100)
        else:
            fill_color = RED

        pygame.draw.rect(self.screen, fill_color, (bar_x, bar_y, fill_width, bar_height))
        pygame.draw.rect(self.screen, BLACK, (bar_x, bar_y, bar_width, bar_height), 2)

        # Happiness text
        happiness_text = self.font.render(f"Happiness: {int(self.character.happiness)}%", True, BLACK)
        self.screen.blit(happiness_text, (bar_x, bar_y + 30))

        # Current conditions
        temp = self.environment.get_temperature(self.character.x, self.character.y)
        humidity = self.environment.get_humidity(self.character.x, self.character.y)

        temp_text = self.font.render(f"Temperature: {int(temp)}°F (wants {self.character.preferred_temp}°F)", True, BLACK)
        humidity_text = self.font.render(f"Humidity: {int(humidity)}% (wants {self.character.preferred_humidity}%)", True, BLACK)

        self.screen.blit(temp_text, (bar_x, bar_y + 70))
        self.screen.blit(humidity_text, (bar_x, bar_y + 100))

        # Tool instructions
        instructions = [
            "Controls:",
            "1 - Heat Source (Red)",
            "2 - Cooling Source (Blue)",
            "3 - Humidifier (Green)",
            "4 - Dehumidifier (Brown)",
            "5 - Remove Tool",
            f"Current Tool: {self.current_tool.title()}"
        ]

        for i, instruction in enumerate(instructions):
            color = YELLOW if i == len(instructions) - 1 else BLACK
            text = self.font.render(instruction, True, color)
            self.screen.blit(text, (bar_x, bar_y + 140 + i * 25))

    def draw_win_message(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        # Main win message
        win_text = self.big_font.render("YOU WIN!", True, GREEN)
        text_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(win_text, text_rect)

        # Big smiley face
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2 + 50
        face_radius = 60

        # Face circle
        pygame.draw.circle(self.screen, GREEN, (center_x, center_y), face_radius)
        pygame.draw.circle(self.screen, BLACK, (center_x, center_y), face_radius, 4)

        # Eyes
        eye_offset = 20
        pygame.draw.circle(self.screen, BLACK, (center_x - eye_offset, center_y - 15), 8)
        pygame.draw.circle(self.screen, BLACK, (center_x + eye_offset, center_y - 15), 8)

        # Big smile
        pygame.draw.arc(self.screen, BLACK, (center_x - 30, center_y - 10, 60, 40), 0, math.pi, 6)

        # Restart instruction
        restart_text = self.font.render("Press R to restart", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150))
        self.screen.blit(restart_text, restart_rect)

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
