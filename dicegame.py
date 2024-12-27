import pygame
from pygame.math import Vector2 as vec2

from constants import *
from isometric import *



# Initialize pygame
pygame.init()

# Base class
class DiceGame:
    def __init__(self):
        pygame.display.set_caption('Totally Orginal Dice Game')

        # Declare window display surface and screen surface
        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        self.camera = IsoCamera(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

        self.isometric = Isometric(self)
        self.isometric.load_blocks('level.png')
    
    def update(self):
        self.isometric.update()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]: self.camera.position.x += 1
        if keys[pygame.K_LEFT]: self.camera.position.x -= 1
        if keys[pygame.K_DOWN]: self.camera.position.y += 1
        if keys[pygame.K_UP]: self.camera.position.y -= 1

    def draw(self):
        self.screen.fill((0,0,0)) # Clear screen

        self.isometric.draw()


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