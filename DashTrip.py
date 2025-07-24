import pygame  # type: ignore
import random
from sys import exit
import os

# ====================== CLASSES ======================
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        player_walk_1 = pygame.image.load('graphics/player_walk_1.png').convert_alpha()
        player_walk_2 = pygame.image.load('graphics/player_walk_2.png').convert_alpha()
        self.player_walk = [player_walk_1, player_walk_2]
        self.player_index = 0
        self.player_jump = pygame.image.load('graphics/jump.png').convert_alpha()

        self.image = self.player_walk[self.player_index]
        self.rect = self.image.get_rect(midbottom=(80, 620))
        self.gravity = 0

        self.jump_sound = pygame.mixer.Sound('audio/audio_jump.mp3')
        self.jump_sound.set_volume(0.5)

    def player_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.rect.bottom >= 620:
            self.gravity = -20
            self.jump_sound.play()

    def apply_gravity(self):
        self.gravity += 1
        self.rect.y += self.gravity
        if self.rect.bottom >= 620: #How Fast the character will fall
            self.rect.bottom = 620

    def animation_state(self):
        if self.rect.bottom < 620:
            self.image = self.player_jump
        else:
            self.player_index += 0.1
            if self.player_index >= len(self.player_walk):
                self.player_index = 0
            self.image = self.player_walk[int(self.player_index)]

    def update(self):
        self.player_input()
        self.apply_gravity()
        self.animation_state()


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, type):
        super().__init__()
        if type == 'ufo':
            ufo_1 = pygame.image.load('graphics/ufo1.png').convert_alpha()
            ufo_2 = pygame.image.load('graphics/ufo2.png').convert_alpha()
            self.frames = [ufo_1, ufo_2]
            y_pos = 500
        else:
            blob_1 = pygame.image.load('graphics/blob1.png').convert_alpha()
            blob_2 = pygame.image.load('graphics/blob2.png').convert_alpha()
            self.frames = [blob_1, blob_2]
            y_pos = 620

        self.animation_index = 0
        self.image = self.frames[self.animation_index]
        self.rect = self.image.get_rect(midbottom=(random.randint(1300, 1500), y_pos))

        # Shrink blob hit box
        if type == 'blob':
            self.rect.inflate_ip(-20, -10)

    def animation_state(self):
        self.animation_index += 0.1 # How fast the characters move
        if self.animation_index >= len(self.frames):
            self.animation_index = 0 # must be at 0 to always be in range
        self.image = self.frames[int(self.animation_index)]

    def update(self):
        self.animation_state()
        self.rect.x -= 6 # How fast the enemies are moving 
        if self.rect.x <= -100:
            self.kill()


