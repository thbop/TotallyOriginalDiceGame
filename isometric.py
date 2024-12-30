import pygame
from pygame.math import Vector2 as vec2, Vector3 as vec3

from math import floor, sin, copysign

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


class IsoParticle(Iso):
    def __init__(self, position: vec3, velocity: vec3, lifetime: int):
        super().__init__(position)
        self.velocity = velocity
        self.lifetime = lifetime
        self.dead = False
    
    def update(self):
        if not self.dead:
            self.position += self.velocity
            self.lifetime -= 1
            if not self.lifetime:
                self.dead = True


class IsoTextParticle(IsoParticle):
    def __init__(self, text: str, position: vec3, velocity: vec3, lifetime: int):
        super().__init__(position, velocity, lifetime)
        self.text = text


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
    

class IsoTimedBlock(IsoBlock):
    def __init__(self, gm, position, ID, time=60):
        super().__init__(position, ID)
        self.gm = gm
        self.time = time
        self.tick = time
        self.stepped_on = False
    
    
    def update(self):
        if self.ID == 4 and self.stepped_on:
            self.tick -= 1
            if not self.tick:
                self.ID = 5 # Become void block
                self.stepped_on = False
                self.gm.sounds['blip'].play()
        
        elif self.ID == 5:
            self.tick += 1
            if self.tick == self.time:
                self.ID = 4 # Become timer block
                self.gm.sounds['blip'].play()

