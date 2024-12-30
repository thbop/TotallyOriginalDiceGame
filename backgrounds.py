import pygame
from pygame.math import Vector2 as vec2
from random import uniform

from constants import *


class Background:
    def __init__(self, gm):
        self.gm = gm
    
    def update(self): pass
    def draw(self): pass

class BackgroundColor(Background):
    def __init__(self, gm, color):
        super().__init__(gm)
        self.color = color
    def draw(self):
        self.gm.screen.fill(self.color)

class Star:
    def __init__(self, position: vec2, velocity: vec2):
        self.position = position
        self.velocity = velocity
    
    def update(self):
        self.position += self.velocity
    
    def draw(self, surf: pygame.Surface):
        pygame.draw.rect(surf, (100,100,120), [self.position.x, self.position.y, 1, 1])

class BackgroundStars(Background):
    def __init__(self, gm, target=20):
        super().__init__(gm)
        self.target = target
        self.surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.dimmer = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.dimmer.fill((3,3,3))
        self.stars = []
    

    def update(self):
        deadStars = []
        screen_rect = pygame.Rect(0,0,SCREEN_WIDTH, SCREEN_HEIGHT)

        for i in range(self.target-len(self.stars)):
            self.stars.append(Star(vec2(uniform(0, SCREEN_WIDTH), uniform(0, SCREEN_HEIGHT)), vec2(uniform(-.3,.3),uniform(-.3,.3))))
        for s in self.stars:
            s.update()
            if not screen_rect.collidepoint(s.position):
                deadStars.append(s)
        for s in deadStars:
            self.stars.remove(s)
    
    def draw(self):
        for s in self.stars:
            s.draw(self.surf)
        
        self.surf.blit(self.dimmer, (0,0), special_flags=pygame.BLEND_RGB_SUB)
        self.gm.screen.blit(self.surf, (0,0))