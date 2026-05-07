import pygame
from settings import *
from support import *
from timer import Timer

class Player(pygame.sprite.Sprite):
    
    def __init__(self, pos, group, collision_sprites, interactable_sprites, interaction_callback):
        super().__init__(group)
        self.collision_sprites = collision_sprites
        self.interactable_sprites = interactable_sprites
        self.interaction_callback = interaction_callback
        
        self.import_assets()
        self.status = 'down_idle'
        self.frame_index = 0
        
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center = pos)
        
        self.hitbox = self.rect.inflate(-64, -90)
        self.hitbox_offset_y = 18
        self.hitbox.bottom = self.rect.bottom - self.hitbox_offset_y
        
        self.z = LAYERS['main']
        
        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.hitbox.center)
        self.speed = 200
        
        self.timers = {
            'interaction_cooldown': Timer(500)
        }
        
    def get_facing_vector(self):
        facing = pygame.math.Vector2()
        status_base = self.status.split('_')[0]
        
        if status_base == 'up':
            facing.y = -1
        elif status_base == 'down':
            facing.y = 1
        elif status_base == 'left':
            facing.x = -1
        elif status_base == 'right':
            facing.x = 1
            
        return facing

    def check_interaction(self):
        facing_vector = self.get_facing_vector()
        
        origin_x = self.hitbox.centerx
        origin_y = self.hitbox.centery

        interaction_distance = 40 
        
        target_x = origin_x + (facing_vector.x * interaction_distance)
        target_y = origin_y + (facing_vector.y * interaction_distance)
        interaction_rect = pygame.Rect(target_x - 20, target_y - 20, 40, 40) 

        for sprite in self.interactable_sprites.sprites():
            if interaction_rect.colliderect(sprite.rect):
                if hasattr(sprite, 'text'):
                    self.interaction_callback(sprite.text)
                return
            

    def input(self):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT]:
            self.direction.x = -1
            self.status = 'left'
        elif keys[pygame.K_RIGHT]:
            self.direction.x = 1
            self.status = 'right'
        else:
            self.direction.x = 0
    
        if keys[pygame.K_UP]:
            self.direction.y = -1
            self.status = 'up'
        elif keys[pygame.K_DOWN]:
            self.direction.y = 1
            self.status = 'down'
        else:
            self.direction.y = 0
            
        if keys[pygame.K_SPACE] and not self.timers['interaction_cooldown'].active:
            self.timers['interaction_cooldown'].activate()
            self.direction = pygame.math.Vector2()
            self.check_interaction()

    def collision(self, direction):
        for sprite in self.collision_sprites.sprites():
            if hasattr(sprite, 'rect') and sprite.rect.colliderect(self.hitbox):
                if direction == 'horizontal':
                    if self.direction.x > 0:
                        self.hitbox.right = sprite.rect.left
                    if self.direction.x < 0:
                        self.hitbox.left = sprite.rect.right
                    self.pos.x = self.hitbox.centerx 
                    
                if direction == 'vertical':
                    if self.direction.y > 0:
                        self.hitbox.bottom = sprite.rect.top
                    if self.direction.y < 0:
                        self.hitbox.top = sprite.rect.bottom
                    self.pos.y = self.hitbox.centery

    def import_assets(self):
        self.animations = {"up":[], "down":[], "left":[], "right":[], "up_idle":[], "down_idle":[], "left_idle":[], "right_idle":[]}
        SCALE = 1
        for animation in self.animations.keys():
            full_path = 'graphics/player/' + animation 
            frames = import_folder(full_path)
            
            scaled_frames = []
            for frame in frames:
                new_width = int(frame.get_width() * SCALE)
                new_height = int(frame.get_height() * SCALE)
                scaled_frame = pygame.transform.scale(frame, (new_width, new_height))
                scaled_frames.append(scaled_frame)
                
            self.animations[animation] = scaled_frames
        
    def animate(self, dt):
        if 'idle' in self.status:
            self.frame_index += 2 * dt
        else:
            self.frame_index += 12 * dt
            
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0
        self.image = self.animations[self.status][int(self.frame_index)]
            
    def get_status(self):
        if self.direction.magnitude() == 0:
            self.status = self.status.split('_')[0] + '_idle'

    def move(self, dt):
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()
        
        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.collision('horizontal')
        self.rect.centerx = self.hitbox.centerx
        
        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.collision('vertical')
        self.rect.bottom = self.hitbox.bottom + self.hitbox_offset_y
        
    def update_timers(self):
        for timer in self.timers.values():
            timer.update()        
        
    def update(self, dt):
        self.input()
        self.get_status()
        self.update_timers()
        self.move(dt)
        self.animate(dt)