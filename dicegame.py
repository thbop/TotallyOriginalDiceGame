import json
import pygame
from pygame.math import Vector2 as vec2

from constants import *
from text import *
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

        self.sounds = {
            'step':pygame.mixer.Sound('sfx/step.wav'),
            'pink':pygame.mixer.Sound('sfx/pink.ogg'),
            'type':pygame.mixer.Sound('sfx/type.wav'),
            'reset':pygame.mixer.Sound('sfx/reset.wav'),
            'win':pygame.mixer.Sound('sfx/win.wav'),
        }
        self.sounds['pink'].play(-1)

        self.text_manager = TextManager(self)

        self.die: IsoDie
        self.isometric = Isometric(self)
        self.load(0)
        

        self.camera = IsoCamera(self, pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
    
    def load(self, lvl):
        with open('levels/dat.json') as f:
            data = json.load(f)[lvl]
        
        self.lvl_id = lvl
        self.isometric.load(f'levels/{self.lvl_id}.png')
        self.die.layout = DieLayout.fromlist(data['die_layout'])
        self.text_manager.load(data['texts'])

        if self.lvl_id:
            self.sounds['win'].play()
    
    def update(self):
        self.text_manager.update()
        self.isometric.update()
        self.die.update(self.isometric.isos)
        self.camera.update()

    def draw(self):
        self.screen.fill((12,13,20)) # Clear screen

        self.isometric.draw()

        self.text_manager.draw()
        self.text_manager.blit(f'LEVEL:{self.lvl_id}', vec2(5,5))

    def run(self):
        running = True
        clock = pygame.time.Clock() # To enforce FPS

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: # Check if window is exited
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r or event.key == pygame.K_SPACE:
                        self.isometric.load(f'levels/{self.lvl_id}.png')
                        self.sounds['reset'].play()
            
            self.update()
            self.draw()

            # Scale screen to fit window and blit, then update window
            pygame.transform.scale(self.screen, (WINDOW_WIDTH, WINDOW_HEIGHT), self.window)
            pygame.display.flip()
            clock.tick(FPS)



if __name__ == '__main__':
    dc = DiceGame()
    dc.run()