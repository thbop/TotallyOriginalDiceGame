import pygame
from pygame.math import Vector2 as vec2, Vector3 as vec3

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
    def __init__(self, rect: pygame.Rect):
        super().__init__(vec3(rect.x, rect.y, 0))
        self.size = vec2(rect.size)
    
    # Checks if an element is in view to prevent unecessary draw instructions
    def in_view(self, element: Iso) -> bool:
        return self.rect.colliderect(
            pygame.Rect(
                element.project(),
                (ISO_ELEMENT_PROJECTED_WIDTH, ISO_ELEMENT_PROJECTED_HEIGHT)
            )
        )


    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(
            self.position.x,
            self.position.y,
            self.size.x,
            self.size.y
        )
    @rect.setter
    def rect(self, value: pygame.Rect):
        self.position = vec3(value.x, value.y, 0)
        self.size = vec2(value.size)

class IsoBlock(Iso):
    def __init__(self, position: vec3, ID: int):
        super().__init__(position)
        self.ID = ID
    

class Isometric:
    def __init__(self, gm):
        self.gm = gm
        ss = spritesheet('sprites.png')
        self.block_textures = ss.images_at(
            [
                [0,0,23,22],
                [23,0,23,22]
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
                    surf = self.block_textures[iso.ID]
                
                if surf:
                    self.gm.screen.blit(surf, iso.project() - self.gm.camera.rect.topleft)
        