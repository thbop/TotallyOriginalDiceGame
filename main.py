import sys, platform

mobile = False
if sys.platform == "emscripten":
    platform.window.canvas.style.imageRendering = "pixelated"
    import js
    user_agent = js.window.navigator.userAgent
    mobile = any(mobile_str in user_agent for mobile_str in ["Mobi", "Android", "iPhone", "iPad"])

import json
import asyncio
import pygame
from pygame.math import Vector2 as vec2

from constants import *
from text import *
from isometric import *
from backgrounds import *


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

        self.backgrounds = {
            'classic': BackgroundColor(self, (12,13,20)),
            'stars': BackgroundStars(self)
        }
        self.current_background = 'classic'

        self.sounds = {
            'step':pygame.mixer.Sound('sfx/step.wav'),
            'pink':pygame.mixer.Sound('sfx/pink.ogg'),
            'stars':pygame.mixer.Sound('sfx/stars.ogg'),
            'type':pygame.mixer.Sound('sfx/type.wav'),
            'reset':pygame.mixer.Sound('sfx/reset.wav'),
            'win':pygame.mixer.Sound('sfx/win.wav'),
            'invalid':pygame.mixer.Sound('sfx/invalid.wav'),
            'blip':pygame.mixer.Sound('sfx/blip.wav'),
        }
        self.sounds['pink'].play(-1)

        self.text_manager = TextManager(self)

        if mobile:
            self.touch_control_rects = [
                pygame.Rect(SCREEN_WIDTH-TOUCH_SIZE-TOUCH_PADDING, SCREEN_HEIGHT-TOUCH_SIZE-TOUCH_PADDING, TOUCH_SIZE, TOUCH_SIZE),
                pygame.Rect(SCREEN_WIDTH-(TOUCH_SIZE+TOUCH_PADDING)*2, SCREEN_HEIGHT-(TOUCH_SIZE+TOUCH_PADDING)*2, TOUCH_SIZE, TOUCH_SIZE),
                pygame.Rect(SCREEN_WIDTH-(TOUCH_SIZE+TOUCH_PADDING)*2, SCREEN_HEIGHT-TOUCH_SIZE-TOUCH_PADDING, TOUCH_SIZE, TOUCH_SIZE),
                pygame.Rect(SCREEN_WIDTH-TOUCH_SIZE-TOUCH_PADDING, SCREEN_HEIGHT-(TOUCH_SIZE+TOUCH_PADDING)*2, TOUCH_SIZE, TOUCH_SIZE),
                pygame.Rect(TOUCH_PADDING, SCREEN_HEIGHT-TOUCH_SIZE-TOUCH_PADDING, TOUCH_SIZE, TOUCH_SIZE),
            ]

        self.die: IsoDie
        self.isometric = Isometric(self)
        self.load(0)
        
        self.camera = IsoCamera(self, pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
    
    def load(self, lvl):
        with open('levels/dat.json') as f:
            data = json.load(f)[lvl]
        
        
        self.lvl_id = lvl
        self.current_background = data['background']

        pygame.mixer.stop()
        if data['music']:
            for m in data['music']:
                self.sounds[m].play(-1)

        self.isometric.load(f'levels/{self.lvl_id}.png')
        self.die.layout = DieLayout.fromlist(data['die_layout'])
        self.die.update_tex()
        self.text_manager.load(data['texts'])

    
    def reset(self, sfx='reset'):
        with open('levels/dat.json') as f:
            data = json.load(f)[self.lvl_id]
        self.die.layout = DieLayout.fromlist(data['die_layout'])
        self.die.update_tex()
        self.die.position = self.die.default_position.copy()
        self.sounds[sfx].play()
    
    def process_touch_controls(self, mouse_pos: vec2):
        if self.touch_control_rects[0].collidepoint(mouse_pos):
            self.die.move_right()
        if self.touch_control_rects[1].collidepoint(mouse_pos):
            self.die.move_left()
        if self.touch_control_rects[2].collidepoint(mouse_pos):
            self.die.move_front()
        if self.touch_control_rects[3].collidepoint(mouse_pos):
            self.die.move_back()
        if self.touch_control_rects[4].collidepoint(mouse_pos):
            self.reset()
    
    def update(self):
        self.text_manager.update()
        self.isometric.update()
        # print(self.die.layout)
        self.camera.update()
        self.backgrounds[self.current_background].update()
    
    def draw_move_options(self):
        self.screen.blit(pygame.transform.scale(self.die.faces[self.die.layout.back], (MV_OP_SIZE, MV_OP_SIZE)), (SCREEN_WIDTH-MV_OP_SIZE-MV_OP_PADDING, MV_OP_PADDING))
        pygame.draw.rect(self.screen, (255,255,255), [SCREEN_WIDTH-MV_OP_SIZE-MV_OP_PADDING-1, 1, MV_OP_SIZE+2, MV_OP_SIZE+2],1)
        self.screen.blit(pygame.transform.scale(self.die.faces[self.die.layout.left], (MV_OP_SIZE, MV_OP_SIZE)), (SCREEN_WIDTH-(MV_OP_SIZE+MV_OP_PADDING)*2, MV_OP_PADDING))
        pygame.draw.rect(self.screen, (255,255,255), [SCREEN_WIDTH-(MV_OP_SIZE+MV_OP_PADDING)*2-1, 1, MV_OP_SIZE+2, MV_OP_SIZE+2],1)
        self.screen.blit(pygame.transform.scale(self.die.faces[self.die.layout.right], (MV_OP_SIZE, MV_OP_SIZE)), (SCREEN_WIDTH-MV_OP_SIZE-MV_OP_PADDING, MV_OP_SIZE+MV_OP_PADDING*2))
        pygame.draw.rect(self.screen, (255,255,255), [SCREEN_WIDTH-MV_OP_SIZE-MV_OP_PADDING-1, MV_OP_SIZE+MV_OP_PADDING+1, MV_OP_SIZE+2, MV_OP_SIZE+2],1)
        self.screen.blit(pygame.transform.scale(self.die.faces[self.die.layout.front], (MV_OP_SIZE, MV_OP_SIZE)), (SCREEN_WIDTH-(MV_OP_SIZE+MV_OP_PADDING)*2, MV_OP_SIZE+MV_OP_PADDING*2))
        pygame.draw.rect(self.screen, (255,255,255), [SCREEN_WIDTH-(MV_OP_SIZE+MV_OP_PADDING)*2-1, MV_OP_SIZE+MV_OP_PADDING+1, MV_OP_SIZE+2, MV_OP_SIZE+2],1)

    def draw(self):
        self.backgrounds[self.current_background].draw()

        self.isometric.draw()

        self.text_manager.draw()
        self.text_manager.blit(f'LVL:{self.lvl_id}', vec2(5,5))

        if mobile:
            for rect in self.touch_control_rects:
                pygame.draw.rect(self.screen, (255,255,255), rect, 1)
            
            self.text_manager.blit('R', vec2(self.touch_control_rects[4].center)-vec2(3,4))
        
        self.draw_move_options()




async def main():
    gm = DiceGame()
    running = True
    clock = pygame.time.Clock() # To enforce FPS

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # Check if window is exited
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r or event.key == pygame.K_SPACE:
                    gm.reset()
                elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    gm.die.move_right()
                elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    gm.die.move_left()
                elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    gm.die.move_front()
                elif event.key == pygame.K_w or event.key == pygame.K_UP:
                    gm.die.move_back()
            
            if mobile and event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = vec2(event.pos)/RATIO
                gm.process_touch_controls(mouse_pos)
                
        
        gm.update()
        gm.draw()

        # Scale screen to fit window and blit, then update window
        pygame.transform.scale(gm.screen, (WINDOW_WIDTH, WINDOW_HEIGHT), gm.window)
        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(0)

asyncio.run(main())