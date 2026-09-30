import pygame
import random
from .target import Target

# Game Engine

WHITE = (255, 255, 255)
RED = (220, 60, 60)


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.margin = 60
        self.hud_height = 60

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

        self.target = self._spawn_target()

        self.round_seconds = 30
        self.time_left_frames = self.round_seconds * 60

        self.hits = 0
        self.misses = 0
        self.score = 0

        self.font = pygame.font.SysFont("Arial", 26)
        self.game_over_font = pygame.font.SysFont("Arial", 48)

        self.game_over = False

    def _spawn_target(self):
        x = random.randint(
            self.margin,
            self.width - self.margin
        )

        y = random.randint(
            self.margin + self.hud_height,
            self.height - self.margin
        )

        settings = self.difficulty_settings[self.difficulty]

        return Target(
            x,
            y,
            base_radius=settings["base_radius"],
            min_radius=settings["min_radius"],
            lifespan_frames=settings["lifespan_frames"]
        )

    def start_new_round(self, difficulty):
        self.difficulty = difficulty

        self.hits = 0
        self.misses = 0
        self.score = 0

        self.round_seconds = 30
        self.time_left_frames = self.round_seconds * 60

        self.game_over = False

        self.target = self._spawn_target()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and self.game_over:
            if event.key == pygame.K_e:
                self.start_new_round("Easy")

            elif event.key == pygame.K_m:
                self.start_new_round("Medium")

            elif event.key == pygame.K_h:
                self.start_new_round("Hard")

            elif event.key == pygame.K_q:
                pygame.quit()
                raise SystemExit

            return

        if self.game_over:
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_click(event.pos)

    def _handle_click(self, pos):
        x, y = pos

        if self.target.contains_point(x, y):
            self.hits += 1
            self.score += 1
            self.target = self._spawn_target()
        else:
            self.misses += 1

    def handle_input(self):
        # Reserved for continuously-held-key input;
        # this game is entirely mouse-driven.
        pass

    def update(self):
        if self.game_over:
            return

        self.time_left_frames -= 1

        if self.time_left_frames <= 0:
            self.game_over = True
            return

        self.target.update()

        if self.target.expired():
            self.misses += 1
            self.target = self._spawn_target()

    def accuracy(self):
        total = self.hits + self.misses

        if total == 0:
            return 0.0

        return round(100 * self.hits / total, 1)

    def render(self, screen):
        if self.game_over:
            game_over_text = self.game_over_font.render(
                "GAME OVER", True, WHITE
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

            screen.blit(
                game_over_text,
                (
                    self.width // 2 -
                    game_over_text.get_width() // 2,
                    80
                )
            )

            screen.blit(
                score_text,
                (
                    self.width // 2 -
                    score_text.get_width() // 2,
                    160
                )
            )

            screen.blit(
                accuracy_text,
                (
                    self.width // 2 -
                    accuracy_text.get_width() // 2,
                    205
                )
            )

            screen.blit(
                difficulty_text,
                (
                    self.width // 2 -
                    difficulty_text.get_width() // 2,
                    275
                )
            )

            screen.blit(
                easy_text,
                (
                    self.width // 2 -
                    easy_text.get_width() // 2,
                    315
                )
            )

            screen.blit(
                medium_text,
                (
                    self.width // 2 -
                    medium_text.get_width() // 2,
                    350
                )
            )

            screen.blit(
                hard_text,
                (
                    self.width // 2 -
                    hard_text.get_width() // 2,
                    385
                )
            )

            screen.blit(
                quit_text,
                (
                    self.width // 2 -
                    quit_text.get_width() // 2,
                    420
                )
            )

            return

        r = int(self.target.visual_radius())

        pygame.draw.circle(
            screen,
            RED,
            (self.target.x, self.target.y),
            r
        )

        pygame.draw.circle(
            screen,
            WHITE,
            (self.target.x, self.target.y),
            r,
            2
        )

        score_text = self.font.render(
            f"Score: {self.score}",
            True,
            WHITE
        )

        screen.blit(
            score_text,
            (10, 10)
        )

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
            (self.width - 140, 10)
        )

        acc_text = self.font.render(
            f"Accuracy: {self.accuracy()}%",
            True,
            WHITE
        )

        screen.blit(
            acc_text,
            (
                self.width // 2 - 90,
                10
            )
        )