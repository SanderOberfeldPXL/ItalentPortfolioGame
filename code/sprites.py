import pygame
from settings import *

class Generic(pygame.sprite.Sprite):
    def __init__(self, pos, surface, groups, z = LAYERS['main']):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_rect(topleft = pos)
        self.z = z
        
        
        
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, pos, size, groups):
        super().__init__(groups)
        self.rect = pygame.Rect(pos, size)
        
        
        
class Interactable(pygame.sprite.Sprite):
    def __init__(self, pos, size, groups, name, text, surface=None, z=LAYERS['main']):
        super().__init__(groups)
        
        if surface:
            self.image = surface
            self.rect = self.image.get_rect(topleft = pos)
            self.z = z
        else:
            self.rect = pygame.Rect(pos, size)
            
        self.name = name
        self.text = text