import random
import math
from pygame import Rect

# --------------------------------------------------------------------
# Window / world
# --------------------------------------------------------------------
WIDTH = 800
HEIGHT = 480
LEVEL_WIDTH = 2400   

# --------------------------------------------------------------------
# states
# --------------------------------------------------------------------
game_state = "menu"   # "menu", "game", "pause", "gameover"
sound_enabled = False

# --------------------------------------------------------------------
# consts
# --------------------------------------------------------------------
GRAVITY = 0.5
# --------------------------------------------------------------------
# simple cam (only x, y)
# --------------------------------------------------------------------
camera_x = 0
camera_y = 0

#points and time change for every phase it can be improved
points_to_win =  5
time_to_win = 5

def clamp(v, a, b):
    return max(a, min(b, v))
timer = 30
timer_game_over = False

#level/phase actual 
level = 1

# --------------------------------------------------------------------
# PLAYER
# --------------------------------------------------------------------
class Player:
    def __init__(self, x=200, y=350):
        self.actor = Actor("player_idle1", (x, y))
        self.start_x = x
        self.start_y = y

        self.vel_x = 0
        self.vel_y = 0
        self.speed = 3.5
        self.jump_power = -10

        # sprites from Kenny
        self.idle_frames = ["player_idle1", "player_idle2"]
        self.run_frames_right = ["player_run1", "player_run2", "player_run3", "player_run4"]
        self.run_frames_left = ["player_run_left1", "player_run2", "player_run3", "player_run4"]
        self.frame = 0
        self.anim_timer = 0
        self.is_running = False
        self.direction = 0

        self.lives = 3
        self.invulnerable = 0   # ticks of invulnerability

        # score
        self.score = 0

    @property
    def x(self):
        return self.actor.x

    @x.setter
    def x(self, v):
        self.actor.x = v

    @property
    def y(self):
        return self.actor.y

    @y.setter
    def y(self, v):
        self.actor.y = v

    def update(self):
        self.handle_input()
        self.apply_gravity()
        self.move_horizontal()
        self.check_platform_collisions()
        self.update_animation()

        if self.invulnerable > 0:
            self.invulnerable -= 1

    def handle_input(self):
        self.is_running = False
        self.vel_x = 0

        if keyboard.left:
            self.vel_x = -self.speed
            self.is_running = True
            self.direction = "left"
        if keyboard.right:
            self.vel_x = self.speed
            self.is_running = True
            self.direction = "right"

        if keyboard.up and self.on_ground():
            self.vel_y = self.jump_power
            try:
                if sound_enabled:
                    sounds.jump.play()
            except:
                pass

    def apply_gravity(self):
        self.vel_y += GRAVITY
        self.actor.y += self.vel_y

    def move_horizontal(self):
        self.actor.x += self.vel_x
        self.actor.x = clamp(self.actor.x, 0, LEVEL_WIDTH)

    def on_ground(self):
        # base floor
        if self.actor.y >= 350:
            return True
        # plataforms
        for p in all_platforms:
            # check collision using Rect (world coords)
            player_rect = Rect(self.actor.x - self.actor.width/5, self.actor.y - self.actor.height/3, self.actor.width, self.actor.height)
            if player_rect.colliderect(p.rect):
                if self.actor.y <= p.rect.top + 2:
                    return True
        return False

    def check_platform_collisions(self):
        # when player fall
        if self.vel_y >= 0:
            for p in all_platforms:
                player_rect = Rect(self.actor.x - self.actor.width/2, self.actor.y - self.actor.height/2, self.actor.width, self.actor.height)
                if player_rect.colliderect(p.rect):
                    # only consider is a colision if player on top 
                    if self.actor.y - self.vel_y <= p.rect.top:
                        # set player on top of the platform
                        self.actor.y = p.rect.top - 50
                        self.vel_y = 0

        # if fall besides the floor death
        if self.actor.y > HEIGHT + 200:
            self.die()

    def update_animation(self):
        self.anim_timer += 1
        if self.anim_timer < 8:
            return
        self.anim_timer = 0

        if self.is_running:
            if self.direction=="right":
                self.frame = (self.frame + 1) % len(self.run_frames_right)
                self.actor.image = self.run_frames_right[self.frame]
            elif self.direction=="left":
                self.frame = (self.frame + 1) % len(self.run_frames_left)
                self.actor.image = self.run_frames_left[self.frame]
        else:
            self.frame = (self.frame + 1) % len(self.idle_frames)
            self.actor.image = self.idle_frames[self.frame]

    def draw(self):
        old_x, old_y = self.actor.x, self.actor.y
        self.actor.x = old_x - camera_x
        self.actor.y = old_y - camera_y
    
        if not timer_game_over:
            screen.draw.text(f"Tempo: {timer}", (230, 20), fontsize=40)
        else:
            self.timer_game_over = True
            self.game_over()
            screen.draw.text("FIM DE JOGO!", (200, 300), fontsize=80, color="red")
        if self.invulnerable > 0 and (self.invulnerable // 6) % 2 == 0:
            pass
        else:
            self.actor.draw()

        # restore coord
        self.actor.x, self.actor.y = old_x, old_y

    def take_damage(self):
        if self.invulnerable > 0:
            return
        self.lives -= 1
        self.invulnerable = 90  # ~1.5 seg a 60fps
        try:
            if sound_enabled:
                sounds.hurt.play()
        except:
            pass
        if self.lives <= 0:
            self.game_over()
        elif timer_game_over:
            self.game_over()
        else:
            self.respawn()

    def die(self):
        # when jump and fall
        self.take_damage()

    def respawn(self):
        self.actor.x = self.start_x
        self.actor.y = self.start_y
        self.vel_x = 0
        self.vel_y = 0

    def game_over(self):
        global game_state
        game_state = "gameover"
        reset_timer() 
        try:
            if sound_enabled:
                music.stop()
        except:
            pass


# --------------------------------------------------------------------
# Platforms
# --------------------------------------------------------------------
class Platform:
    def __init__(self, x, y, w, h, move_type=None, move_range=0, speed=0):
        self.rect = Rect(x, y, w, h)   # world coords
        self.move_type = move_type
        self.move_range = move_range
        self.speed = speed
        self.origin_x = x
        self.origin_y = y
        self.dir = 1

    def update(self):
        if self.move_type == "horizontal":
            self.rect.x += self.speed * self.dir
            if abs(self.rect.x - self.origin_x) > self.move_range:
                self.dir *= -1
        elif self.move_type == "vertical":
            self.rect.y += self.speed * self.dir
            if abs(self.rect.y - self.origin_y) > self.move_range:
                self.dir *= -1

    def draw(self):
        # draw with cam offset
        draw_rect = Rect(self.rect.x - camera_x, self.rect.y - camera_y, self.rect.width, self.rect.height)
        screen.draw.filled_rect(draw_rect, (120, 75, 20))

# --------------------------------------------------------------------
# enemys
# --------------------------------------------------------------------
class Enemy:
    def __init__(self, x, y, left_bound, right_bound, speed=1.5, picture='',points = 0):
        self.actor = Actor(picture, (x, y))
        self.left = left_bound
        self.right = right_bound
        self.speed = speed
        self.dir = 1
        self.alive = True
        self.points = points

    def update(self):
        if not self.alive:
            return
        self.actor.x += self.speed * self.dir
        if self.actor.x < self.left:
            self.actor.x = self.left
            self.dir = 1
        if self.actor.x > self.right:
            self.actor.x = self.right
            self.dir = -1

        if self.collide_with_player():
            if player.vel_y > 0 and player.y < self.actor.y:
                self.alive = False
                try:
                    if sound_enabled:
                        sounds.enemy_die.play()
                except:
                    pass
                player.vel_y = player.jump_power / 2
                player.score += self.points
            else:
                player.take_damage()

    def collide_with_player(self):
        if not self.alive:
            return False
        e_rect = Rect(self.actor.x - self.actor.width/2, self.actor.y - self.actor.height/2, self.actor.width, self.actor.height)
        p_rect = Rect(player.x - player.actor.width/2, player.y - player.actor.height/2, player.actor.width, player.actor.height)
        return e_rect.colliderect(p_rect)

    def draw(self):
        if not self.alive:
            return
        old_x, old_y = self.actor.x, self.actor.y
        self.actor.x -= camera_x
        self.actor.y -= camera_y
        self.actor.draw()
        self.actor.x, self.actor.y = old_x, old_y

# --------------------------------------------------------------------
# coins
# --------------------------------------------------------------------
class Coin:
    def __init__(self, x, y, picture = '',points = 0, time_bonus = 0, win = False):
        self.actor = Actor(picture, (x, y))
        self.collected = False
        self.points = points
        self.time_bonus = time_bonus
        self.win = win
 
    def update(self):
        global timer,level
        if self.collected:
            return
        # check colision with player
        c_rect = Rect(self.actor.x - self.actor.width/2, self.actor.y - self.actor.height/2, self.actor.width, self.actor.height)
        p_rect = Rect(player.x - player.actor.width/2, player.y - player.actor.height/2, player.actor.width, player.actor.height)
        if c_rect.colliderect(p_rect):
            self.collected = True
            if self.points//level >= 1:
                player.score += self.points//level
            else: 
                player.score += 1
            timer += self.time_bonus//level
            if self.win:
                self.game_over_win()
            try:
                if sound_enabled:
                    sounds.coin.play()
            except:
                pass

    def draw(self):
        if self.collected:
            return
        old_x, old_y = self.actor.x, self.actor.y
        self.actor.x -= camera_x
        self.actor.y -= camera_y
        self.actor.draw()
        self.actor.x, self.actor.y = old_x, old_y
    def game_over_win(self):
        global game_state,level
        game_state = "gameoverwin"
        level += 1
        reset_timer() 
        try:
            if sound_enabled:
                music.stop()
        except:
            pass

# --------------------------------------------------------------------
# Phase objects
# --------------------------------------------------------------------
player = Player()

# plataforms
platforms_static = [
    Platform(50, 380, 300, 20),
    Platform(420, 320, 160, 20),
    Platform(700, 280, 140, 20),
    Platform(980, 340, 200, 20),
    Platform(1300, 300, 220, 20),
    Platform(2000, 210, 250, 20),
    Platform(2300, 400, 260, 20),
    Platform(2800, 330, 120, 20),
]

platforms_moving = [
    Platform(1600, 260, 180, 20, move_type="horizontal", move_range=200, speed=2),
    Platform(1800, 180, 140, 20, move_type="vertical", move_range=60, speed=1.2),
]

all_platforms = platforms_static + platforms_moving

# enemys
enemies = [
    Enemy(520, 290, 500, 640, speed=1.2, picture="enemy1", points = 10),
    Enemy(1020, 320, 980, 1180, speed=1.0, picture="enemy2", points = 50),
]

# coins
coins = [
    Coin(460, 300,"coin",points_to_win,time_to_win,False),
    Coin(740, 260,"coin",points_to_win,time_to_win,False),
    Coin(1060, 320,"coin",points_to_win,time_to_win,False),
    Coin(1400, 280,"coin",points_to_win,time_to_win,False),
    Coin(1650, 240,"coin",points_to_win,time_to_win,False),
    Coin(1950, 250,"gem_red",points_to_win+10,time_to_win+10,False),
    Coin(2150, 200,"coin",points_to_win,time_to_win,False),
    Coin(2350,375,"flag_blue_a",points_to_win,time_to_win,True),
]   

# --------------------------------------------------------------------
# MENU / INPUT  mouse
# --------------------------------------------------------------------
def draw_menu():
    state = "ON" if sound_enabled else "OFF"
    screen.clear()
    screen.blit("menu_bg", (0, 0))  
    screen.draw.text("Welcome", center=(WIDTH//2, 100), fontsize=64)
    screen.draw.text("Start Game", center=(WIDTH//2, 220), fontsize=40)
    screen.draw.text("Sound: " + state, center=(WIDTH//2, 300), fontsize=40)
    screen.draw.text("Exit", center=(WIDTH//2, 380), fontsize=40)
def on_mouse_down(pos):
    global game_state, sound_enabled
    sounds.click.play()
    if game_state == "menu":
        if 180 < pos[1] < 260:
            start_game()
        elif 260 < pos[1] < 340:
            if sound_enabled:
                sound_enabled = not sound_enabled
                music.stop()
                #screen.draw.text("Sound: OFF", center=(WIDTH//2, 300), fontsize=40)
            else:
                 sound_enabled = not sound_enabled
                 music.play("bg_music")
                 music.set_volume(0.5)
                 #screen.draw.text("Sound: ON", center=(WIDTH//2, 300), fontsize=40)
        elif 340 < pos[1] < 420:
            game_state = "exit"
    elif game_state == "gameover":
        # click restart
        start_game()
    elif game_state == "gameoverwin":
        # click restart
        start_game()

# --------------------------------------------------------------------
# Helpers: start_game
# --------------------------------------------------------------------
def start_game():
    global game_state, camera_x,timer,timer_game_over
    # reset player and objects
    player.actor.x = player.start_x
    player.actor.y = player.start_y
    player.vel_x = 0
    player.vel_y = 0
    player.lives = 3
    player.score = 0
    player.invulnerable = 0
    timer_game_over = False
    timer = 30

    # reset enemys / coins
    for e in enemies:
        e.alive = True
    for c in coins:
        c.collected = False

    camera_x = 0
    game_state = "game"
    try:
        if sound_enabled:
            music.play("bg_music")
            music.set_volume(20.5)
    except:
        pass

# --------------------------------------------------------------------
# DRAW 
# --------------------------------------------------------------------
def draw():
    screen.clear()
    if game_state == "menu":
        draw_menu()
        return

    if game_state == "game" or game_state == "pause":
        screen.fill((120, 180, 255))
        ground_rect = Rect(0 - camera_x, 380 - camera_y, LEVEL_WIDTH, HEIGHT - 380)
        screen.draw.filled_rect(ground_rect, (80, 160, 60))

        # draw plataforms
        for p in all_platforms:
            p.draw()

        # draw coins / enemys / players
        for c in coins:
            c.draw()
        for e in enemies:
            e.draw()
        player.draw()

        # HUD
        screen.draw.text(f"Score: {player.score}", (10, 10), fontsize=30)
        screen.draw.text(f"Lives: {player.lives}", (10, 40), fontsize=28)
        screen.draw.text(f"Level Round: {level}", (10, 70), fontsize=28)

    elif game_state == "gameover":
        screen.fill("black")
        screen.draw.text("GAME OVER", center=(WIDTH//2, HEIGHT//2 - 30), fontsize=64)
        screen.draw.text("Click to retry", center=(WIDTH//2, HEIGHT//2 + 30), fontsize=30)
    
    elif game_state == "gameoverwin":
        screen.fill("blue")
        screen.draw.text("CONGRATULATIONS! YOU WIN", center=(WIDTH//2, HEIGHT//2 - 30), fontsize=64)
        screen.draw.text("Click to play next phase!", center=(WIDTH//2, HEIGHT//2 + 30), fontsize=30)


    elif game_state == "exit":
        screen.clear()
        screen.draw.text("Goodbye!", center=(WIDTH//2, HEIGHT//2), fontsize=40)

# --------------------------------------------------------------------
# main UPDATE
# --------------------------------------------------------------------
def update():
    global camera_x, camera_y

    if game_state != "game":
        return

    # update objects
    player.update()
    for p in platforms_moving:
        p.update()
    for e in enemies:
        e.update()
    for c in coins:
        c.update()

    # set cam in X following the player
    target_x = player.x - WIDTH // 2
    camera_x = clamp(target_x, 0, LEVEL_WIDTH - WIDTH)
    camera_y = 0

#--------------------------------------------------------------------
#timer
#--------------------------------------------------------------------
def diminuir_tempo():
    global timer, timer_game_over
    timer -= 1

    if timer > 0:
        clock.schedule(diminuir_tempo, 1)  # call again in 1 seg
    else:
        timer_game_over = True
def reset_timer():
    global timer, game_over

    timer = 30
    game_over = False

    # cancel old calls if their exists
    clock.unschedule(diminuir_tempo)

    # Starts timer again;
    clock.schedule(diminuir_tempo, 1)

clock.schedule(diminuir_tempo, 1)


# --------------------------------------------------------------------
# Plays back souns if it exists!
# --------------------------------------------------------------------
try:
    if sound_enabled:
        #sounds.bg_music.play()
        music.play("bg_music")
        music.set_volume(0.5)
except:
    pass


