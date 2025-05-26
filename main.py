import pygame
import random
import os
import time

# Initialize Pygame
pygame.init()

# Get the screen info
screen_info = pygame.display.Info()
WINDOW_WIDTH = screen_info.current_w
WINDOW_HEIGHT = screen_info.current_h

# Calculate card size based on screen size
CARD_WIDTH = int(WINDOW_WIDTH * 0.1)  # 10% of screen width
CARD_HEIGHT = int(CARD_WIDTH * 1.5)   # 3:2 aspect ratio
CARD_MARGIN = int(CARD_WIDTH * 0.1)   # 10% of card width
ROWS = 4
COLS = 8  # 4x8 grid for 32 unique cards
ANIMATION_SPEED = int(CARD_WIDTH * 0.05)  # 5% of card width per frame
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)

# Load card images
def load_card_images():
    # Create card back
    card_back = pygame.Surface((CARD_WIDTH, CARD_HEIGHT), pygame.SRCALPHA)
    card_back.fill((0, 0, 0, 0))
    # Draw subtle shadow
    shadow_offset = int(CARD_WIDTH * 0.04)
    pygame.draw.rect(card_back, (60, 60, 120, 60), (shadow_offset, shadow_offset, CARD_WIDTH - shadow_offset, CARD_HEIGHT - shadow_offset), border_radius=int(CARD_WIDTH*0.13))
    # Draw elegant blue back
    pygame.draw.rect(card_back, (70, 120, 200), (0, 0, CARD_WIDTH, CARD_HEIGHT), border_radius=int(CARD_WIDTH*0.13))
    pygame.draw.rect(card_back, (30, 30, 150), (0, 0, CARD_WIDTH, CARD_HEIGHT), 3, border_radius=int(CARD_WIDTH*0.13))
    # Remove grid pattern for a cleaner look

    # Create realistic playing card faces (A, 2, 3, 4, 5, 6, 7, 8 of all suits)
    card_faces = []
    ranks = ['A', '2', '3', '4', '5', '6', '7', '8']
    suits = [
        {'symbol': '\u2665', 'color': (200, 0, 0)},  # Hearts (♥, red)
        {'symbol': '\u2666', 'color': (200, 0, 0)},  # Diamonds (♦, red)
        {'symbol': '\u2663', 'color': (0, 0, 0)},    # Clubs (♣, black)
        {'symbol': '\u2660', 'color': (0, 0, 0)},    # Spades (♠, black)
    ]
    for suit in suits:
        for rank in ranks:
            face = pygame.Surface((CARD_WIDTH, CARD_HEIGHT), pygame.SRCALPHA)
            # Draw subtle shadow
            pygame.draw.rect(face, (60, 60, 120, 60), (shadow_offset, shadow_offset, CARD_WIDTH - shadow_offset, CARD_HEIGHT - shadow_offset), border_radius=int(CARD_WIDTH*0.13))
            # Draw white rounded rectangle for card
            pygame.draw.rect(face, WHITE, (0, 0, CARD_WIDTH, CARD_HEIGHT), border_radius=int(CARD_WIDTH*0.13))
            pygame.draw.rect(face, BLACK, (0, 0, CARD_WIDTH, CARD_HEIGHT), 2, border_radius=int(CARD_WIDTH*0.13))
            # Draw rank in top-left
            font = pygame.font.SysFont('arial', int(CARD_HEIGHT * 0.19), bold=True)
            text = font.render(rank, True, suit['color'])
            face.blit(text, (10, 6))
            # Draw small suit pip in top-left, close to rank
            corner_suit_font = pygame.font.SysFont('arial', int(CARD_HEIGHT * 0.13))
            corner_suit = corner_suit_font.render(suit['symbol'], True, suit['color'])
            face.blit(corner_suit, (12, 10 + text.get_height()))
            # Draw rank and small suit in bottom-right (rotated)
            text_rot = pygame.transform.rotate(text, 180)
            corner_suit_rot = pygame.transform.rotate(corner_suit, 180)
            face.blit(text_rot, (CARD_WIDTH - text.get_width() - 10, CARD_HEIGHT - text.get_height() - corner_suit.get_height() - 6))
            face.blit(corner_suit_rot, (CARD_WIDTH - corner_suit.get_width() - 12, CARD_HEIGHT - corner_suit.get_height() - 10))
            # Draw large suit in center for Ace
            center_font = pygame.font.SysFont('arial', int(CARD_HEIGHT * 0.55))
            center_suit = center_font.render(suit['symbol'], True, suit['color'])
            center_rect = center_suit.get_rect(center=(CARD_WIDTH//2, CARD_HEIGHT//2))
            if rank == 'A':
                face.blit(center_suit, center_rect)
            # Draw pips for number cards (2-8) in a realistic layout
            elif rank.isdigit():
                count = int(rank)
                pip_font = pygame.font.SysFont('arial', int(CARD_HEIGHT * 0.22))
                pip = pip_font.render(suit['symbol'], True, suit['color'])
                pip_w, pip_h = pip.get_size()
                pip_layouts = {
                    2: [(.5, .3), (.5, .7)],
                    3: [(.5, .26), (.5, .5), (.5, .74)],
                    4: [(.36, .34), (.64, .34), (.36, .66), (.64, .66)],
                    5: [(.36, .34), (.64, .34), (.5, .5), (.36, .66), (.64, .66)],
                    6: [(.36, .34), (.64, .34), (.36, .5), (.64, .5), (.36, .66), (.64, .66)],
                    7: [(.36, .34), (.64, .34), (.5, .42), (.36, .5), (.64, .5), (.36, .66), (.64, .66)],
                    8: [(.36, .34), (.64, .34), (.36, .5), (.64, .5), (.36, .66), (.64, .66), (.5, .42), (.5, .58)],
                }
                for pos in pip_layouts[count]:
                    x = int(CARD_WIDTH * pos[0]) - pip_w//2
                    y = int(CARD_HEIGHT * pos[1]) - pip_h//2
                    face.blit(pip, (x, y))
            card_faces.append(face)
    return card_back, card_faces

# Create the game window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Fruit Matching Game")

class Card:
    def __init__(self, x, y, value, card_back, card_face):
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self.value = value
        self.revealed = False
        self.matched = False
        self.flip_progress = 0  # 0: face down, 1: face up
        self.rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        self.card_back = card_back
        self.card_face = card_face

    def move_towards_target(self):
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        if abs(dx) > ANIMATION_SPEED:
            self.x += ANIMATION_SPEED * (1 if dx > 0 else -1)
        else:
            self.x = self.target_x
        if abs(dy) > ANIMATION_SPEED:
            self.y += ANIMATION_SPEED * (1 if dy > 0 else -1)
        else:
            self.y = self.target_y
        self.rect.x = self.x
        self.rect.y = self.y

    def update_flip(self):
        target_flip = 1 if self.revealed else 0
        diff = target_flip - self.flip_progress
        if abs(diff) > 0.1:
            self.flip_progress += 0.1 * (1 if diff > 0 else -1)
        else:
            self.flip_progress = target_flip

    def draw(self):
        self.move_towards_target()
        self.update_flip()
        
        # Calculate card width based on flip progress (simulate 3D rotation)
        scaled_width = abs(int(CARD_WIDTH * (0.2 + 0.8 * abs(1 - 2 * (self.flip_progress % 1)))))
        x_offset = (CARD_WIDTH - scaled_width) // 2
        
        if self.matched:
            # Draw matched cards with a slight transparency
            surface = self.card_face.copy()
            surface.set_alpha(128)
        else:
            # Determine which side of the card to show based on flip progress
            if self.flip_progress < 0.5:
                surface = self.card_back
            else:
                surface = self.card_face
        
        # Scale the surface to create flip animation
        scaled_surface = pygame.transform.scale(surface, (scaled_width, CARD_HEIGHT))
        screen.blit(scaled_surface, (self.x + x_offset, self.y))

def create_board():
    card_back, card_faces = load_card_images()
    cards = []
    num_pairs = (ROWS * COLS) // 2
    # Use as many unique cards as needed for pairs, cycling through card_faces if needed
    values = list(range(len(card_faces)))
    pair_values = (values * ((num_pairs + len(values) - 1) // len(values)))[:num_pairs]
    all_values = pair_values * 2  # two of each for pairs
    random.shuffle(all_values)
    # Calculate grid size and center offset
    grid_width = COLS * (CARD_WIDTH + CARD_MARGIN) - CARD_MARGIN
    grid_height = ROWS * (CARD_HEIGHT + CARD_MARGIN) - CARD_MARGIN
    offset_x = (WINDOW_WIDTH - grid_width) // 2
    offset_y = (WINDOW_HEIGHT - grid_height) // 2
    for row in range(ROWS):
        for col in range(COLS):
            x = offset_x + col * (CARD_WIDTH + CARD_MARGIN)
            y = offset_y + row * (CARD_HEIGHT + CARD_MARGIN)
            idx = row * COLS + col
            value = all_values[idx]
            card = Card(x, y, value, card_back, card_faces[value])
            cards.append(card)
    return cards

def draw_buttons(screen, paused):
    font = pygame.font.Font(None, 36)
    pause_text = "Resume" if paused else "Pause"
    pause_btn = font.render(pause_text, True, WHITE, (70, 130, 180))
    exit_btn = font.render("Exit", True, WHITE, (220, 20, 60))
    pause_rect = pause_btn.get_rect(topright=(WINDOW_WIDTH - 20, 20))
    exit_rect = exit_btn.get_rect(topright=(WINDOW_WIDTH - 20, 70))
    screen.blit(pause_btn, pause_rect)
    screen.blit(exit_btn, exit_rect)
    return pause_rect, exit_rect

def main():
    global CARD_WIDTH, CARD_HEIGHT, CARD_MARGIN, screen
    total_width = COLS * (CARD_WIDTH + CARD_MARGIN) - CARD_MARGIN
    total_height = ROWS * (CARD_HEIGHT + CARD_MARGIN) - CARD_MARGIN
    if total_width > WINDOW_WIDTH * 0.9 or total_height > WINDOW_HEIGHT * 0.9:
        scale = min(WINDOW_WIDTH * 0.9 / total_width, WINDOW_HEIGHT * 0.9 / total_height)
        CARD_WIDTH = int(CARD_WIDTH * scale)
        CARD_HEIGHT = int(CARD_HEIGHT * scale)
        CARD_MARGIN = int(CARD_MARGIN * scale)
    total_width = COLS * (CARD_WIDTH + CARD_MARGIN) - CARD_MARGIN
    total_height = ROWS * (CARD_HEIGHT + CARD_MARGIN) - CARD_MARGIN
    cards = create_board()
    running = True
    clock = pygame.time.Clock()
    fullscreen = False
    paused = False
    revealed_cards = []
    last_flip_time = 0
    flip_delay = 800  # milliseconds

    font_match = pygame.font.Font(None, 40)
    num_pairs = (ROWS * COLS) // 2

    # Timer setup
    start_ticks = pygame.time.get_ticks()
    timer_font = pygame.font.Font(None, 44)
    game_over = False
    paused_time = 0
    pause_start = None

    while running:
        if not paused and not game_over:
            # Timer logic
            if pause_start is not None:
                # Add paused duration to paused_time
                paused_time += pygame.time.get_ticks() - pause_start
                pause_start = None
            seconds_left = 60 - ((pygame.time.get_ticks() - start_ticks - paused_time) // 1000)
            if seconds_left <= 0:
                seconds_left = 0
                game_over = True
        elif paused and pause_start is None:
            pause_start = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if fullscreen:
                        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
                    else:
                        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
                    fullscreen = not fullscreen
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                pos = pygame.mouse.get_pos()
                pause_rect, exit_rect = draw_buttons(screen, paused)
                if pause_rect.collidepoint(pos):
                    paused = not paused
                elif exit_rect.collidepoint(pos):
                    running = False
                elif not paused and len(revealed_cards) < 2:
                    for card in cards:
                        if card.rect.collidepoint(pos) and not card.revealed and not card.matched:
                            card.revealed = True
                            revealed_cards.append(card)
                            if len(revealed_cards) == 2:
                                last_flip_time = pygame.time.get_ticks()
        # Pause logic
        if paused:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            font = pygame.font.Font(None, 74)
            text = font.render("Paused", True, WHITE)
            text_rect = text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
            screen.blit(text, text_rect)
            draw_buttons(screen, paused)
            pygame.display.flip()
            clock.tick(FPS)
            continue
        # Handle card matching logic
        if len(revealed_cards) == 2 and not game_over:
            now = pygame.time.get_ticks()
            if now - last_flip_time > flip_delay:
                c1, c2 = revealed_cards
                if c1.value == c2.value:
                    c1.matched = True
                    c2.matched = True
                else:
                    c1.revealed = False
                    c2.revealed = False
                revealed_cards = []
        # Draw the game
        screen.fill(WHITE)
        for card in cards:
            card.draw()
        pause_rect, exit_rect = draw_buttons(screen, paused)
        # Draw number of correct matches
        matches = sum(1 for c in cards if c.matched) // 2
        match_text = font_match.render(f"Matches: {matches} / {num_pairs}", True, (30, 30, 120))
        screen.blit(match_text, (30, 20))
        # Draw timer
        timer_text = timer_font.render(f"Time: {seconds_left:02d}s", True, (180, 30, 30))
        screen.blit(timer_text, (30, 60))
        pygame.display.flip()
        # Check for win condition
        if all(card.matched for card in cards) and not game_over:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.fill(WHITE)
            overlay.set_alpha(200)
            screen.blit(overlay, (0, 0))
            font = pygame.font.Font(None, 74)
            text = font.render("You Win!", True, BLACK)
            text_rect = text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
            bg_rect = text_rect.copy()
            bg_rect.inflate_ip(40, 40)
            pygame.draw.rect(screen, WHITE, bg_rect)
            pygame.draw.rect(screen, BLACK, bg_rect, 3)
            screen.blit(text, text_rect)
            font_small = pygame.font.Font(None, 36)
            exit_text = font_small.render("Press ESC to exit", True, BLACK)
            exit_rect = exit_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 50))
            screen.blit(exit_text, exit_rect)
            pygame.display.flip()
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        waiting = False
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            waiting = False
                            running = False
        # Game over screen
        if game_over:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(180)
            screen.blit(overlay, (0, 0))
            font = pygame.font.Font(None, 74)
            text = font.render("Game Over", True, (255, 0, 0))
            text_rect = text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
            screen.blit(text, text_rect)
            font_small = pygame.font.Font(None, 36)
            exit_text = font_small.render("Press ESC to exit", True, WHITE)
            exit_rect = exit_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 50))
            screen.blit(exit_text, exit_rect)
            pygame.display.flip()
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        waiting = False
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            waiting = False
                            running = False
        clock.tick(FPS)
    pygame.quit()

def get_grid_size():
    import tkinter as tk
    from tkinter import simpledialog, messagebox
    root = tk.Tk()
    root.withdraw()
    while True:
        try:
            rows = simpledialog.askinteger("Grid Size", "Enter number of rows:", minvalue=2, maxvalue=10)
            cols = simpledialog.askinteger("Grid Size", "Enter number of columns:", minvalue=2, maxvalue=16)
            if rows is None or cols is None:
                messagebox.showinfo("Info", "Game cancelled.")
                exit()
            if (rows * cols) % 2 != 0:
                messagebox.showerror("Error", "The total number of cards (rows x columns) must be even.")
            else:
                return rows, cols
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    ROWS, COLS = get_grid_size()
    main()
