import array
import math
import random
import pygame
from game.color_button import ColorButton


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        pad_size = 130
        gap = 24
        start_x = width // 2 - pad_size - (gap // 2)
        start_y = 150

        self.buttons = [
            ColorButton(0, pygame.Rect(start_x, start_y, pad_size, pad_size), (110, 20, 20), (255, 50, 50)),                      # Red
            ColorButton(1, pygame.Rect(start_x + pad_size + gap, start_y, pad_size, pad_size), (15, 60, 150), (40, 170, 255)),   # Blue
            ColorButton(2, pygame.Rect(start_x, start_y + pad_size + gap, pad_size, pad_size), (15, 100, 30), (50, 255, 90)),    # Green
            ColorButton(3, pygame.Rect(start_x + pad_size + gap, start_y + pad_size + gap, pad_size, pad_size), (140, 110, 10), (255, 235, 40)), # Yellow
        ]

        self.sequence = []
        self.player_input = []
        self.score = 0

        self.state = "WATCH"
        self.showing_step = 0
        self.step_start_time = 0
        self.base_flash_duration = 450
        self.base_pause_duration = 200
        self.min_flash_duration = 180
        self.min_pause_duration = 80
        self.flash_duration = self.base_flash_duration
        self.pause_duration = self.base_pause_duration
        self.is_flashing = False

        self.timer_base_duration = 3500
        self.timer_per_step = 900
        self.timer_min_duration = 3500
        self.timer_max_duration = 15000
        self.player_turn_start = 0
        self.player_turn_duration = 0
        self.player_turn_timer_active = False

        self.player_lit_button = None
        self.player_lit_start = 0
        self.player_flash_duration = 150
        self.sounds = {}
        self.sound_frequencies = {
            0: 261.63,
            1: 329.63,
            2: 392.00,
            3: 523.25,
        }
        self.audio_enabled = self.initialize_audio()

        self.font_title = pygame.font.SysFont(None, 40)
        self.font_medium = pygame.font.SysFont(None, 28)

        self.start_next_round()

    def start_next_round(self):
        new_color = random.randint(0, 3)

        self.sequence.append(new_color)
        round_number = len(self.sequence)
        self.flash_duration = max(
            self.min_flash_duration,
            self.base_flash_duration - (round_number - 1) * 25,
        )
        self.pause_duration = max(
            self.min_pause_duration,
            self.base_pause_duration - (round_number - 1) * 12,
        )

        self.player_input.clear()
        self.state = "WATCH"
        self.showing_step = 0
        self.step_start_time = pygame.time.get_ticks()
        self.is_flashing = True
        self.player_turn_timer_active = False
        self.buttons[self.sequence[0]].is_lit = True
        self.play_sound(self.sequence[0])

    def initialize_audio(self):
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
            for color_id, frequency in self.sound_frequencies.items():
                self.sounds[color_id] = self.create_tone(frequency)
        except pygame.error:
            self.sounds.clear()
            return False
        return True

    def create_tone(self, frequency):
        sample_rate = 44100
        sample_count = int(sample_rate * 0.12)
        samples = array.array("h")

        for index in range(sample_count):
            envelope = min(1.0, index / 200)
            envelope *= min(1.0, (sample_count - index) / 800)
            sample = math.sin(2 * math.pi * frequency * index / sample_rate)
            samples.append(int(14000 * envelope * sample))

        return pygame.mixer.Sound(buffer=samples.tobytes())

    def play_sound(self, color_id):
        sound = self.sounds.get(color_id)
        if sound is not None:
            sound.play()

    def calculate_player_turn_duration(self):
        duration = self.timer_base_duration + len(self.sequence) * self.timer_per_step
        return max(self.timer_min_duration, min(self.timer_max_duration, duration))

    def start_player_turn(self, now):
        self.state = "PLAYER_TURN"
        self.player_turn_start = now
        self.player_turn_duration = self.calculate_player_turn_duration()
        self.player_turn_timer_active = True

    def end_game(self):
        self.state = "GAME_OVER"
        self.player_turn_timer_active = False

    def update(self):
        now = pygame.time.get_ticks()

        if self.player_lit_button is not None:
            if now - self.player_lit_start >= self.player_flash_duration:
                self.player_lit_button.is_lit = False
                self.player_lit_button = None

        if self.state == "WATCH":
            current_btn_id = self.sequence[self.showing_step]

            if self.is_flashing:
                if now - self.step_start_time >= self.flash_duration:
                    self.buttons[current_btn_id].is_lit = False
                    self.is_flashing = False
                    self.step_start_time = now
            else:
                if now - self.step_start_time >= self.pause_duration:
                    self.showing_step += 1
                    if self.showing_step < len(self.sequence):
                        next_id = self.sequence[self.showing_step]
                        self.buttons[next_id].is_lit = True
                        self.play_sound(next_id)
                        self.is_flashing = True
                        self.step_start_time = now
                    else:
                        self.start_player_turn(now)
        elif self.state == "PLAYER_TURN" and self.player_turn_timer_active:
            if now - self.player_turn_start >= self.player_turn_duration:
                self.end_game()

    def handle_event(self, event):
        if self.state == "GAME_OVER":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()
            return

        if self.state == "PLAYER_TURN" and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            now = pygame.time.get_ticks()
            if self.player_turn_timer_active and now - self.player_turn_start >= self.player_turn_duration:
                self.end_game()
                return

            for btn in self.buttons:
                if btn.contains(event.pos):
                    btn.is_lit = True
                    self.player_lit_button = btn
                    self.player_lit_start = now
                    self.play_sound(btn.color_id)

                    self.register_player_click(btn.color_id)
                    break

    def register_player_click(self, color_id):
        self.player_input.append(color_id)
        current_idx = len(self.player_input) - 1

        if self.player_input[current_idx] != self.sequence[current_idx]:
            self.end_game()
            return

        if len(self.player_input) == len(self.sequence):
            self.score += 1
            self.player_turn_timer_active = False
            self.start_next_round()

    def reset(self):
        self.sequence.clear()
        self.player_input.clear()
        self.score = 0
        for btn in self.buttons:
            btn.is_lit = False
        self.player_lit_button = None
        self.player_turn_timer_active = False
        self.start_next_round()

    def render(self, screen):
        screen.fill((22, 24, 30))

        title_surf = self.font_title.render("Memory Pattern Arena", True, (245, 245, 245))
        screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 20))

        score_surf = self.font_medium.render(f"Score: {self.score}", True, (255, 220, 80))
        screen.blit(score_surf, (self.width // 2 - score_surf.get_width() // 2, 60))

        status_text = "Watch the pattern..." if self.state == "WATCH" else "Your turn: Click the pattern!"
        status_color = (190, 195, 205) if self.state == "WATCH" else (80, 240, 130)
        status_surf = self.font_medium.render(status_text, True, status_color)
        screen.blit(status_surf, (self.width // 2 - status_surf.get_width() // 2, 95))

        if self.state == "PLAYER_TURN" and self.player_turn_timer_active:
            elapsed = pygame.time.get_ticks() - self.player_turn_start
            remaining = max(0, self.player_turn_duration - elapsed)
            progress = remaining / self.player_turn_duration
            timer_rect = pygame.Rect(50, 125, self.width - 100, 14)
            pygame.draw.rect(screen, (65, 70, 80), timer_rect, border_radius=7)
            fill_rect = timer_rect.copy()
            fill_rect.width = int(timer_rect.width * progress)
            pygame.draw.rect(screen, (80, 220, 130), fill_rect, border_radius=7)

        for btn in self.buttons:
            btn.render(screen)

        if self.state == "GAME_OVER":
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))

            over_surf = self.font_title.render("WRONG PATTERN! GAME OVER", True, (240, 70, 70))
            screen.blit(over_surf, (self.width // 2 - over_surf.get_width() // 2, self.height // 2 - 40))

            final_score_surf = self.font_medium.render(f"Final Score: {self.score}", True, (255, 255, 255))
            screen.blit(final_score_surf, (self.width // 2 - final_score_surf.get_width() // 2, self.height // 2 + 10))

            restart_surf = self.font_medium.render("Press [R] to Play Again", True, (200, 200, 200))
            screen.blit(restart_surf, (self.width // 2 - restart_surf.get_width() // 2, self.height // 2 + 50))
