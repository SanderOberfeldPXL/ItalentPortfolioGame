import pygame
from settings import *
from support import *
from timer import Timer

class Player(pygame.sprite.Sprite):
    
    def __init__(self, pos, group, collision_sprites):
        
        super().__init__(group)
        self.collision_sprites = collision_sprites
        
        self.import_assets()
        self.status = 'down_idle'
        self.frame_index = 0
        
        
        # generic setup
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center = pos)
        
        self.hitbox = self.rect.inflate(-64, -90)
        self.hitbox_offset_y = 18
        self.hitbox.bottom = self.rect.bottom - self.hitbox_offset_y
        
        self.z = LAYERS['main']
        
        # movement attribvutes
        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.hitbox.center)
        self.speed = 200
        
        #timers
        self.timers = {
                'equipment use': Timer(350, self.use_equipment),
                'equipment switch': Timer(200)
        }
        
        #equip
        self.equipment = ['axe']
        self.equipment_index = 0
        self.selected_equipment = self.equipment[self.equipment_index]
        
        
    def use_equipment(self):
        return
    
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
        self.animations = {"up":[], "down":[], "left":[], "right":[], "up_idle":[], "down_idle":[], "left_idle":[], "right_idle":[], "up_axe":[], "down_axe":[], "left_axe":[], "right_axe":[]}
        
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
        
        
    def input(self):
        keys = pygame.key.get_pressed()
        
        if not self.timers['equipment use'].active:
        
            if keys[pygame.K_LEFT]:
                self.direction.x = -1
                self.status = 'left'
            elif keys[pygame.K_RIGHT]:
                self.direction.x = 1
                self.status = 'right'
            else:
                self.direction.x = 0
        
            # movements
            if keys[pygame.K_UP]:
                self.direction.y = -1
                self.status = 'up'
            elif keys[pygame.K_DOWN]:
                self.direction.y = 1
                self.status = 'down'
            else:
                self.direction.y = 0
            
            
            #equipment
            #use equipment
            if keys[pygame.K_SPACE]:
                self.timers['equipment use'].activate()
                self.direction = pygame.math.Vector2()
                self.frame_index = 0

            # cycle equipment
            if keys[pygame.K_a] and not self.timers['equipment switch'].active:
                self.timers['equipment switch'].activate()
                self.equipment_index += 1
                if self.equipment_index >= len(self.equipment):
                    self.equipment_index = 0
                self.selected_equipment = self.equipment[self.equipment_index]
    
    def get_status(self):
        #idle?
        if self.direction.magnitude() == 0:
            self.status = self.status.split('_')[0] + '_idle'
    
        if self.timers['equipment use'].active:
            self.status = self.status.split('_')[0] + '_' + self.selected_equipment
    

    def move(self, dt):
        #diagonal stuff
        if self .direction.magnitude() > 0:
            self.direction = self.direction.normalize()
        
        # horizontal movement 
        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.collision('horizontal')
        self.rect.centerx = self.hitbox.centerx
        
        # vertical movement
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