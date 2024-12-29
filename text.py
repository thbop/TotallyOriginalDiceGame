import pygame
from pygame.math import Vector2 as vec2

from spritesheet import spritesheet

class Text:
    def __init__(self, text: str, pos: vec2, follow_camera=True):
        self.text = text
        self.pos = pos
        self.follow_camera = follow_camera

class Typer(Text):
    def __init__(self, text: str, pos: vec2, delay, sfx: pygame.mixer.Sound=None, follow_camera=True):
        super().__init__('', pos, follow_camera)
        self.full_text = text

        self.delay = delay
        self.tick = 0

        self.cursor = 0
        self.finished = False
        self.sfx = sfx
    def update(self):
        if len(self.full_text) > self.cursor:
            if self.tick >= self.delay:
                if self.sfx and self.full_text[self.cursor] != ' ':
                    self.sfx.play()
                self.tick = 0
                self.text += self.full_text[self.cursor]
                self.cursor += 1
            self.tick += 1
        else:
            self.finished = True

class TextManager:
    def __init__(self, gm):
        self.gm = gm
        self.ss = spritesheet('img/text.png')
        self.texts = []
    
    def load(self, texts):
        self.texts = []
        for t in texts:
            if t['delay']:
                self.texts.append( Typer(t['text'], vec2(t['pos']), t['delay'], self.gm.sounds['type'], t['follow_camera']) )
            else:
                self.texts.append( Text(t['text'], vec2(t['pos']), t['follow_camera']) )
    
    def blit(self, text: str, pos: vec2):
        width = len(text)*6
        surf = pygame.Surface((width, 7))
        surf.fill((0, 0, 0))
        surf.set_colorkey((0, 0, 0))
        i = 0
        for c in text:
            surf.blit(
                self.ss.image_at([ (ord(c)-32)*5, 0, 5, 7], (0, 0, 0)),
                (i, 0)
            )
            i += 6
        self.gm.screen.blit(surf, pos)
    
    def update(self):
        for t in self.texts:
            if isinstance(t, Typer):
                t.update()
    
    def draw(self):
        for t in self.texts:
            self.blit(t.text, t.pos - self.gm.camera.rect.topleft if not t.follow_camera else vec2(0,0))
    

