import pygame
from pygame.math import Vector2 as vec2

# Constants
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 200
FPS = 60

# Initialize pygame
pygame.init()

# Base class
class DiceGame:
    def __init__(self):
        pygame.display.set_caption('Totally Orginal Dice Game')

        # Declare window display surface and screen surface
        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    def update(self):
        pass

    def draw(self):
        self.screen.fill((0,0,0)) # Clear screen

        pygame.draw.rect(self.screen, (255, 0, 0), (10, 10, 10, 10))

    def run(self):
        running = True
        clock = pygame.time.Clock() # To enforce FPS

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: # Check if window is exited
                    running = False
            
            self.update()
            self.draw()

            # Scale screen to fit window and blit, then update window
            pygame.transform.scale(self.screen, (WINDOW_WIDTH, WINDOW_HEIGHT), self.window)
            pygame.display.flip()
            clock.tick(FPS)



if __name__ == '__main__':
    dc = DiceGame()
    dc.run()