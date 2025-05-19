# Tiny Tractor Tycoon — Rabbits Edition
# --------------------------------------------------
# A bite‑sized, coin‑driven farming sim in a single Python + Pygame file.
# Now mischievous rabbits spawn when crops are ripe and will happily munch
# on your harvest unless you beat them to it!
"""
Controls
• WASD – move 🚜 (wraps at edges)
• 1‑6  – choose seed
• SPACE – plant / harvest
•  F   – fertilize (5 💰)
• ESC  – quit

New features
• 🐇 Rabbits spawn the moment a crop reaches stage 3 (harvestable).
• Rabbits wander the field every few frames.
• If a rabbit lands on a harvest‑ready crop, it eats it — the crop is lost!
• Rabbits are indestructible; plan your timing wisely.
"""

import math
import random
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import pygame

# ──────────────────────────────── CONSTANTS ──────────────────────────────── #
TILE              = 64
COLS, ROWS        = 8, 6
FIELD_W, FIELD_H  = COLS * TILE, ROWS * TILE
SIDEBAR_W         = 220         # widened a little for breathing room
WIN_W, WIN_H      = FIELD_W + SIDEBAR_W, FIELD_H
FPS               = 60
RABBIT_MOVE_INT   = 0.6         # seconds between rabbit hops

# Sidebar layout tweaks
SEED_TITLE_PAD_Y  = 20       # padding from top for "Seeds" title
SEED_START_Y      = SEED_TITLE_PAD_Y + 24
SEED_ROW_H        = 40       # vertical space per seed row (reduced)
SEED_KEY_X_OFF    = 10       # x‑offsets within sidebar
SEED_EMOJI_X_OFF  = 30
SEED_COST_X_OFF   = 80
LEGEND_EXTRA_PAD  = 16       # gap between last seed row and legend

# ──────────────────────────────── CROP DATA ──────────────────────────────── #
@dataclass(frozen=True)
class CropType:
    key: str
    name: str
    emojis: tuple    # 4‑tuple of stage emojis
    grow_time: float # seconds (stage 0‑3 total)
    seed_cost: int
    reward: int

CROPS = [
    CropType("1", "Corn",     ("🫘","🌱","🌾","🌽"), 240, 5, 12),
    CropType("2", "Potato",   ("🥔","🌱","🌿","🥔"), 210, 4, 10),
    CropType("3", "Tomato",   ("🍅","🌱","🌿","🍅"), 180, 4, 10),
    CropType("4", "Bean",     ("🫘","🌱","🌿","🫘"), 150, 3,  8),
    CropType("5", "Cabbage",  ("🥬","🌱","🌿","🥬"), 270, 6, 15),
    CropType("6", "Broccoli", ("🥦","🌱","🌿","🥦"), 300, 7, 18),
]
CROP_BY_KEY = {c.key: c for c in CROPS}

# ──────────────────────────────── TILE & RABBIT DATA ─────────────────────── #
@dataclass
class Tile:
    crop      : CropType | None = None
    planted_at: float  = 0.0
    stage     : int    = 0
    fertilized: bool   = False
    flash_to  : float  = 0.0     # yellow‑flash timer
    sparkle_t : float  = 0.0     # sparkle anim start

@dataclass
class Rabbit:
    x: int
    y: int
    next_move: float = 0.0      # timestamp of next hop