# ====================== FUNCTIONS ======================
def display_score():
    current_time = pygame.time.get_ticks() - start_time
    score = current_time // 1000
    score_surf = test_font.render(f'Score: {score}', False, (8, 0, 127))
    score_rect = score_surf.get_rect(center=(screen_width // 2, 100))
    screen.blit(score_surf, score_rect)
    return score

# outline in text
def draw_text_with_outline(surface, text, font, main_color, outline_color, center_pos, thickness=2):
    text_surf = font.render(text, True, main_color)
    text_rect = text_surf.get_rect(center=center_pos)

    for dx in [-thickness, 0, thickness]:
        for dy in [-thickness, 0, thickness]:
            if dx != 0 or dy != 0:
                outline = font.render(text, True, outline_color)
                outline_rect = outline.get_rect(center=(center_pos[0] + dx, center_pos[1] + dy))
                surface.blit(outline, outline_rect)
    surface.blit(text_surf, text_rect)


# ====================== SETUP ======================
pygame.init()

# 🟩 Updated screen resolution
screen_width = 1380
screen_height = 690
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Dash Trip')
clock = pygame.time.Clock()
test_font = pygame.font.Font('font/Pixeltype.ttf', 60)

game_active = False
start_time = 0
score = 0

# Load high score
if os.path.exists("highscore.txt"):
    with open("highscore.txt", "r") as f:
        high_score = int(f.read())
else:
    high_score = 0

# Music
bg_music = pygame.mixer.Sound('audio/music.mp3') # MUSIC CHANGE
bg_music.set_volume(0.5)
bg_music.play(loops= 1)

# Groups
player = pygame.sprite.GroupSingle()
player.add(Player())

obstacle_group = pygame.sprite.Group()

# 🟩 Background & ground scaling
sky_surface = pygame.image.load('graphics/Sky.png').convert()
sky_surface = pygame.transform.scale(sky_surface, (screen_width, screen_height))

ground_surface = pygame.image.load('graphics/Ground.png').convert_alpha()
ground_surface = pygame.transform.scale(ground_surface, (screen_width, 100))

ground_x_pos = 0

# 🟩 Menu assets adjusted
player_stand = pygame.image.load('graphics/player_stand.png').convert_alpha()
player_stand = pygame.transform.scale2x(player_stand)
player_stand_rect = player_stand.get_rect(center=(screen_width // 2, screen_height // 2 - 50))

game_name = test_font.render('Dash Trip', False, (200, 255, 165))
game_name_rect = game_name.get_rect(center=(screen_width // 2, 80))

jump_hint = test_font.render('To jump, press the space bar', False, (255, 162, 0))
jump_hint_rect = jump_hint.get_rect(center=(screen_width // 2, screen_height - 130))

game_message = test_font.render('Press space to start', False, (111, 196, 169))
game_message_rect = game_message.get_rect(center=(screen_width // 2, screen_height - 200))

# Timer
obstacle_timer = pygame.USEREVENT + 1
pygame.time.set_timer(obstacle_timer, 1500)

# ====================== GAME LOOP ======================
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if game_active:
            if event.type == obstacle_timer:
                obstacle_group.add(Obstacle(random.choice(['ufo', 'blob', 'blob', 'blob'])))
        else:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game_active = True
                start_time = pygame.time.get_ticks()
                obstacle_group.empty()

    if game_active:
        # Draw background
        screen.blit(sky_surface, (0, 0))

        # Ground animation
        ground_x_pos -= 5
        if ground_x_pos <= -screen_width:
            ground_x_pos = 0
        screen.blit(ground_surface, (ground_x_pos, screen_height - 100))
        screen.blit(ground_surface, (ground_x_pos + screen_width, screen_height - 100))

        # Game elements
        score = display_score()
        player.draw(screen)
        player.update()
        obstacle_group.draw(screen)
        obstacle_group.update()

        # Collision
        if pygame.sprite.spritecollide(player.sprite, obstacle_group, False):
            game_active = False
            if score > high_score:
                high_score = score
                with open("highscore.txt", "w") as f:
                    f.write(str(high_score))
    
    # Draw Menu/Game Over Screen
    else:
        screen.blit(sky_surface, (0,0))
        screen.blit(player_stand, player_stand_rect)

        screen.blit(sky_surface, (0,0))

        screen.blit(player_stand, player_stand_rect)

        draw_text_with_outline(screen,'Dash Trip',test_font,(200, 255, 165),(0, 0, 0),game_name_rect.center,thickness=2)
        
        if score == 0:
            draw_text_with_outline(screen, 'To jump, press the space bar', test_font, (230, 1, 88), (0, 0, 0), game_message_rect.center, thickness=2)
            draw_text_with_outline(screen, 'Press space to start', test_font, (74, 233, 255), (0, 0, 0), jump_hint_rect.center, thickness=2)

        else:
            draw_text_with_outline(screen, f'Your score: {score}', test_font, (136, 112, 255), (0, 0, 0), (screen_width // 2, screen_height - 250))

            draw_text_with_outline(screen, f'High score: {high_score}', test_font, (249, 255, 0), (0, 0, 0), (screen_width // 2, screen_height - 170))

            draw_text_with_outline(screen, 'Press Space To Play Again', test_font, (200, 200, 200), (0, 0, 0), (screen_width // 2, screen_height - 90))

            draw_text_with_outline(screen,'Dash Trip',test_font,(200, 255, 165),(0, 0, 0),game_name_rect.center,thickness=2)

    pygame.display.update()
    clock.tick(60)

   #https://www.youtube.com/watch?v=AY9MnQ4x3zk 

  #copy and paste python DashTrip.py into terminal
