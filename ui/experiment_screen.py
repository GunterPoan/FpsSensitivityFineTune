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

        # Window size
        self.win_w = 900
        self.win_h = 520


        # Trial data
        self.trials = []
        self.current_trial = {
            "total_distance": 0.0,
            "mouse_positions": [],
            "net_dx": 0.0, 
            "net_dy": 0.0
        }
        self.in_progress = False

        # Visual: target angle and distance
        self.target_distance = 200
        self.TARGET_RADIUS = 6
        self.target_visual_angle = 45

        # Logical: desired rotation in degrees (the actual task)
        self.target_rotation_deg = 45
        
        self.MIN_TRIALS_FOR_ANALYSIS = 3
        self.MIN_IDEAL_DELTA = 5

        # Reset button (bottom-left)
        self.reset_font = pygame.font.SysFont("arial", 16)
        self.reset_button_rect = pygame.Rect(0, 0, 80, 30)
        

    def start_new_trial(self):
        """Reset for a new flick attempt."""
        self.current_trial = {
            "total_distance": 0.0,
            "mouse_positions": [],
            "net_dx": 0.0,
            "net_dy": 0.0,
        }
        self.in_progress = True
        
        # Random visual distance (120 ~ 360 pixels from center)
        max_dist_x = self.win_w // 2 - 20
        max_dist_y = self.win_h // 2 - 20
        max_dist = min(max_dist_x, max_dist_y, 360)
        self.target_distance = random.randint(120, max(120, max_dist))
        
        # Random visual direction (0° = right, 90° = up, 180° = left)
        self.target_visual_angle = random.choice(
            [0, 30, 45, 60, 90, 120, 135, 150, 180,
            210, 225, 240, 270, 300, 315, 330]
        )
        
        # Random rotation demand (15 ~ 90 degrees)
        self.target_rotation_deg = random.choice([15, 30, 45, 60, 75, 90])

        angle_rad = math.radians(self.target_visual_angle)
        self.ideal_dx = self.target_distance * math.cos(angle_rad)
        self.ideal_dy = -self.target_distance * math.sin(angle_rad)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.reset_button_rect.collidepoint(event.pos):
                self._reset_trials()
                return

        if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
            if self.in_progress:
                self._end_trial()
            else:
                self.start_new_trial()

        elif event.type == pygame.MOUSEMOTION and self.in_progress:
            dx, dy = event.rel
            distance = (dx ** 2 + dy ** 2) ** 0.5
            self.current_trial["total_distance"] += distance
            self.current_trial["mouse_positions"].append((dx, dy))
            self.current_trial["net_dx"] += dx
            self.current_trial["net_dy"] += dy

    def _end_trial(self):
        """Complete current trial and store results."""
        self.in_progress = False

        # Actual offset
        actual_dx = self.current_trial["net_dx"]
        actual_dy = self.current_trial["net_dy"]

        # Ideal offset
        ideal_dx = self.ideal_dx
        ideal_dy = self.ideal_dy

        # ratio = Actual / Ideal
        h_ratio = abs(actual_dx) / abs(ideal_dx) if abs(ideal_dx) > self.MIN_IDEAL_DELTA else 0
        v_ratio = abs(actual_dy) / abs(ideal_dy) if abs(ideal_dy) > self.MIN_IDEAL_DELTA else 0

        trial_data = {
            "target_rotation": self.target_rotation_deg,
            "mouse_total": self.current_trial["total_distance"],
            "net_dx": actual_dx,
            "net_dy": actual_dy,
            "ideal_dx": ideal_dx,
            "ideal_dy": ideal_dy,
            "h_ratio": h_ratio,
            "v_ratio": v_ratio,
        }
        self.trials.append(trial_data)

        print(f"Trial {len(self.trials)}: H_ratio={h_ratio:.2f}, V_ratio={v_ratio:.2f}")

    def _reset_trials(self):
        """Clear all trial data and reset state."""
        self.trials.clear()
        self.in_progress = False
        self.current_trial = {
            "total_distance": 0.0,
            "mouse_positions": [],
            "net_dx": 0.0,
            "net_dy": 0.0,
        }
        print("All trials reset.")

    def _analyze_trials(self):
        """
        Analyze completed trials and return sensitivity adjustment suggestions.
        Uses overshoot ratio instead of degrees.
        """
        if len(self.trials) < self.MIN_TRIALS_FOR_ANALYSIS:
            return None

        # Current sensitivities
        settings = self.model.settings
        sens_h = settings.horizontalSens
        sens_v = settings.verticalSens

        # --- Horizontal ---
        h_ratios = [t["h_ratio"] for t in self.trials if t["h_ratio"] > 0]
        avg_h_ratio = sum(h_ratios) / len(h_ratios) if h_ratios else 0
        has_h_data = len(h_ratios) > 0

        rec_h = None
        if has_h_data and avg_h_ratio > 0.01:
            rec_h = int(round(sens_h / avg_h_ratio))
            rec_h = max(1, min(100, rec_h))

        # --- Vertical ---
        v_ratios = [t["v_ratio"] for t in self.trials if t["v_ratio"] > 0]
        avg_v_ratio = sum(v_ratios) / len(v_ratios) if v_ratios else 0
        has_v_data = len(v_ratios) > 0

        rec_v = None
        if has_v_data and avg_v_ratio > 0.01:
            rec_v = int(round(sens_v / avg_v_ratio))
            rec_v = max(1, min(100, rec_v))

        # Threshold
        threshold = self.model.settings.threshold / 100.0
        ratio_lower = 1 - threshold
        ratio_upper = 1 + threshold

        h_ok = ratio_lower <= avg_h_ratio <= ratio_upper
        v_ok = ratio_lower <= avg_v_ratio <= ratio_upper
        needs_adjust = not (h_ok and v_ok)

        return {
            "h_ratio": avg_h_ratio,
            "v_ratio": avg_v_ratio,
            "rec_h": rec_h,
            "rec_v": rec_v,
            "has_h_data": has_h_data,
            "has_v_data": has_v_data,
            "needs_adjust": needs_adjust,
        }

    def update(self):
        pass

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BG_DARK)

        self.win_w = surface.get_width()
        self.win_h = surface.get_height()

        # Dynamically position reset button at bottom-left
        self.reset_button_rect.x = int(surface.get_width() * 0.033)
        self.reset_button_rect.y = int(surface.get_height() * 0.808)

        center_x = surface.get_width() // 2
        center_y = surface.get_height() // 2

        # Draw center crosshair
        pygame.draw.line(surface, WHITE, (center_x - 15, center_y),
                        (center_x + 15, center_y), 2)
        pygame.draw.line(surface, WHITE, (center_x, center_y - 15),
                        (center_x, center_y + 20), 2)

        # Calculate target position on circle
        angle_rad = math.radians(self.target_visual_angle)
        tx = center_x + int(self.target_distance * math.cos(angle_rad))
        ty = center_y - int(self.target_distance * math.sin(angle_rad))

        # Draw target circle
        pygame.draw.circle(surface, (255, 80, 80), (tx, ty), self.TARGET_RADIUS)
        pygame.draw.circle(surface, WHITE, (tx, ty), self.TARGET_RADIUS, 2)

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
            f"Target: {self.target_rotation_deg}",
            f"Visual: {self.target_visual_angle}°",
            f"Mouse: {self.current_trial['total_distance']:.1f} px",
        ]

        gain_h, gain_v = self.model.get_gain()
        info_lines.append(f"Gain  H:{gain_h:.3f} V:{gain_v:.3f}")
        info_lines.append(f"Trials: {len(self.trials)}")
        
        for i, line in enumerate(info_lines):
            surf = self.font.render(line, True, TEXT_DIM)
            surface.blit(surf, (30, 130 + i * 28))

        y_offset = 280
        threshold = self.model.settings.threshold / 100.0
        ratio_lower = 1 - threshold
        ratio_upper = 1 + threshold
        
        # Last trial result
        if self.trials:
            last = self.trials[-1]
            h_ratio = last["h_ratio"]
            v_ratio = last["v_ratio"]
            result_text = (f"Last  H:{h_ratio:.2f}x V:{v_ratio:.2f}x")
        
            err_ok = (ratio_lower <= h_ratio <= ratio_upper
                      and ratio_lower <= v_ratio <= ratio_upper)

            color = (80, 255, 80) if err_ok else (255, 200, 80)
            result_surf = self.font.render(result_text, True, color)
            surface.blit(result_surf, (30, y_offset))

        # Analysis & Suggestion
        analysis = self._analyze_trials()
        if analysis:
            y_offset += 35
            rec_h = analysis["rec_h"]
            rec_v = analysis["rec_v"]
            
            # Tendency text using ratio
            def axis_text_ratio(axis_name, ratio, rec, has_data):
                if not has_data:
                    return f"{axis_name}: N/A"
                if ratio > ratio_upper:
                    return f"{axis_name}: {ratio:.2f}x OVERSHOOT → {rec}"
                elif ratio < ratio_lower:
                    return f"{axis_name}: {ratio:.2f}x UNDERSHOOT → {rec}"
                else:
                    return f"{axis_name}: {ratio:.2f}x OK"

            h_text = axis_text_ratio("H", analysis["h_ratio"], rec_h, analysis["has_h_data"])
            v_text = axis_text_ratio("V", analysis["v_ratio"], rec_v, analysis["has_v_data"])
                    
            if analysis["needs_adjust"]:
                full_tend = f"{h_text} | {v_text}"
                color = (255, 200, 80)
            else:
                full_tend = "Both axes within threshold. No adjustment needed."
                color = (80, 255, 80)
            
            tend_surf = self.font.render(full_tend, True, color)
            surface.blit(tend_surf, (30, y_offset))

        # Reset button
        pygame.draw.rect(surface, PANEL_BG, self.reset_button_rect)
        pygame.draw.rect(surface, PANEL_BORDER, self.reset_button_rect, 2)
        reset_surf = self.reset_font.render("Reset", True, TEXT_DIM)
        reset_rect = reset_surf.get_rect(center=self.reset_button_rect.center)
        surface.blit(reset_surf, reset_rect)
