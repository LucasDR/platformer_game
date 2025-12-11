import random
import math

WIDTH = 800
HEIGHT = 480

# -----------------------------
# ESTADOS DO JOGO
# -----------------------------
game_state = "menu"  # menu, game, exit
sound_enabled = True

# -----------------------------
# JOGADOR
# -----------------------------
GRAVITY = 0.5

class Player:
    def __init__(self):
        self.actor = Actor("player_idle1")   # sprite inicial
        self.actor.x = 200
        self.actor.y = 350

        # movimento
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 3
        self.jump_power = -10

        # animação
        self.frame = 0
        self.anim_timer = 0
        self.idle_frames = ["player_idle1", "player_idle2"]
        self.run_frames = ["player_run1", "player_run2", "player_run3", "player_run4"]
        self.is_running = False

    def update(self):
        self.handle_input()
        self.apply_gravity()
        self.move()
        self.animate()

    def handle_input(self):
        self.is_running = False

        # MOVIMENTO HORIZONTAL
        if keyboard.left:
            self.vel_x = -self.speed
            self.is_running = True
        elif keyboard.right:
            self.vel_x = self.speed
            self.is_running = True
        else:
            self.vel_x = 0

        # PULO
        if keyboard.up and self.on_ground():
            self.vel_y = self.jump_power

    def apply_gravity(self):
        self.vel_y += GRAVITY

    def move(self):
        # mover horizontal
        self.actor.x += self.vel_x

        # limites da tela
        self.actor.x = max(0, min(WIDTH, self.actor.x))

        # mover vertical
        self.actor.y += self.vel_y

        # chão
        if self.actor.y >= 350:
            self.actor.y = 350
            self.vel_y = 0

    def on_ground(self):
        return self.actor.y >= 350

    def animate(self):
        self.anim_timer += 1

        if self.anim_timer < 10:
            return

        self.anim_timer = 0
        self.frame += 1

        if self.is_running:
            if self.frame >= len(self.run_frames):
                self.frame = 0
            self.actor.image = self.run_frames[self.frame]

        else:
            if self.frame >= len(self.idle_frames):
                self.frame = 0
            self.actor.image = self.idle_frames[self.frame]

    def draw(self):
        self.actor.draw()


# Criar o player
player = Player()


# -----------------------------
# MENU
# -----------------------------
def draw_menu():
    screen.clear()
    screen.draw.text("My Platformer", center=(WIDTH//2, 100), fontsize=60)

    screen.draw.text("Start Game", center=(WIDTH//2, 220), fontsize=40)
    screen.draw.text("Sound: ON/OFF", center=(WIDTH//2, 300), fontsize=40)
    screen.draw.text("Exit", center=(WIDTH//2, 380), fontsize=40)


def on_mouse_down(pos):
    global game_state, sound_enabled

    if game_state == "menu":
        # Start
        if 180 < pos[1] < 260:
            game_state = "game"

        # Toggle sound
        elif 260 < pos[1] < 340:
            sound_enabled = not sound_enabled

        # Exit
        elif 340 < pos[1] < 420:
            game_state = "exit"


# -----------------------------
# DRAW PRINCIPAL
# -----------------------------
def draw():
    screen.clear()

    if game_state == "menu":
        draw_menu()

    elif game_state == "game":
        screen.fill((120, 180, 255))  # fundo azul claro
        # chão
        screen.draw.filled_rect(Rect((0, 380), (WIDTH, 100)), (50, 200, 50))

        player.draw()

    elif game_state == "exit":
        screen.draw.text("Goodbye!", center=(WIDTH//2, HEIGHT//2), fontsize=40)


# -----------------------------
# UPDATE PRINCIPAL
# -----------------------------
def update():
    if game_state == "game":
        player.update()
