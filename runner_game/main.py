import random
import pgzrun
from pgzero.actor import Actor

# --- Ayarlar ---
WIDTH, HEIGHT = 800, 400
ground_y = HEIGHT - 50

# Oyun durumları ve ses kontrol
game_state = 'menu'      # 'menu', 'playing', 'game_over'
sound_on = True

# Spawn zamanlayıcıları
spawn_timer = 0
next_spawn_interval = 0

# Skor
score = 0

# Arka plan kaydırma
bg_x = 0
bg_speed = 100  # px/sn

# --- UI Butonları ---
start_button   = Rect((WIDTH//2 - 100, HEIGHT//2 - 60), (200, 50))
sound_button   = Rect((WIDTH//2 - 100, HEIGHT//2    ), (200, 50))
exit_button    = Rect((WIDTH//2 - 100, HEIGHT//2 + 60), (200, 50))
restart_button = Rect((WIDTH//2 - 100, HEIGHT//2 + 20), (200, 50))

# --- Oyun Objeleri ---
hero = None
obstacles = []

# --- Sınıflar ---
class Hero:
    def __init__(self):
        self.images = ['hero0', 'hero1']
        self.frame = 0
        self.anim_timer = 0
        self.actor = Actor(self.images[self.frame], (100, ground_y))
        self.vy = 0
        self.on_ground = True

    def update(self, dt):
        # Sprite animasyonu
        self.anim_timer += dt
        if self.anim_timer > 0.1:
            self.anim_timer = 0
            self.frame = (self.frame + 1) % len(self.images)
            self.actor.image = self.images[self.frame]
        # Yerçekimi
        self.vy += 800 * dt
        self.actor.y += self.vy * dt
        if self.actor.y >= ground_y:
            self.actor.y = ground_y
            self.vy = 0
            self.on_ground = True

    def jump(self):
        if self.on_ground:
            self.vy = -350
            self.on_ground = False
            if sound_on:
                sounds.jump.play()

class Obstacle:
    def __init__(self, x):
        self.actor = Actor('obstacle', (x, ground_y))
    def update(self, dt):
        self.actor.x -= 250 * dt
    def off_screen(self):
        return self.actor.x < -self.actor.width

# --- Çizim Fonksiyonları ---
def draw():
    screen.clear()
    if game_state == 'menu':
        draw_menu()
    elif game_state == 'playing':
        draw_game()
    else:
        draw_game_over()

def draw_menu():
    screen.fill((30, 30, 30))
    screen.draw.text("RUNNER OYUNU", center=(WIDTH//2, HEIGHT//2 - 120),
                     fontsize=50, color="white")
    screen.draw.filled_rect(start_button, "dodgerblue")
    screen.draw.text("Oyuna Başla", center=start_button.center,
                     fontsize=30, color="white")
    screen.draw.filled_rect(sound_button, "gray")
    status = "Açık" if sound_on else "Kapalı"
    screen.draw.text(f"Ses: {status}", center=sound_button.center,
                     fontsize=30, color="white")
    screen.draw.filled_rect(exit_button, "red")
    screen.draw.text("Çıkış", center=exit_button.center,
                     fontsize=30, color="white")

def draw_game():
    # Kayan arka plan
    screen.blit('background', (bg_x, 0))
    screen.blit('background', (bg_x + WIDTH, 0))
    # Oyun objeleri
    hero.actor.draw()
    for obs in obstacles:
        obs.actor.draw()
    screen.draw.text(f"Skor: {int(score)}", topright=(WIDTH-10, 10),
                     fontsize=30, color="white")

def draw_game_over():
    screen.fill("black")
    screen.draw.text("OYUN BİTTİ", center=(WIDTH//2, HEIGHT//2 - 80),
                     fontsize=60, color="white")
    screen.draw.filled_rect(restart_button, "green")
    screen.draw.text("Tekrar Başlat", center=restart_button.center,
                     fontsize=30, color="white")

# --- Olaylar & Güncellemeler ---
def on_mouse_down(pos):
    global game_state, sound_on
    if game_state == 'menu':
        if start_button.collidepoint(pos):
            start_playing()
        elif sound_button.collidepoint(pos):
            sound_on = not sound_on
            if sound_on:
                sounds.bgm.set_volume(0.6); sounds.bgm.play(-1)
            else:
                sounds.bgm.stop()
        elif exit_button.collidepoint(pos):
            exit()
    elif game_state == 'game_over':
        if restart_button.collidepoint(pos):
            start_playing()

def on_key_down(key):
    if game_state == 'playing' and key == keys.SPACE:
        hero.jump()

def update(dt):
    global bg_x
    if game_state == 'playing':
        # Arka plan kaydır
        bg_x -= bg_speed * dt
        if bg_x <= -WIDTH:
            bg_x += WIDTH
        update_game(dt)

def update_game(dt):
    global spawn_timer, score, game_state, next_spawn_interval
    hero.update(dt)
    spawn_timer += dt
    if spawn_timer > next_spawn_interval:
        spawn_timer = 0
        next_spawn_interval = random.uniform(1.5, 3.0)
        obstacles.append(Obstacle(WIDTH + 50))
    for obs in list(obstacles):
        obs.update(dt)
        if obs.off_screen():
            obstacles.remove(obs)
        if hero.actor.colliderect(obs.actor):
            if sound_on:
                sounds.hit.play()
                sounds.bgm.stop()
            game_state = 'game_over'
    score += dt * 10

# --- Yardımcı Fonksiyonlar ---
def start_playing():
    global game_state
    reset_game()
    game_state = 'playing'
    if sound_on:
        sounds.bgm.set_volume(0.6)
        sounds.bgm.play(-1)

def reset_game():
    global hero, obstacles, score, spawn_timer, next_spawn_interval, bg_x
    hero = Hero()
    obstacles = []
    score = 0
    spawn_timer = 0
    next_spawn_interval = random.uniform(1.5, 3.0)
    bg_x = 0

# --- Oyun Başlat ---
reset_game()
pgzrun.go()
