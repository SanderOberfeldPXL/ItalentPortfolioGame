import pygame
from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic, Obstacle
from pytmx.util_pygame import load_pygame

class Level:
    
    def __init__(self):
        # get display surface
        self.display_surface = pygame.display.get_surface()
        
        # sprite groups
        self.all_sprites = CameraGroup()
        self.collision_sprites = pygame.sprite.Group()
        
        self.setup()
        self.overlay = Overlay(self.player)
        self.spawn = (640, 360)
        
        
    def setup(self):
        tmx_data = load_pygame('./data/portfoliomap.tmx')
        WORLD_SCALE = 1.5
        
        map_pixel_width = tmx_data.width * tmx_data.tilewidth * WORLD_SCALE
        map_pixel_height = tmx_data.height * tmx_data.tileheight * WORLD_SCALE
        
        self.all_sprites.set_map_boundaries(map_pixel_width, map_pixel_height)
        
        for obj in tmx_data.get_layer_by_name('Spawns'):
            if obj.name == 'Player':

                self.spawn = (obj.x * WORLD_SCALE, obj.y * WORLD_SCALE)
                break
        
        # VISUAL-ONLY TILE LAYERS
        visual_tile_layers = ['background', 'ground', 'grounddetails', 'hills', 'overlaphills', 'trees', 'hilldetails']
        for layer in visual_tile_layers:
            tmx_layer = tmx_data.get_layer_by_name(layer)
            for x, y, surface in tmx_layer.tiles():
                new_w = int(surface.get_width() * WORLD_SCALE)
                new_h = int(surface.get_height() * WORLD_SCALE)
                scaled_surface = pygame.transform.scale(surface, (new_w, new_h))
                Generic(
                    pos = (x * tmx_data.tilewidth * WORLD_SCALE, y * tmx_data.tileheight * WORLD_SCALE),
                    surface = scaled_surface,
                    groups = [self.all_sprites], # Only drawing
                    z = LAYERS['ground'] 
                )

        # details layer
        for layer in ['hilldetails']:
            tmx_layer = tmx_data.get_layer_by_name(layer)
            for x, y, surface in tmx_layer.tiles():
                # Scale the tile image
                new_w = int(surface.get_width() * WORLD_SCALE)
                new_h = int(surface.get_height() * WORLD_SCALE)
                scaled_surface = pygame.transform.scale(surface, (new_w, new_h))
                
                Generic(
                    pos = (x * tmx_data.tilewidth * WORLD_SCALE, y * tmx_data.tileheight * WORLD_SCALE),
                    surface = scaled_surface,
                    groups = [self.all_sprites], 
                    z = LAYERS['main']
                )
                
        # VISUAL OBJECT LAYERS
        object_layers = ['buildings', 'object_trees', 'interaction']
        
        for layer in object_layers:
            tmx_layer = tmx_data.get_layer_by_name(layer)
            for obj in tmx_layer:
                if hasattr(obj, 'image') and obj.image:
                    surface = obj.image
                    
                    target_w = int(obj.width * WORLD_SCALE)
                    target_h = int(obj.height * WORLD_SCALE)
            
                    if surface.get_width() != target_w or surface.get_height() != target_h:
                        surface = pygame.transform.scale(surface, (target_w, target_h))
                    
                    if obj.rotation != 0:
                        surface = pygame.transform.rotate(surface, -obj.rotation)

                    groups = [self.all_sprites]
                    if layer == 'interaction':
                        groups.append(self.collision_sprites)

                    Generic(
                        pos = (obj.x * WORLD_SCALE, obj.y * WORLD_SCALE),
                        surface = surface,
                        groups = groups,
                        z = LAYERS['main']
                    )
                    
                elif layer == 'interaction':
                    Obstacle(
                        pos = (obj.x * WORLD_SCALE, obj.y * WORLD_SCALE), 
                        size = (obj.width * WORLD_SCALE, obj.height * WORLD_SCALE), 
                        groups = [self.collision_sprites]
                    )

        # INVISIBLE COLLISION OBJECT LAYERS
        for layer in ['collision']:
            tmx_layer = tmx_data.get_layer_by_name(layer)
            for obj in tmx_layer:
                
                Obstacle(
                    pos = (obj.x * WORLD_SCALE, obj.y * WORLD_SCALE), 
                    size = (obj.width * WORLD_SCALE, obj.height * WORLD_SCALE), 
                    groups = [self.collision_sprites] 
                )

        # Setup Player
        self.player = Player(self.spawn, self.all_sprites, self.collision_sprites)
        
    
    def run(self, dt):
        self.display_surface.fill('black')
        
        self.all_sprites.custom_draw(self.player)
        
        # call update method of all children
        self.all_sprites.update(dt)
    
        self.overlay.display()
        
        
class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()
        
        self.map_width = 0
        self.map_height = 0
        
    
    def set_map_boundaries(self, width, height):
        self.map_width = width
        self.map_height = height
        
        
    def custom_draw(self, player):
        # offset
        self.offset.x = player.rect.centerx - SCREEN_WIDTH // 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT // 2
        
        self.offset.x = max(0, self.offset.x)
        self.offset.y = max(0, self.offset.y)
        
        max_offset_x = self.map_width - SCREEN_WIDTH
        max_offset_y = self.map_height - SCREEN_HEIGHT
        
        self.offset.x = min(self.offset.x, max_offset_x)
        self.offset.y = min(self.offset.y, max_offset_y)
        
        for layer in LAYERS.values():
            
            sprites_in_layer = [sprite for sprite in self.sprites() if sprite.z == layer]
            if layer == LAYERS['main']:
                sprites_in_layer = sorted(
                    sprites_in_layer, 
                    key=lambda sprite: sprite.hitbox.bottom if hasattr(sprite, 'hitbox') else sprite.rect.bottom
                )
            
            for sprite in sprites_in_layer:
                offset_rect = sprite.rect.copy()
                offset_rect.center -= self.offset
                self.display_surface.blit(sprite.image, offset_rect)