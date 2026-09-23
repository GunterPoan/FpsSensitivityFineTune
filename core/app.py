import pygame

from models.settings import R6Settings
from ui.settings_screen import SettingsScreen
from ui.experiment_screen import ExperimentScreen
from ui.colors import PANEL_BG, PANEL_BORDER, WHITE

class SensitivityModel:
    """
    Simplified mouse movement → rotation angle relationship.
    NOT the exact R6 physics engine. This is a RELATIVE linear model
    that can be experimentally calibrated later.
    """

    def __init__(self, settings: R6Settings):
        self.settings = settings
        self._gain = 0.0
        self.update_settings()

    def update_settings(self) -> None:
        """
        Recompute gain from current settings.
        Call this whenever settings change.
        """
        dpi_norm = self.settings.dpi / 800.0
        sens = self.settings.horizontalSens
        xf = self.settings.xfactorAiming
        # Arbitrary scaling for usable degree values
        self._gain = dpi_norm * sens * xf * 100.0

    def predict_rotation(self, mouse_pixels: float) -> float:
        """
        Predict rotation angle (degrees) for a given mouse movement.
        LINEAR APPROXIMATION.
        """
        return mouse_pixels * self._gain * 0.1

    def get_gain(self) -> float:
        """Return current gain factor."""
        return self._gain


class Application:
    """
    Top-level Pygame application.
    """

    def __init__(self):
        pygame.init()

        pygame.display.set_caption("R6 Sensitivity Calibration")

        self.settings = R6Settings()
        self.model = SensitivityModel(self.settings)

        # Window sizing: compute initial size from aspect ratio
        desktop_info = pygame.display.Info()
        self.desktop_w = desktop_info.current_w or 1920
        self.desktop_h = desktop_info.current_h or 1080
        self.window_w, self.window_h = self._calc_window_size(
            self.settings.aspectRatio
        )
        self.screen = pygame.display.set_mode((self.window_w, self.window_h))

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 22)
        
        self.settings_screen = SettingsScreen(
            self.settings, self.font, self.window_w, self.window_h
        )
        self.experiment_screen = ExperimentScreen(self.model)

        # Screen management
        self.screens = {
            "settings": self.settings_screen,
            "experiment": self.experiment_screen,
        }
        self.current_screen_name = "experiment"
        self.current_screen = self.screens["experiment"]


        # Aspect ratio change detection
        self._previous_aspect_ratio = self.settings.aspectRatio

        # Navigation button (top-right, dynamically positioned)
        nav_w, nav_h = 80, 34
        self.nav_button_rect = pygame.Rect(
            self.window_w - nav_w - 20, 20, nav_w, nav_h
        )
        self.nav_font = pygame.font.SysFont("arial", 18)

        self.running = False

    def run(self):
        self.running = True

        while self.running:
            self._process_events()
            self._update()
            self._draw()
            self.clock.tick(60)

        pygame.quit()

    def _process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                # Check nav button first
                if self.nav_button_rect.collidepoint(event.pos):
                    self._toggle_screen()
                else:
                    self.current_screen.handle_event(event)
            else:
                self.current_screen.handle_event(event)
    
    def _toggle_screen(self):
        if self.current_screen_name == "settings":
            self.current_screen_name = "experiment"
            self.experiment_screen.start_new_trial(
                (self.screen.get_width() // 2, self.screen.get_height() // 2)
            )
        else:
            self.current_screen_name = "settings"
        self.current_screen = self.screens[self.current_screen_name]

    def _calc_window_size(self, aspect_str: str):
        """
        Compute window size based on aspect ratio.
        Window fills ~85% of screen width or height, whichever limits first.
        Minimum size: 640x400.
        """
        screen_w = self.desktop_w
        screen_h = self.desktop_h

        # Parse aspect ratio
        if aspect_str == "16:9":
            ratio = 16.0 / 9.0
        elif aspect_str == "4:3":
            ratio = 4.0 / 3.0
        else:
            ratio = 16.0 / 9.0

        # Try 85% of screen width
        w = int(screen_w * 0.85)
        h = int(w / ratio)

        # If height exceeds 85% of screen, constrain by height instead
        max_h = int(screen_h * 0.85)
        if h > max_h:
            h = max_h
            w = int(h * ratio)

        return max(w, 640), max(h, 400)

    def _resize_window(self, aspect_str: str):
        """Resize window to match new aspect ratio and update dependent rects."""
        self.window_w, self.window_h = self._calc_window_size(aspect_str)
        self.screen = pygame.display.set_mode((self.window_w, self.window_h))

        # Reposition nav button to top-right corner
        self.nav_button_rect.x = self.window_w - self.nav_button_rect.width - 20

        # Resize settings screen layout
        self.settings_screen.resize(self.window_w, self.window_h)

    def _update(self):
        self.current_screen.update()
        self.model.update_settings()

        # Detect aspect ratio change → resize window
        current_aspect = self.settings.aspectRatio
        if current_aspect != self._previous_aspect_ratio:
            self._resize_window(current_aspect)
            self._previous_aspect_ratio = current_aspect

    def _draw(self):
        self.current_screen.draw(self.screen)

        # Draw navigation button on top of everything
        nav_text = "Experiment" if self.current_screen_name == "settings" else "Settings"
        nav_surf = self.nav_font.render(nav_text, True, WHITE)
        pygame.draw.rect(self.screen, PANEL_BG, self.nav_button_rect)
        pygame.draw.rect(self.screen, PANEL_BORDER, self.nav_button_rect, 2)
        text_rect = nav_surf.get_rect(center=self.nav_button_rect.center)
        self.screen.blit(nav_surf, text_rect)

        pygame.display.flip()