class DieLayout:
    def __init__(self, top, bottom, right, left, front, back):
        self.top = top
        self.bottom = bottom
        self.right = right
        self.left = left
        self.front = front
        self.back = back
    
    def __repr__(self):
        return f'DieLayout(top: {self.top}, bottom: {self.bottom}, right: {self.right}, left: {self.left}, front: {self.front}, back: {self.back})'

    def copy(self, existing):
        return DieLayout(existing.top, existing.bottom, existing.right, existing.left, existing.front, existing.back)
    
    def fromlist(l):
        return DieLayout(l[0],l[1],l[2],l[3],l[4],l[5])
    
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
        super().__init__(position)
        self.gm = gm
        self.default_position = position.copy()
        self.sample_offset = vec3(-1,0,-1)
        self.layout = layout


        ss = spritesheet('img/die.png')

        self.sampler = ss.image_at([0,0,9,9])
        self.tex = ss.image_at([0,0,9,9],(0,0,0))

        self.faces = ss.images_at([
            [0, 9,3,3], [3, 9,3,3], [6, 9,3,3],
            [0,12,3,3], [3,12,3,3], [6,12,3,3],
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
    
    def _check_collision(self, sample: vec3, isos):
        for iso in isos:
            if isinstance(iso, IsoBlock) and iso.position == sample:
                return iso
        return None
    
    def _move_process(self, iso):
        if iso == None or iso.ID == 5: # Void tiles
            self.gm.sounds['invalid'].play()
            return False
        elif iso.ID == 4: # White tile
            iso.stepped_on = True
        elif iso.ID == 3: # Red tile
            self.gm.load(self.gm.lvl_id+1)
            if self.gm.lvl_id:
                self.gm.sounds['win'].play()
        
        return True
    
    def _move_complete(self, dice_number):
        self.update_tex()
        self.gm.sounds['step'].play()
        self.gm.isometric.isos.append(IsoTextParticle(f'{dice_number}', self.position.copy(), vec3(.01,0,.2), 20))

    def move_x(self, dx, isos):
        sample = self.position + self.sample_offset
        step = copysign(1, dx)
        for s in range(abs(dx)):
            sample.x += step
            step_collision = self._check_collision(sample, isos)
            if step_collision and step_collision.ID == 1:
                self.gm.sounds['invalid'].play()
                return False
        
        end_collision = self._check_collision(sample, isos)
        if not self._move_process(end_collision):
            return False
        
        self.position.x += dx

        self._move_complete(abs(dx))
        return True

    
    def move_y(self, dy, isos):
        sample = self.position + self.sample_offset
        step = copysign(1, dy)
        for s in range(abs(dy)):
            sample.y += step
            step_collision = self._check_collision(sample, isos)
            if step_collision and step_collision.ID == 1:
                self.gm.sounds['invalid'].play()
                return False
        
        end_collision = self._check_collision(sample, isos)
        if not self._move_process(end_collision):
            return False
        
        self.position.y += dy

        self._move_complete(abs(dy))
        return True
    
    def move_right(self):
        self.layout.roll_right()
        if not self.move_x(self.layout.bottom+1, self.gm.isometric.isos): self.layout.roll_left()
    def move_left(self):
            self.layout.roll_left()
            if not self.move_x(-(self.layout.bottom+1), self.gm.isometric.isos): self.layout.roll_right()
    def move_front(self):
            self.layout.roll_front()
            if not self.move_y(self.layout.bottom+1, self.gm.isometric.isos): self.layout.roll_back()
    def move_back(self):
            self.layout.roll_back()
            if not self.move_y(-(self.layout.bottom+1), self.gm.isometric.isos): self.layout.roll_front()
    
    def update(self):
        if self._check_collision(self.position+self.sample_offset, self.gm.isometric.isos).ID == 5:
            self.gm.reset('invalid')

    def draw(self):
        self.gm.screen.blit(self.tex, self.project() - self.gm.camera.rect.topleft + vec2(-4,3))

    

class Isometric:
    def __init__(self, gm):
        self.gm = gm
        block_ss = spritesheet('img/blocks.png')
        self.block_textures = block_ss.images_at(
            [
                [0,0,23,22],   # Blue
                [23,0,23,22],  # Orange
                [46,0,23,22],  # Green/Start
                [69,0,23,22],  # Red/End
                [92,0,23,22],  # White/Timed
                [115,0,23,22], # Empty
            ],
            (0,0,0)
        )
        self.size: vec2
        self.isos = []
    
    def load(self, image_filename: str):
        self.isos = []
        im = pygame.image.load(image_filename)
        self.size = vec2(im.get_size())
        for j in range(im.get_height()):
            for i in range(im.get_width()):
                color = im.get_at((i,j))
                if color == (0,0,0xFF): self.isos.append(IsoBlock(vec3(i,j,0), 0))
                elif color == (0xFF,0x7F,0): self.isos.append(IsoBlock(vec3(i,j,0), 1))
                elif color == (0xFF,0,0): self.isos.append(IsoBlock(vec3(i,j,0), 3))
                elif color == (0,0xFF,0):
                    self.isos.append(IsoBlock(vec3(i,j,0), 2))
                    # Regular die layout DieLayout(0,5,1,4,2,3)
                    self.gm.die = IsoDie(self.gm, vec3(i+1,j,1), DieLayout(0,0,0,0,0,0))
                    self.isos.append(self.gm.die)
                elif color == (0x64,0x64,0x64):
                    self.isos.append(IsoTimedBlock(self.gm, vec3(i,j,0), 4))


    def update(self):
        sort_expr = lambda x: (x.project().y + x.position.z * ISO_Y_OFFSET)
        self.isos.sort(key=sort_expr)
        deadIsos = []
        for iso in self.isos:
            if isinstance(iso, IsoTimedBlock) or isinstance(iso, IsoDie):
                iso.update()
            if isinstance(iso, IsoParticle):
                iso.update()
                if iso.dead:
                    deadIsos.append(iso)
        
        for iso in deadIsos:
            self.isos.remove(iso)
    
    def draw(self):
        for iso in self.isos:
            if self.gm.camera.in_view(iso):
                surf: pygame.Surface = None
                if isinstance(iso, IsoBlock):
                    self.gm.screen.blit(self.block_textures[iso.ID], iso.project() - self.gm.camera.rect.topleft)

                if isinstance(iso, IsoDie):
                    iso.draw()
                
                if isinstance(iso, IsoTextParticle):
                    self.gm.text_manager.blit(iso.text, iso.project() - self.gm.camera.rect.topleft)
                
        