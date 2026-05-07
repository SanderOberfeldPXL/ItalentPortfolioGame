import pygame
import json
from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic, Obstacle, Interactable
from pytmx.util_pygame import load_pygame

class Level:
    
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(None, 30)
        
        self.all_sprites = CameraGroup()
        self.collision_sprites = pygame.sprite.Group()
        self.interactable_sprites = pygame.sprite.Group() 
        
        self.dialogue_active = False
        self.dialogue_pages = []
        self.current_page = 0
        
        self.menu_active = False
        
        self.setup()
        
    def setup(self):
        with open('data/dialogue.json') as file:
            dialogue_data = json.load(file)

        tmx_data = load_pygame('./data/portfoliomap.tmx')
        WORLD_SCALE = 1.5
        
        map_pixel_width = tmx_data.width * tmx_data.tilewidth * WORLD_SCALE
        map_pixel_height = tmx_data.height * tmx_data.tileheight * WORLD_SCALE
        
        self.all_sprites.set_map_boundaries(map_pixel_width, map_pixel_height)
        
        for obj in tmx_data.get_layer_by_name('Spawns'):
            if obj.name == 'Player':
                self.spawn = (obj.x * WORLD_SCALE, obj.y * WORLD_SCALE)
                break
        
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
                    groups = [self.all_sprites], 
                    z = LAYERS['ground'] 
                )

        for layer in ['hilldetails']:
            tmx_layer = tmx_data.get_layer_by_name(layer)
            for x, y, surface in tmx_layer.tiles():
                new_w = int(surface.get_width() * WORLD_SCALE)
                new_h = int(surface.get_height() * WORLD_SCALE)
                scaled_surface = pygame.transform.scale(surface, (new_w, new_h))
                
                Generic(
                    pos = (x * tmx_data.tilewidth * WORLD_SCALE, y * tmx_data.tileheight * WORLD_SCALE),
                    surface = scaled_surface,
                    groups = [self.all_sprites], 
                    z = LAYERS['main']
                )
                
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

                    if layer == 'interaction':
                        groups = [self.all_sprites, self.collision_sprites, self.interactable_sprites]
                        text = dialogue_data.get(obj.name, "Text not found.")
                        Interactable(
                            pos = (obj.x * WORLD_SCALE, obj.y * WORLD_SCALE),
                            size = (target_w, target_h),
                            groups = groups,
                            name = obj.name,
                            text = text,
                            surface = surface
                        )
                    else:
                        Generic(
                            pos = (obj.x * WORLD_SCALE, obj.y * WORLD_SCALE),
                            surface = surface,
                            groups = [self.all_sprites],
                            z = LAYERS['main']
                        )
                    
                elif layer == 'interaction':
                    text = dialogue_data.get(obj.name, "Text not found.")
                    Interactable(
                        pos = (obj.x * WORLD_SCALE, obj.y * WORLD_SCALE), 
                        size = (obj.width * WORLD_SCALE, obj.height * WORLD_SCALE), 
                        groups = [self.collision_sprites, self.interactable_sprites],
                        name = obj.name,
                        text = text
                    )

        for layer in ['collision']:
            tmx_layer = tmx_data.get_layer_by_name(layer)
            for obj in tmx_layer:
                Obstacle(
                    pos = (obj.x * WORLD_SCALE, obj.y * WORLD_SCALE), 
                    size = (obj.width * WORLD_SCALE, obj.height * WORLD_SCALE), 
                    groups = [self.collision_sprites] 
                )

        self.player = Player(
            self.spawn, 
            self.all_sprites, 
            self.collision_sprites, 
            self.interactable_sprites, 
            self.toggle_dialogue
        )
        
        start_text = dialogue_data.get("game_start", "Welcome! Press Space to start.")
        self.toggle_dialogue(start_text)
        
    def toggle_menu(self):
        self.menu_active = not self.menu_active
        if self.menu_active and self.dialogue_active:
            self.dialogue_active = False

    def draw_menu(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180) 
        overlay.fill('black')
        self.display_surface.blit(overlay, (0, 0))

        title_surf = pygame.font.Font(None, 60).render("PAUSE MENU", True, 'white')
        title_rect = title_surf.get_rect(center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        self.display_surface.blit(title_surf, title_rect)

        controls_text = [
            "Arrow Keys : Move",
            "Spacebar : Interact",
            "Escape : Resume Game",
            "Enter : Quit Game"
        ]

        for index, text in enumerate(controls_text):
            color = 'red' if 'Quit' in text else 'white'
            text_surf = self.font.render(text, True, color)
            text_rect = text_surf.get_rect(center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + (index * 40)))
            self.display_surface.blit(text_surf, text_rect)
        
        
    def toggle_dialogue(self, text=None):
        if self.dialogue_active:
            self.dialogue_active = False
            self.dialogue_pages = []
            self.current_page = 0
        elif text:
            self.dialogue_active = True
            self.create_dialogue_pages(text)
            self.current_page = 0

    def create_dialogue_pages(self, raw_text):
        box_width = int(SCREEN_WIDTH * 0.6)
        padding = 20
        max_text_width = box_width - (padding * 2)
        max_lines_per_page = 6

        all_lines = []
        paragraphs = raw_text.split('\n')
        
        for paragraph in paragraphs:
            if paragraph == "":
                all_lines.append("")
                continue
                
            words = paragraph.split(' ')
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                if self.font.size(test_line)[0] < max_text_width:
                    current_line.append(word)
                else:
                    all_lines.append(' '.join(current_line))
                    current_line = [word]
            
            if current_line:
                all_lines.append(' '.join(current_line))

        self.dialogue_pages = []
        for i in range(0, len(all_lines), max_lines_per_page):
            self.dialogue_pages.append(all_lines[i:i + max_lines_per_page])
            

    def draw_dialogue(self):
        if not self.dialogue_active or not self.dialogue_pages:
            return

        box_width = int(SCREEN_WIDTH * 0.6)
        padding = 20
        line_height = self.font.get_linesize()
        
        actual_lines = max(len(page) for page in self.dialogue_pages)
        box_height = (actual_lines * line_height) + (padding * 2) + 20 

        box_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - box_width // 2, 
            SCREEN_HEIGHT - box_height - 20, 
            box_width, 
            box_height
        )
        
        pygame.draw.rect(self.display_surface, 'white', box_rect, border_radius=10)
        pygame.draw.rect(self.display_surface, 'black', box_rect, width=4, border_radius=10)

        current_page_lines = self.dialogue_pages[self.current_page]
        current_y = box_rect.top + padding
        
        for line in current_page_lines:
            if line: 
                text_surf = self.font.render(line, True, 'black')
                text_rect = text_surf.get_rect(topleft = (box_rect.left + padding, current_y))
                self.display_surface.blit(text_surf, text_rect)
            current_y += line_height
            
        self.draw_page_indicator(box_rect, padding)


    def draw_page_indicator(self, box_rect, padding):
        total_pages = len(self.dialogue_pages)
        current = self.current_page + 1
        
        if total_pages > 1:
            if self.current_page < total_pages - 1:
                indicator_text = f"Space to continue  {current}/{total_pages} ->"
            else:
                indicator_text = f"Space to close  {current}/{total_pages} X"
        else:
            indicator_text = "Space to close X"
            
        small_font = pygame.font.Font(None, 24)
        indicator_surf = small_font.render(indicator_text, True, 'gray40') 
        indicator_rect = indicator_surf.get_rect(bottomright = (box_rect.right - padding, box_rect.bottom - 10))
        self.display_surface.blit(indicator_surf, indicator_rect)


    def run(self, dt):
        self.display_surface.fill('black')
        self.all_sprites.custom_draw(self.player)
        
        if self.menu_active:
            self.draw_menu()
        elif self.dialogue_active:
            self.check_dialogue_input()
            self.draw_dialogue()
        else:
            self.all_sprites.update(dt)

    def check_dialogue_input(self):
        self.player.timers['interaction_cooldown'].update()
        
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_SPACE] and not self.player.timers['interaction_cooldown'].active:
            self.player.timers['interaction_cooldown'].activate()
            
            if self.current_page < len(self.dialogue_pages) - 1:
                self.current_page += 1
            else:
                self.toggle_dialogue()
            
        elif keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or keys[pygame.K_UP] or keys[pygame.K_DOWN]:
            self.toggle_dialogue()
        
        
        
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