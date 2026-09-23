import pygame

from models.settings import R6Settings
from config.ads_data import get_ads_names
from ui.components import Dropdown, InputField
from ui.colors import BG_DARK, TEXT_NORMAL, WHITE


# Dropdown options that are NOT sourced from ads_data
RESOLUTION_OPTIONS = ["1920x1080", "2560x1440", "3840x2160"]
ASPECT_OPTIONS = ["16:9", "4:3"]


class SettingsScreen:
    """
    The settings UI page. Two-column layout:
    Left: Mouse, Display
    Right: FOV & Advanced, Sensitivity & ADS
    """

    def __init__(
        self,
        settings: R6Settings,
        font: pygame.font.Font,
        width: int = 900,
        height: int = 520,
    ):
        self.font = font
        font_size = font.get_height()
        self.bold_font = pygame.font.SysFont("arial", font_size, bold=True)

        self.settings = settings
        self._width = width
        self._height = height

        # Recalculate layout based on current dimensions
        self._recalculate_layout(width, height)
        self._build_controls()
        

    def _recalculate_layout(self, width: int, height: int) -> None:
        """
        Recalculate all layout constants and control positions based on
        current window dimensions.
        """
        self._width = width
        self._height = height

        # ------------------------------------------------------------------
        # Proportional layout constants
        # ------------------------------------------------------------------
        # Horizontal: left column starts at 3.3%, right at 53%
        self.left_section_x = int(width * 0.033)
        self.left_label_x = int(width * 0.089)
        self.left_control_x = int(width * 0.256)
        self.left_control_w = int(width * 0.200)

        self.right_section_x = int(width * 0.533)
        self.right_label_x = int(width * 0.589)
        self.right_control_x = int(width * 0.756)
        self.right_control_w = int(width * 0.200)

        # Vertical: top section at 15%, bottom at 54%, line height ~8%
        self.top_section_y = int(height * 0.154)
        self.bottom_section_y = int(height * 0.538)
        self.line_height = int(height * 0.087)
        self.control_h = int(height * 0.069)

        self._build_controls()

    def _build_controls(self):
        """
        Create or recreate all InputField and Dropdown controls.
        Called during init and resize. Reads current values from
        self.settings to preserve data.
        """
        # ------------------------------------------------------------------
        # Top-left: Mouse
        # ------------------------------------------------------------------
        ly = self.top_section_y
        self._mouse_title_y = ly

        ly += int(self._height * 0.077)
        self.dpi_field = InputField(
            self.left_control_x, ly,
            self.left_control_w, self.control_h,
            value=self.settings.dpi,
            text_input_type="int",
            min_value=100,
            max_value=16000,
        )
        self._dpi_label_y = ly

        # ------------------------------------------------------------------
        # Top-right: FOV & Advanced
        # ------------------------------------------------------------------
        ry = self.top_section_y
        self._fov_section_title_y = ry

        ry += int(self._height * 0.077)
        self.fov_field = InputField(
            self.right_control_x, ry,
            self.right_control_w, self.control_h,
            value=self.settings.fov,
            text_input_type="int",
            min_value=60,
            max_value=120,
        )
        self._fov_label_y = ry

        ry += self.line_height
        self.xfactor_field = InputField(
            self.right_control_x, ry,
            self.right_control_w, self.control_h,
            value=self.settings.xfactorAiming,
            text_input_type="float",
        )
        self._xfactor_label_y = ry

        ry += self.line_height
        self.threshold_field = InputField(
            self.right_control_x, ry,
            self.right_control_w, self.control_h,
            value=self.settings.threshold,
            text_input_type="int",
            min_value=1,
            max_value=99,
        )
        self._threshold_label_y = ry

        # ------------------------------------------------------------------
        # Bottom-left: Display
        # ------------------------------------------------------------------
        ly = self.bottom_section_y
        self._display_title_y = ly

        ly += int(self._height * 0.077)
        res_index = (
            RESOLUTION_OPTIONS.index(self.settings.resolution)
            if self.settings.resolution in RESOLUTION_OPTIONS
            else 0
        )
        self.resolution_dropdown = Dropdown(
            self.left_control_x, ly,
            self.left_control_w, self.control_h,
            options=RESOLUTION_OPTIONS,
            selected_index=res_index,
        )
        self._resolution_label_y = ly

        ly += self.line_height
        asp_index = (
            ASPECT_OPTIONS.index(self.settings.aspectRatio)
            if self.settings.aspectRatio in ASPECT_OPTIONS
            else 0
        )
        self.aspect_dropdown = Dropdown(
            self.left_control_x, ly,
            self.left_control_w, self.control_h,
            options=ASPECT_OPTIONS,
            selected_index=asp_index,
        )
        self._aspect_label_y = ly

        # ------------------------------------------------------------------
        # Bottom-right: Sensitivity & ADS
        # ------------------------------------------------------------------
        ry = self.bottom_section_y
        self._sens_title_y = ry

        ry += int(self._height * 0.077)
        self.horiz_field = InputField(
            self.right_control_x, ry,
            self.right_control_w, self.control_h,
            value=self.settings.horizontalSens,
            text_input_type="int",
            min_value=1,
            max_value=100,
        )
        self._horiz_label_y = ry

        ry += self.line_height
        self.vert_field = InputField(
            self.right_control_x, ry,
            self.right_control_w, self.control_h,
            value=self.settings.verticalSens,
            text_input_type="int",
            min_value=1,
            max_value=100,
        )
        self._vert_label_y = ry

        ry += self.line_height
        ads_names = get_ads_names()
        ads_index = (
            self.settings.selectedAds
            if 0 <= self.settings.selectedAds < len(ads_names)
            else 0
        )
        self.ads_dropdown = Dropdown(
            self.right_control_x, ry,
            self.right_control_w, self.control_h,
            options=ads_names,
            selected_index=ads_index,
        )
        self._ads_label_y = ry

        # ------------------------------------------------------------------
        # Collections for easy iteration
        # ------------------------------------------------------------------
        self.input_fields = [
            self.dpi_field,
            self.fov_field,
            self.xfactor_field,
            self.threshold_field,
            self.horiz_field,
            self.vert_field,
        ]
        self.dropdowns = [
            self.resolution_dropdown,
            self.aspect_dropdown,
            self.ads_dropdown,
        ]

    def resize(self, width: int, height: int) -> None:
        """
        Recalculate layout and rebuild controls for a new window size.
        """
        self._recalculate_layout(width, height)

    # -----------------------------------------------------------------------
    # Event routing
    # -----------------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event) -> None:
        """
        Route Pygame events to the appropriate UI controls.

        KEY DESIGN: if any dropdown is expanded, give ALL dropdowns
        exclusive access to events.
        """
        any_expanded = any(d.expanded for d in self.dropdowns)

        if any_expanded:
            for dropdown in self.dropdowns:
                dropdown.handle_event(event)
            return

        for field in self.input_fields:
            field.handle_event(event)
        for dropdown in self.dropdowns:
            dropdown.handle_event(event)

    # -----------------------------------------------------------------------
    # Update (data sync)
    # -----------------------------------------------------------------------
    def update(self) -> None:
        """Synchronize UI control values back into the R6Settings model."""
        self._sync_from_ui()

    # -----------------------------------------------------------------------
    # Rendering
    # -----------------------------------------------------------------------
    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the entire settings screen.
        Font is no longer passed in — stored in self.font / self.bold_font.
        """
        # Background
        surface.fill(BG_DARK)

        # Main title
        title_surf = self.font.render("R6 Sensitivity Calibration", True, WHITE)
        title_rect = title_surf.get_rect(
            midtop=(surface.get_width() // 2, int(surface.get_height() * 0.038))
        )
        surface.blit(title_surf, title_rect)

        # --- Top row ---
        self._draw_section_title(surface, "Mouse", self.left_section_x, self._mouse_title_y)
        self._draw_label(surface, "DPI", self.left_label_x, self._dpi_label_y)

        self._draw_section_title(surface, "FOV & Advanced", self.right_section_x, self._fov_section_title_y)
        self._draw_label(surface, "FOV", self.right_label_x, self._fov_label_y)
        self._draw_label(surface, "XFactorAiming", self.right_label_x, self._xfactor_label_y)
        self._draw_label(surface, "Threshold(%)", self.right_label_x, self._threshold_label_y)

        # --- Bottom row ---
        self._draw_section_title(surface, "Display", self.left_section_x, self._display_title_y)
        self._draw_label(surface, "Resolution", self.left_label_x, self._resolution_label_y)
        self._draw_label(surface, "Aspect Ratio", self.left_label_x, self._aspect_label_y)

        self._draw_section_title(surface, "Sensitivity & ADS", self.right_section_x, self._sens_title_y)
        self._draw_label(surface, "Horizontal", self.right_label_x, self._horiz_label_y)
        self._draw_label(surface, "Vertical", self.right_label_x, self._vert_label_y)
        self._draw_label(surface, "Zoom", self.right_label_x, self._ads_label_y)

        # Phase 1: Draw input fields and collapsed dropdowns
        expanded_dropdowns = []
        for dropdown in self.dropdowns:
            if dropdown.expanded:
                expanded_dropdowns.append(dropdown)
            else:
                dropdown.draw(surface, self.font)

        for field in self.input_fields:
            field.draw(surface, self.font)

        # Phase 2: Draw expanded dropdowns LAST (on top layer)
        for dropdown in expanded_dropdowns:
            dropdown.draw(surface, self.font)

    # -----------------------------------------------------------------------
    # Private helpers
    # -----------------------------------------------------------------------
    def _draw_label(self, surface, text, x, y):
        """Draw a text label left-aligned, vertically centered to a control."""
        surf = self.font.render(text, True, TEXT_NORMAL)
        rect = surf.get_rect(
            midleft=(x, y + self.control_h // 2)
        )
        surface.blit(surf, rect)

    def _draw_section_title(self, surface, text, x, y):
        """
        Draw a section header using BOLD font.
        Positioned further left than labels for visual hierarchy.
        """
        surf = self.bold_font.render(text, True, WHITE)
        rect = surf.get_rect(topleft=(x, y))
        surface.blit(surf, rect)

    def _sync_from_ui(self):
        """Copy validated values from UI controls into the data model."""
        self.settings.dpi = self.dpi_field.get_value()
        self.settings.fov = self.fov_field.get_value()
        self.settings.horizontalSens = self.horiz_field.get_value()
        self.settings.verticalSens = self.vert_field.get_value()
        self.settings.xfactorAiming = self.xfactor_field.get_value()
        self.settings.threshold = self.threshold_field.get_value()

        self.settings.resolution = RESOLUTION_OPTIONS[
            self.resolution_dropdown.selected_index
        ]
        self.settings.aspectRatio = ASPECT_OPTIONS[
            self.aspect_dropdown.selected_index
        ]
        self.settings.selectedAds = self.ads_dropdown.selected_index