# ──────────────────────────────── GAME CLASS ──────────────────────────────── #
class TinyTractorTycoon:
    def __init__(self):
        pygame.init()
        self.screen  = pygame.display.set_mode((WIN_W, WIN_H))
        pygame.display.set_caption("🚜 Tiny Tractor Tycoon — Rabbits Edition")
        self.clock   = pygame.time.Clock()

        # ─── Fonts ─────────────────── #
        emoji_font_name = next((f for f in pygame.font.get_fonts() if "emoji" in f), None)
        self.emoji_font = pygame.font.SysFont(emoji_font_name, 48) if emoji_font_name else pygame.font.SysFont(None, 48)
        self.ui_font    = pygame.font.SysFont(None, 24)
        self.small_font = pygame.font.SysFont(None, 18)
        # Smaller fonts for sidebar
        self.sidebar_emoji_font = pygame.font.SysFont(emoji_font_name, 32) if emoji_font_name else pygame.font.SysFont(None, 32)
        self.sidebar_ui_font = pygame.font.SysFont(None, 20)

        # ─── Field state ───────────── #
        self.grid = [[Tile() for _ in range(ROWS)] for _ in range(COLS)]

        # ─── Player state ──────────── #
        self.x, self.y   = 0, 0          # tile coordinates
        self.selected    = CROPS[0]      # currently selected seed
        self.coins       = 25
        self.harvest_log = {c: 0 for c in CROPS}

        # ─── Rabbits ────────────────── #
        self.rabbits: list[Rabbit] = []

        # ─── Pre‑render crop emoji surfaces ──────────── #
        self.crop_img = {
            (c, s): self.emoji_font.render(c.emojis[s], True, (255, 255, 255))
            for c in CROPS for s in range(3)
        }
        # Stage‑3 will pulse alpha, so keep text surface without alpha preset:
        self.crop_img_stage3 = {c: self.emoji_font.render(c.emojis[3], True, (255, 255, 255)) for c in CROPS}
        # Sparkle surface
        self.sparkle = self.emoji_font.render("✨", True, (255, 255, 255))
        # Tractor
        self.tractor_img = self.emoji_font.render("🚜", True, (255, 255, 255))
        # Rabbit
        self.rabbit_img  = self.emoji_font.render("🐇", True, (255, 255, 255))

    # ─────────────────────────────────────────────────────────────────── #
    def run(self):
        while True:
            dt  = self.clock.tick(FPS) / 1000.0
            now = time.time()
            self.handle_input(now)
            self.update_growth(now)
            self.update_rabbits(now)
            self.render(now)

    # ─────────────────────────────────────────────────────────────────── #
    def handle_input(self, now):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                match event.key:
                    case pygame.K_ESCAPE: pygame.event.post(pygame.event.Event(pygame.QUIT))
                    case pygame.K_w: self.y = (self.y - 1) % ROWS
                    case pygame.K_s: self.y = (self.y + 1) % ROWS
                    case pygame.K_a: self.x = (self.x - 1) % COLS
                    case pygame.K_d: self.x = (self.x + 1) % COLS
                    case pygame.K_SPACE: self.handle_action(now)
                    case pygame.K_f: self.handle_fertilizer(now)
                    case _:
                        key = pygame.key.name(event.key)
                        if key in CROP_BY_KEY:
                            self.selected = CROP_BY_KEY[key]

    # ─────────────────────────────────────────────────────────────────── #
    def handle_action(self, now):
        tile = self.grid[self.x][self.y]
        if tile.crop is None:
            # Plant seed
            c = self.selected
            if self.coins >= c.seed_cost:
                self.coins -= c.seed_cost
                tile.crop       = c
                tile.planted_at = now
                tile.stage      = 0
                tile.fertilized = False
                tile.flash_to   = now + 0.3
        elif tile.stage == 3:
            # Harvest
            self.coins += tile.crop.reward
            self.harvest_log[tile.crop] += 1
            self.grid[self.x][self.y] = Tile()   # reset tile

    # ─────────────────────────────────────────────────────────────────── #
    def handle_fertilizer(self, now):
        if self.coins < 5:
            return
        tile = self.grid[self.x][self.y]
        if tile.crop and not tile.fertilized:
            self.coins -= 5
            elapsed = now - tile.planted_at
            remaining = max(tile.crop.grow_time - elapsed, 0)
            tile.planted_at -= remaining / 2    # halve remaining time
            tile.fertilized  = True
            tile.sparkle_t   = now

    # ─────────────────────────────────────────────────────────────────── #
    def update_growth(self, now):
        for gx in range(COLS):
            for gy in range(ROWS):
                tile = self.grid[gx][gy]
                if tile.crop is None or tile.stage == 3:
                    continue
                elapsed = now - tile.planted_at
                new_stage = min(int((elapsed / tile.crop.grow_time) * 4), 3)
                if new_stage != tile.stage:
                    # Crop just advanced a stage
                    if new_stage == 3:
                        self.spawn_rabbit()
                    tile.stage = new_stage

    # ─────────────────────────────────────────────────────────────────── #
    def spawn_rabbit(self):
        """Spawn a rabbit at a random tile (avoiding player tile)."""
        for _ in range(30):  # try a few times to avoid overcrowding one spot
            rx = random.randrange(COLS)
            ry = random.randrange(ROWS)
            if (rx, ry) != (self.x, self.y):
                break
        self.rabbits.append(Rabbit(rx, ry, time.time() + random.random() * RABBIT_MOVE_INT))

    # ─────────────────────────────────────────────────────────────────── #
    def update_rabbits(self, now):
        for rabbit in self.rabbits:
            # Move occasionally
            if now >= rabbit.next_move:
                dx, dy = random.choice([(0, -1), (0, 1), (-1, 0), (1, 0)])
                rabbit.x = (rabbit.x + dx) % COLS
                rabbit.y = (rabbit.y + dy) % ROWS
                rabbit.next_move = now + RABBIT_MOVE_INT
            # Check for munching
            tile = self.grid[rabbit.x][rabbit.y]
            if tile.crop and tile.stage == 3:
                # Rabbit eats the crop — tile reset, player loses it
                self.grid[rabbit.x][rabbit.y] = Tile()

    # ─────────────────────────────────────────────────────────────────── #
    def render(self, now):
        self.screen.fill((40, 120, 40))                  # background

        # ─── Draw field tiles ───────────────────────────── #
        for gx in range(COLS):
            for gy in range(ROWS):
                left, top = gx * TILE, gy * TILE
                rect = pygame.Rect(left, top, TILE, TILE)
                pygame.draw.rect(self.screen, (80, 50, 20), rect)
                pygame.draw.rect(self.screen, (30, 30, 30), rect, 1)  # grid lines

                tile = self.grid[gx][gy]
                if tile.crop:
                    # choose surface
                    if tile.stage == 3:
                        base = self.crop_img_stage3[tile.crop]
                        alpha = int(128 + 127 * math.sin(now * 4 + gx + gy))
                        img = base.copy()
                        img.set_alpha(alpha)
                    else:
                        img = self.crop_img[(tile.crop, tile.stage)]

                    img_rect = img.get_rect(center=rect.center)
                    self.screen.blit(img, img_rect)

                # flash on planting
                if tile.flash_to > now:
                    flash_alpha = int(255 * (tile.flash_to - now) / 0.3)
                    flash_surf = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
                    flash_surf.fill((255, 255, 0, flash_alpha))
                    self.screen.blit(flash_surf, (left, top))

                # sparkle if fertilized
                if tile.fertilized:
                    sparkle_phase = (now - tile.sparkle_t) * 4
                    if sparkle_phase % 1 < 0.5:        # blink
                        spark_rect = self.sparkle.get_rect(center=(left + TILE - 12, top + 12))
                        self.screen.blit(self.sparkle, spark_rect)

        # ─── Draw rabbits ──────────────────────────────── #
        for rabbit in self.rabbits:
            r_rect = self.rabbit_img.get_rect(center=(rabbit.x * TILE + TILE // 2,
                                                      rabbit.y * TILE + TILE // 2))
            self.screen.blit(self.rabbit_img, r_rect)

        # ─── Draw tractor ─────────────────────────── #
        tractor_rect = self.tractor_img.get_rect(center=(self.x * TILE + TILE // 2,
                                                         self.y * TILE + TILE // 2))
        self.screen.blit(self.tractor_img, tractor_rect)

        # ─── Sidebar  ─────────────────────────────── #
        sb_left = FIELD_W
        pygame.draw.rect(self.screen, (50, 60, 70), (sb_left, 0, SIDEBAR_W, WIN_H))
        pygame.draw.rect(self.screen, (20, 20, 20), (sb_left, 0, SIDEBAR_W, WIN_H), 2)

        # Current seed selection
        seed_title = self.sidebar_ui_font.render("Seeds", True, (255, 255, 255))
        self.screen.blit(seed_title, (sb_left + 10, SEED_TITLE_PAD_Y))

        for i, c in enumerate(CROPS):
            row_y = SEED_START_Y + i * SEED_ROW_H

            # Selection highlight rectangle
            if c == self.selected:
                highlight_rect = pygame.Rect(sb_left + 4, row_y - 4,
                                             SIDEBAR_W - 8, SEED_ROW_H - 4)
                pygame.draw.rect(self.screen, (220, 220, 70), highlight_rect, 0, border_radius=4)
                pygame.draw.rect(self.screen, (50, 50, 20), highlight_rect, 2, border_radius=4)

            # Row contents
            key_surf = self.sidebar_ui_font.render(c.key, True, (30, 30, 30) if c == self.selected else (200, 200, 200))
            emoji_surf = self.sidebar_emoji_font.render(c.emojis[3], True, (30, 30, 30) if c == self.selected else (255, 255, 255))
            cost_surf = self.small_font.render(f"{c.seed_cost} 💰", True,
                                               (30, 30, 30) if c == self.selected else (180, 180, 180))

            self.screen.blit(key_surf, (sb_left + SEED_KEY_X_OFF, row_y))
            self.screen.blit(emoji_surf, (sb_left + SEED_EMOJI_X_OFF, row_y - 4))
            self.screen.blit(cost_surf, (sb_left + SEED_COST_X_OFF, row_y + 4))

        # Coin counter
        coin_text = self.ui_font.render(f"Coins: {self.coins} 💰", True, (255, 255, 255))
        self.screen.blit(coin_text, (sb_left + 10, SEED_START_Y + len(CROPS) * SEED_ROW_H))

        # Harvest totals
        harvest_title_y = SEED_START_Y + len(CROPS) * SEED_ROW_H + 30
        h_title = self.sidebar_ui_font.render("Harvested", True, (255, 255, 255))
        self.screen.blit(h_title, (sb_left + 10, harvest_title_y))

        for i, c in enumerate(CROPS):
            y = harvest_title_y + 30 + i * 20
            if y > WIN_H - 20:
                break
            self.screen.blit(self.sidebar_emoji_font.render(c.emojis[3], True, (255, 255, 255)),
                             (sb_left + 10, y - 4))
            count = self.small_font.render(f"x {self.harvest_log[c]}", True, (200, 200, 200))
            self.screen.blit(count, (sb_left + 45, y))

        # Help legend – placed dynamically below seed list (or above bottom)
        legend_lines = ["WASD: move",
                        "SPACE: plant/harvest",
                        "1‑6: pick seed",
                        "F: fertilizer (5💰)",
                        "ESC: quit"]

        legend_start_y = SEED_START_Y + len(CROPS) * SEED_ROW_H + LEGEND_EXTRA_PAD
        legend_height = len(legend_lines) * 20
        # Ensure it doesn't overlap harvest totals or go off screen
        legend_start_y = min(legend_start_y,
                             harvest_title_y - legend_height - 10)

        for i, line in enumerate(legend_lines):
            t = self.small_font.render(line, True, (180, 180, 180))
            self.screen.blit(t, (sb_left + 10, legend_start_y + i * 20))

        # ─── Flip! ─────────────────────────────── #
        pygame.display.flip()

# ────────────────────────────── MAIN ────────────────────────────── #
if __name__ == "__main__":
    # Ensure emoji glyphs render on Windows by locating emoji font file if needed
    if sys.platform == "win32":
        emoji_path = Path("seguiemj.ttf")
        if emoji_path.exists():
            pygame.font.Font(str(emoji_path), 12)
    TinyTractorTycoon().run()
