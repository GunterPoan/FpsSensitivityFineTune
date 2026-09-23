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

        self.screen = pygame.display.set_mode((1600, 900))
        pygame.display.set_caption("R6 Sensitivity Calibration")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 22)

        self.settings = R6Settings()
        self.model = SensitivityModel(self.settings)
        self.settings_screen = SettingsScreen(self.settings, self.font)
        self.experiment_screen = ExperimentScreen(self.model)

        # Screen management
        self.screens = {
            "settings": self.settings_screen,
            "experiment": self.experiment_screen,
        }
        self.current_screen_name = "experiment"
        self.current_screen = self.screens["experiment"]

        # Navigation button (top-right)
        self.nav_button_rect = pygame.Rect(790, 20, 80, 34)
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

    def _update(self):
        self.current_screen.update()
        self.model.update_settings()

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