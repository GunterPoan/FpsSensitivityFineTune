import pygame

from models.settings import R6Settings
from ui.settings_screen import SettingsScreen


class Application:
    """
    Top-level Pygame application controller.
    Owns the window, the clock, the font, the settings model,
    and the active screen (currently just SettingsScreen).
    """

    def __init__(self):
        # --- Pygame initialization ---
        pygame.init()

        self.screen = pygame.display.set_mode((900, 700))
        pygame.display.set_caption("R6 Sensitivity Calibration")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 22)

        # --- Data model & UI screen ---
        self.settings = R6Settings()
        self.settings_screen = SettingsScreen(self.settings, self.font)

        self.running = False

    # -----------------------------------------------------------------------
    # Main loop
    # -----------------------------------------------------------------------
    def run(self):
        """
        Entry point. Starts the frame loop.
        Typical Pygame loop: process events → update state → draw frame.
        """
        self.running = True

        while self.running:
            self._process_events()
            self._update()
            self._draw()
            self.clock.tick(60)

        pygame.quit()

    # -----------------------------------------------------------------------
    # Three phases of every frame
    # -----------------------------------------------------------------------
    def _process_events(self):
        """
        Phase 1: Pump all pending Pygame events and route them.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            else:
                self.settings_screen.handle_event(event)

    def _update(self):
        """
        Phase 2: Update internal state (sync UI → model, animations, etc).
        """
        self.settings_screen.update()

    def _draw(self):
        """
        Phase 3: Render the current frame onto the screen.
        """
        self.settings_screen.draw(self.screen)
        pygame.display.flip()