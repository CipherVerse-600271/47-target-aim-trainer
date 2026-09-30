import pygame
import random
import math
import struct

from .target import Target


WHITE = (255, 255, 255)
RED = (220, 60, 60)


def create_tone(frequency, duration, volume=0.3):
    """
    Create a simple sound effect directly in memory.

    No external audio files are required.
    """

    mixer_settings = pygame.mixer.get_init()

    if mixer_settings is None:
        pygame.mixer.init()
        mixer_settings = pygame.mixer.get_init()

    sample_rate, sample_format, channels = mixer_settings

    # We generate 16-bit signed samples.
    if sample_format not in (-16, 16):
        sample_format = -16

    sample_count = int(sample_rate * duration)

    samples = bytearray()

    for i in range(sample_count):
        value = int(
            volume
            * 32767
            * math.sin(
                2 * math.pi * frequency * i / sample_rate
            )
        )

        packed_sample = struct.pack("<h", value)

        # Match the number of mixer channels.
        for _ in range(channels):
            samples.extend(packed_sample)

    return pygame.mixer.Sound(buffer=bytes(samples))


class GameEngine:

    def __init__(self, width, height):

        self.width = width
        self.height = height

        self.margin = 60
        self.hud_height = 60

        # ==================================================
        # TASK 3: DIFFICULTY SETTINGS
        # ==================================================

        self.difficulty = "Medium"

        self.difficulty_settings = {
            "Easy": {
                "lifespan_frames": 120,
                "base_radius": 40,
                "min_radius": 12
            },

            "Medium": {
                "lifespan_frames": 90,
                "base_radius": 40,
                "min_radius": 12
            },

            "Hard": {
                "lifespan_frames": 60,
                "base_radius": 40,
                "min_radius": 12
            }
        }

        # ==================================================
        # ROUND STATE
        # ==================================================

        self.round_seconds = 30
        self.time_left_frames = self.round_seconds * 60

        self.hits = 0
        self.misses = 0
        self.score = 0

        self.game_over = False

        # ==================================================
        # FONTS
        # ==================================================

        self.font = pygame.font.SysFont(
            "Arial",
            26
        )

        self.game_over_font = pygame.font.SysFont(
            "Arial",
            48
        )

        # ==================================================
        # TASK 4: SOUND EFFECTS
        # ==================================================

        # Initialize mixer if it has not already been initialized.
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        # Successful hit
        self.hit_sound = create_tone(
            900,
            0.08,
            0.30
        )

        # Player clicks outside the target
        self.miss_sound = create_tone(
            300,
            0.10,
            0.25
        )

        # Target expires
        self.timeout_sound = create_tone(
            180,
            0.15,
            0.25
        )

        # Round ends
        self.game_over_sound = create_tone(
            120,
            0.40,
            0.30
        )

        # ==================================================
        # CREATE FIRST TARGET
        # ==================================================

        self.target = self._spawn_target()

    # ======================================================
    # TARGET SPAWNING
    # ======================================================

    def _spawn_target(self):

        x = random.randint(
            self.margin,
            self.width - self.margin
        )

        y = random.randint(
            self.margin + self.hud_height,
            self.height - self.margin
        )

        settings = self.difficulty_settings[
            self.difficulty
        ]

        return Target(
            x,
            y,
            base_radius=settings["base_radius"],
            min_radius=settings["min_radius"],
            lifespan_frames=settings["lifespan_frames"]
        )

    # ======================================================
    # TASK 3: START NEW ROUND
    # ======================================================

    def start_new_round(self, difficulty):

        self.difficulty = difficulty

        # Reset score and statistics
        self.hits = 0
        self.misses = 0
        self.score = 0

        # Reset 30-second timer
        self.round_seconds = 30
        self.time_left_frames = self.round_seconds * 60

        # Exit Game Over state
        self.game_over = False

        # Spawn a fresh target
        self.target = self._spawn_target()

    # ======================================================
    # EVENT HANDLING
    # ======================================================

    def handle_event(self, event):

        # --------------------------------------------------
        # TASK 3:
        # Handle keyboard input on Game Over screen
        # --------------------------------------------------

        if event.type == pygame.KEYDOWN and self.game_over:

            # Easy
            if event.key == pygame.K_e:
                self.start_new_round("Easy")

            # Medium
            elif event.key == pygame.K_m:
                self.start_new_round("Medium")

            # Hard
            elif event.key == pygame.K_h:
                self.start_new_round("Hard")

            # Exit
            elif event.key == pygame.K_q:
                pygame.quit()
                raise SystemExit

            return

        # --------------------------------------------------
        # Ignore normal gameplay input during Game Over
        # --------------------------------------------------

        if self.game_over:
            return

        # --------------------------------------------------
        # NORMAL MOUSE GAMEPLAY
        # --------------------------------------------------

        if event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_click(event.pos)

    # ======================================================
    # CLICK HANDLING
    # ======================================================

    def _handle_click(self, pos):

        x, y = pos

        # ==================================================
        # TASK 1:
        # Collision uses visual_radius()
        # ==================================================

        if self.target.contains_point(x, y):

            # Existing scoring logic
            self.hits += 1
            self.score += 1

            # ==================================================
            # TASK 4: SUCCESSFUL HIT SOUND
            # ==================================================

            self.hit_sound.play()

            # Spawn next target
            self.target = self._spawn_target()

        else:

            # Existing miss logic
            self.misses += 1

            # ==================================================
            # TASK 4: NORMAL MISS SOUND
            # ==================================================

            self.miss_sound.play()

    # ======================================================
    # KEYBOARD INPUT
    # ======================================================

    def handle_input(self):

        # The game is mouse-driven.
        # Keyboard input is handled through handle_event().
        pass

    # ======================================================
    # GAME UPDATE
    # ======================================================

    def update(self):

        # Do nothing after Game Over
        if self.game_over:
            return

        # ==================================================
        # TIMER
        # ==================================================

        self.time_left_frames -= 1

        # ==================================================
        # GAME OVER CONDITION
        # ==================================================

        if self.time_left_frames <= 0:

            self.game_over = True

            # ==================================================
            # TASK 4: GAME OVER SOUND
            # ==================================================

            self.game_over_sound.play()

            return

        # ==================================================
        # UPDATE TARGET SHRINKING
        # ==================================================

        self.target.update()

        # ==================================================
        # TARGET TIMEOUT
        # ==================================================

        if self.target.expired():

            # Existing behavior:
            # expired target counts as a miss
            self.misses += 1

            # ==================================================
            # TASK 4: TIMEOUT SOUND
            # ==================================================

            self.timeout_sound.play()

            # Spawn another target
            self.target = self._spawn_target()

    # ======================================================
    # ACCURACY
    # ======================================================

    def accuracy(self):

        total = self.hits + self.misses

        if total == 0:
            return 0.0

        return round(
            100 * self.hits / total,
            1
        )

    # ======================================================
    # RENDERING
    # ======================================================

    def render(self, screen):

        # ==================================================
        # TASK 2 + TASK 3:
        # GAME OVER SCREEN
        # ==================================================

        if self.game_over:

            game_over_text = self.game_over_font.render(
                "GAME OVER",
                True,
                WHITE
            )

            score_text = self.font.render(
                f"Final Score: {self.score}",
                True,
                WHITE
            )

            accuracy_text = self.font.render(
                f"Final Accuracy: {self.accuracy()}%",
                True,
                WHITE
            )

            difficulty_text = self.font.render(
                "Choose Difficulty",
                True,
                WHITE
            )

            easy_text = self.font.render(
                "[E] Easy",
                True,
                WHITE
            )

            medium_text = self.font.render(
                "[M] Medium",
                True,
                WHITE
            )

            hard_text = self.font.render(
                "[H] Hard",
                True,
                WHITE
            )

            quit_text = self.font.render(
                "[Q] Exit",
                True,
                WHITE
            )

            # --------------------------------------------------
            # GAME OVER HEADING
            # --------------------------------------------------

            screen.blit(
                game_over_text,
                (
                    self.width // 2
                    - game_over_text.get_width() // 2,
                    80
                )
            )

            # --------------------------------------------------
            # FINAL SCORE
            # --------------------------------------------------

            screen.blit(
                score_text,
                (
                    self.width // 2
                    - score_text.get_width() // 2,
                    160
                )
            )

            # --------------------------------------------------
            # FINAL ACCURACY
            # --------------------------------------------------

            screen.blit(
                accuracy_text,
                (
                    self.width // 2
                    - accuracy_text.get_width() // 2,
                    205
                )
            )

            # --------------------------------------------------
            # DIFFICULTY HEADING
            # --------------------------------------------------

            screen.blit(
                difficulty_text,
                (
                    self.width // 2
                    - difficulty_text.get_width() // 2,
                    275
                )
            )

            # --------------------------------------------------
            # EASY
            # --------------------------------------------------

            screen.blit(
                easy_text,
                (
                    self.width // 2
                    - easy_text.get_width() // 2,
                    315
                )
            )

            # --------------------------------------------------
            # MEDIUM
            # --------------------------------------------------

            screen.blit(
                medium_text,
                (
                    self.width // 2
                    - medium_text.get_width() // 2,
                    350
                )
            )

            # --------------------------------------------------
            # HARD
            # --------------------------------------------------

            screen.blit(
                hard_text,
                (
                    self.width // 2
                    - hard_text.get_width() // 2,
                    385
                )
            )

            # --------------------------------------------------
            # EXIT
            # --------------------------------------------------

            screen.blit(
                quit_text,
                (
                    self.width // 2
                    - quit_text.get_width() // 2,
                    420
                )
            )

            # Do not draw target/HUD
            return

        # ==================================================
        # NORMAL GAMEPLAY
        # ==================================================

        # Task 1:
        # Draw target using the same visual radius used
        # by collision detection.

        r = int(
            self.target.visual_radius()
        )

        # --------------------------------------------------
        # TARGET
        # --------------------------------------------------

        pygame.draw.circle(
            screen,
            RED,
            (
                self.target.x,
                self.target.y
            ),
            r
        )

        # --------------------------------------------------
        # TARGET OUTLINE
        # --------------------------------------------------

        pygame.draw.circle(
            screen,
            WHITE,
            (
                self.target.x,
                self.target.y
            ),
            r,
            2
        )

        # ==================================================
        # SCORE
        # ==================================================

        score_text = self.font.render(
            f"Score: {self.score}",
            True,
            WHITE
        )

        screen.blit(
            score_text,
            (10, 10)
        )

        # ==================================================
        # TIMER
        # ==================================================

        seconds_left = max(
            0,
            self.time_left_frames // 60
        )

        timer_text = self.font.render(
            f"Time: {seconds_left}s",
            True,
            WHITE
        )

        screen.blit(
            timer_text,
            (
                self.width - 140,
                10
            )
        )

        # ==================================================
        # ACCURACY
        # ==================================================

        accuracy_text = self.font.render(
            f"Accuracy: {self.accuracy()}%",
            True,
            WHITE
        )

        screen.blit(
            accuracy_text,
            (
                self.width // 2 - 90,
                10
            )
        )