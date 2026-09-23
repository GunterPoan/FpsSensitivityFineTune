import math
import random

import pygame

from ui.colors import BG_DARK, WHITE, TEXT_NORMAL, TEXT_DIM, PANEL_BORDER, PANEL_BG


class ExperimentScreen:
    """
    Flick test experiment screen.
    Shows a target, records mouse movement distance,
    and calculates overshoot/undershoot tendency.
    """

    def __init__(self, model):
        self.model = model
        self.font = pygame.font.SysFont("arial", 22)

        # Trial data
        self.trials = []
        self.current_trial = {
            "total_distance": 0.0,
            "mouse_positions": [],
        }
        self.in_progress = False

        # Visual: target angle and distance
        self.target_angle = 45
        self.target_distance = 200

        # Reset button (bottom-left)
        self.reset_font = pygame.font.SysFont("arial", 16)
        self.reset_button_rect = pygame.Rect(30, 365, 80, 30)

    def start_new_trial(self, screen_center):
        """Reset for a new flick attempt."""
        self.current_trial = {
            "total_distance": 0.0,
            "mouse_positions": [],
        }
        self.in_progress = True
        self.target_angle = random.choice([30, 45, 60, 90])

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.reset_button_rect.collidepoint(event.pos):
                self._reset_trials()
                return

        if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
            if self.in_progress:
                self._end_trial()
            else:
                self.start_new_trial((450, 260))

        elif event.type == pygame.MOUSEMOTION and self.in_progress:
            dx, dy = event.rel
            distance = (dx ** 2 + dy ** 2) ** 0.5
            self.current_trial["total_distance"] += distance
            self.current_trial["mouse_positions"].append((dx, dy))

    def _end_trial(self):
        """Complete current trial and store results."""
        self.in_progress = False

        predicted = self.model.predict_rotation(
            self.current_trial["total_distance"]
        )

        trial_data = {
            "target_angle": self.target_angle,
            "mouse_distance": self.current_trial["total_distance"],
            "predicted_angle": predicted,
            "error": predicted - self.target_angle,
        }
        self.trials.append(trial_data)

        print(f"Trial {len(self.trials)}: "
              f"target={trial_data['target_angle']:.0f}°, "
              f"predicted={trial_data['predicted_angle']:.1f}°, "
              f"error={trial_data['error']:+.1f}°")

    def _reset_trials(self):
        """Clear all trial data and reset state."""
        self.trials.clear()
        self.in_progress = False
        self.current_trial = {
            "total_distance": 0.0,
            "mouse_positions": [],
        }
        print("All trials reset.")

    def update(self) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BG_DARK)

        center_x = surface.get_width() // 2
        center_y = surface.get_height() // 2

        # Draw center crosshair
        pygame.draw.line(surface, WHITE, (center_x - 15, center_y),
                        (center_x + 15, center_y), 2)
        pygame.draw.line(surface, WHITE, (center_x, center_y - 15),
                        (center_x, center_y + 20), 2)

        # Calculate target position on circle
        angle_rad = math.radians(self.target_angle)
        tx = center_x + int(self.target_distance * math.cos(angle_rad))
        ty = center_y - int(self.target_distance * math.sin(angle_rad))

        # Draw target circle
        pygame.draw.circle(surface, (255, 80, 80), (tx, ty), 12)
        pygame.draw.circle(surface, WHITE, (tx, ty), 12, 2)

        # Draw line from center to target
        pygame.draw.line(surface, PANEL_BORDER, (center_x, center_y),
                        (tx, ty), 1)

        # Title
        title = self.font.render("Flick Test", True, WHITE)
        surface.blit(title, (30, 30))

        # Status
        if self.in_progress:
            status = "Move mouse toward target, press SPACE when ready"
        else:
            status = "Press SPACE to start new trial"
        status_surf = self.font.render(status, True, TEXT_NORMAL)
        surface.blit(status_surf, (30, 80))

        # Current trial info
        info_lines = [
            f"Target Angle: {self.target_angle}°",
            f"Mouse Moved: {self.current_trial['total_distance']:.1f} px",
            f"Current Gain: {self.model.get_gain():.4f}",
            f"Trials Completed: {len(self.trials)}",
        ]
        for i, line in enumerate(info_lines):
            surf = self.font.render(line, True, TEXT_DIM)
            surface.blit(surf, (30, 130 + i * 30))

        # Last trial result
        if self.trials:
            last = self.trials[-1]
            result_text = (f"Last: {last['predicted_angle']:.1f}° "
                          f"(error {last['error']:+.1f}°)")
            color = (80, 255, 80) if abs(last["error"]) < 5 else (255, 200, 80)
            result_surf = self.font.render(result_text, True, color)
            surface.blit(result_surf, (30, 280))

        # Average tendency
        if len(self.trials) >= 3:
            avg_error = sum(t["error"] for t in self.trials) / len(self.trials)
            if avg_error > 5:
                tendency = "Tendency: OVERSHOOT (reduce sens)"
            elif avg_error < -5:
                tendency = "Tendency: UNDERSHOOT (increase sens)"
            else:
                tendency = "Tendency: BALANCED"
            tend_surf = self.font.render(tendency, True, WHITE)
            surface.blit(tend_surf, (30, 320))

        # Reset button
        pygame.draw.rect(surface, PANEL_BG, self.reset_button_rect)
        pygame.draw.rect(surface, PANEL_BORDER, self.reset_button_rect, 2)
        reset_surf = self.reset_font.render("Reset", True, TEXT_DIM)
        reset_rect = reset_surf.get_rect(center=self.reset_button_rect.center)
        surface.blit(reset_surf, reset_rect)