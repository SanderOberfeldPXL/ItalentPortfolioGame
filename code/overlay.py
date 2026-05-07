import pygame
from settings import *

class Overlay:
    def __init__(self, player):
        
        self.display_surface = pygame.display.get_surface()
        self.player = player
        
        overlay_path = 'graphics/overlay/'
        self.equipment_surfaces = {equipment:pygame.image.load(f'{overlay_path}{equipment}.png').convert_alpha() for equipment in player.equipment}
        print(self.equipment_surfaces)
        
        
    def display(self):
        equipment_surface = self.equipment_surfaces[self.player.selected_equipment]
        tool_rect = equipment_surface.get_rect(midbottom = OVERLAY_POS['equipment'])
        self.display_surface.blit(equipment_surface, tool_rect)