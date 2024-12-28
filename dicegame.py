import pygame
from pygame.math import Vector2 as vec2

from constants import *
from isometric import *



# Initialize pygame
pygame.init()
pygame.mixer.init()



# Base class
class DiceGame:
    def __init__(self):
        pygame.display.set_caption('Totally Orginal Dice Game')

        # Declare window display surface and screen surface
        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        self.isometric = Isometric(self)
        self.isometric.load_blocks('img/level.png')

        self.camera = IsoCamera(self, pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        self.die = IsoDie(self, vec3(10,10,1), DieLayout(0,1,0,1,0,1))
        self.isometric.isos.append(self.die)

        self.sounds = {
            'step':pygame.mixer.Sound('sfx/step.wav'),
            'pink':pygame.mixer.Sound('sfx/pink.ogg'),
        }
        self.sounds['pink'].play(-1)
    
    def update(self):
        self.isometric.update()
        self.die.update()
        self.camera.update()

    def draw(self):
        self.screen.fill((12,13,20)) # Clear screen

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