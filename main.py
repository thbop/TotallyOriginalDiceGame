import sys, platform

mobile = False
if sys.platform == "emscripten":
    platform.window.canvas.style.imageRendering = "pixelated"
    import js
    user_agent = js.window.navigator.userAgent
    # Simple check for mobile user agents
    mobile = any(mobile_str in user_agent for mobile_str in ["Mobi", "Android", "iPhone"])

import json
import asyncio
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
            'invalid':pygame.mixer.Sound('sfx/invalid.wav'),
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
        self.isometric.load(f'levels/{self.lvl_id}.png')
        self.die.layout = DieLayout.fromlist(data['die_layout'])
        self.die.update_tex()
        self.text_manager.load(data['texts'])

    
    def reset(self):
        self.load(self.lvl_id)
        self.sounds['reset'].play()
    
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

    def draw(self):
        self.screen.fill((12,13,20)) # Clear screen

        self.isometric.draw()

        self.text_manager.draw()
        self.text_manager.blit(f'LVL:{self.lvl_id}', vec2(5,5))

        if mobile:
            for rect in self.touch_control_rects:
                pygame.draw.rect(self.screen, (255,255,255), rect, 1)
            
            self.text_manager.blit('R', vec2(self.touch_control_rects[4].center)-vec2(3,4))




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