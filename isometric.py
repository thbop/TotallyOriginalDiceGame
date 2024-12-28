import pygame
from pygame.math import Vector2 as vec2, Vector3 as vec3

from math import floor, sin, pi

from constants import *
from spritesheet import spritesheet


ISO_X_OFFSET = 11
ISO_Y_OFFSET = 5
ISO_ELEMENT_PROJECTED_WIDTH = 23
ISO_ELEMENT_PROJECTED_HEIGHT = 22

class Iso:
    def __init__(self, position: vec3):
        self.position = position
    
    def project_coord(self, coord: vec3) -> vec2:
        return vec2(
                (coord.x - coord.y) * ISO_X_OFFSET,
                (coord.x + coord.y - coord.z) * ISO_Y_OFFSET
            )
    def project(self) -> vec2:
        return self.project_coord(self.position)
    

class IsoCamera(Iso):
    def __init__(self, gm, rect: pygame.Rect):
        super().__init__(vec3(rect.x, rect.y, 0))
        self.rect = rect
        self.gm = gm

    
    # Checks if an element is in view to prevent unecessary draw instructions
    def in_view(self, element: Iso) -> bool:
        return self.rect.colliderect(
            pygame.Rect(
                element.project(),
                (ISO_ELEMENT_PROJECTED_WIDTH, ISO_ELEMENT_PROJECTED_HEIGHT)
            )
        )
    
    def update(self):
        die_pos = self.gm.die.project()

        self.rect.centerx += ( die_pos.x - self.rect.centerx ) / 10
        self.rect.centery += ( die_pos.y - self.rect.centery ) / 10





class IsoBlock(Iso):
    def __init__(self, position: vec3, ID: int):
        super().__init__(position)
        self.ID = ID

class DieLayout:
    def __init__(self, top, bottom, right, left, front, back):
        self.top = top
        self.bottom = bottom
        self.right = right
        self.left = left
        self.front = front
        self.back = back

    def copy(self, existing):
        return DieLayout(existing.top, existing.bottom, existing.right, existing.left, existing.front, existing.back)
    
    def roll_front(self):
        old = self.copy(self)
        self.top = old.back
        self.back = old.bottom
        self.bottom = old.front
        self.front = old.top
    def roll_back(self):
        old = self.copy(self)
        self.top = old.front
        self.back = old.top
        self.bottom = old.back
        self.front = old.bottom
    def roll_right(self):
        old = self.copy(self)
        self.top = old.left
        self.left = old.bottom
        self.bottom = old.right
        self.right = old.top
    def roll_left(self):
        old = self.copy(self)
        self.top = old.right
        self.left = old.top
        self.bottom = old.left
        self.right = old.bottom

class IsoDie(Iso):
    def __init__(self, gm, position: vec3, layout: DieLayout):
        self.gm = gm
        super().__init__(position)
        self.layout = layout


        ss = spritesheet('img/die.png')

        self.sampler = ss.image_at([0,0,9,9])
        self.tex = ss.image_at([0,0,9,9],(0,0,0))

        self.faces = ss.images_at([
            [0, 9,3,3], [3, 9,3,3], [6, 9,3,3],
            [0,12,3,3], [3,12,3,3], [6,12,3,3],
            [0,15,3,3], [3,15,3,3], [6,15,3,3],
        ])
        self.update_tex()
    
    def _sample_uv(self, value: int, sampled: pygame.Surface):
        q = (255 - value)/5
        uv = ( q % 3, floor(q/3) )
        return sampled.get_at(uv)
    
    def update_tex(self):
        for j in range(9):
            for i in range(9):
                sample = self.sampler.get_at((i,j))
                if sample != (0,0,0) and sample != (237,237,228):
                    if sample.r:
                        color = self._sample_uv(sample.r, self.faces[self.layout.front])
                        self.tex.set_at((i,j), (max(color.r-10, 1), max(color.g-10, 1), max(color.b-10, 1), 255))
                    elif sample.g: self.tex.set_at((i,j), self._sample_uv(sample.g, self.faces[self.layout.top]))
                    elif sample.b:
                        color = self._sample_uv(sample.b, self.faces[self.layout.right])
                        self.tex.set_at((i,j), (max(color.r-50, 1), max(color.g-50, 1), max(color.b-50, 1), 255))
    
    def update(self):
        tapped = pygame.key.get_just_pressed()
        moved = False
        if tapped[pygame.K_d]:
            self.layout.roll_left()
            self.position.x += self.layout.bottom+1
            moved = True
        if tapped[pygame.K_a]:
            self.layout.roll_right()
            self.position.x -= self.layout.bottom+1
            moved = True
        if tapped[pygame.K_s]:
            self.layout.roll_front()
            self.position.y += self.layout.bottom+1
            moved = True
        if tapped[pygame.K_w]:
            self.layout.roll_back()
            self.position.y -= self.layout.bottom+1
            moved = True
        
        if moved:
            self.update_tex()
            self.gm.sounds['step'].play()


    def draw(self):
        self.gm.screen.blit(self.tex, self.project() - self.gm.camera.rect.topleft + vec2(-4,3))

    

class Isometric:
    def __init__(self, gm):
        self.gm = gm
        block_ss = spritesheet('img/blocks.png')
        self.block_textures = block_ss.images_at(
            [
                [0,0,23,22],  # Blue
                [23,0,23,22], # Orange
            ],
            (0,0,0)
        )
        self.size: vec2
        self.isos = []
    
    def load_blocks(self, image_filename: str):
        im = pygame.image.load(image_filename)
        self.size = vec2(im.get_size())
        lvlarr = pygame.PixelArray(im)
        for j in range(im.get_height()):
            for i in range(im.get_width()):
                if lvlarr[i,j] == im.map_rgb((0,0,0xFF)): self.isos.append(IsoBlock(vec3(i,j,0), 0))
                elif lvlarr[i,j] == im.map_rgb((0xFF,0x7F,0)): self.isos.append(IsoBlock(vec3(i,j,0), 1))



    def update(self):
        sort_expr = lambda x: (x.project().y + x.position.z * ISO_Y_OFFSET)
        self.isos.sort(key=sort_expr)
    
    def draw(self):
        for iso in self.isos:
            if self.gm.camera.in_view(iso):
                surf: pygame.Surface = None
                if isinstance(iso, IsoBlock):
                    self.gm.screen.blit(self.block_textures[iso.ID], iso.project() - self.gm.camera.rect.topleft)

                if isinstance(iso, IsoDie):
                    iso.draw()
                
        