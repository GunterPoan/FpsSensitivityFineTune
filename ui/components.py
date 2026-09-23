import pygame

from ui.colors import (
    PANEL_BG,
    PANEL_BORDER,
    TEXT_NORMAL,
    TEXT_DIM,
    INPUT_ACTIVE_BORDER,
    DROPDOWN_HOVER,
    WHITE,
)



class Dropdown:
    """
    A reusable dropdown component for Pygame.
    Displays a collapsed field that expands into a list of options on click.
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        options: list[str],
        selected_index: int = 0,
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.selected_index = selected_index
        self.expanded = False
        self.hover_index = -1
        self.option_height = height
        self._expand_direction = "down"  # "down" or "up"

    # -----------------------------------------------------------------------
    # Event handling
    # -----------------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event) -> None:
        """
        Process a single Pygame event.
        Must be called every frame for all dropdowns before drawing.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos

            # --- Click on the collapsed box itself ---
            if self.rect.collidepoint(mouse_pos):
                self.expanded = not self.expanded
                return

            # --- Click while expanded ---
            if self.expanded:
                # Check if click landed on any option
                for i, _ in enumerate(self.options):
                    option_rect = self._get_option_rect(i)
                    if option_rect.collidepoint(mouse_pos):
                        self.selected_index = i
                        self.expanded = False
                        self.hover_index = -1
                        return

                # Click outside the list → close without changing selection
                self.expanded = False
                self.hover_index = -1

        # --- Hover tracking while expanded ---
        if event.type == pygame.MOUSEMOTION and self.expanded:
            mouse_pos = event.pos
            self.hover_index = -1
            for i, _ in enumerate(self.options):
                if self._get_option_rect(i).collidepoint(mouse_pos):
                    self.hover_index = i
                    break

    # -----------------------------------------------------------------------
    # Rendering
    # -----------------------------------------------------------------------
    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """
        Draw the dropdown onto the given surface.
        Call this every frame inside the draw phase.
        """
        # --- Draw collapsed box ---
        border_color = INPUT_ACTIVE_BORDER if self.expanded else PANEL_BORDER
        pygame.draw.rect(surface, PANEL_BG, self.rect)
        pygame.draw.rect(surface, border_color, self.rect, 2)

        selected_text = self.options[self.selected_index]
        text_surf = font.render(selected_text, True, TEXT_NORMAL)
        text_rect = text_surf.get_rect(
            midleft=(self.rect.x + 10, self.rect.centery)
        )
        surface.blit(text_surf, text_rect)

        # Draw arrow indicator
        arrow = "▲" if self.expanded else "▼"
        arrow_surf = font.render(arrow, True, TEXT_NORMAL)
        arrow_rect = arrow_surf.get_rect(
            midright=(self.rect.right - 10, self.rect.centery)
        )
        surface.blit(arrow_surf, arrow_rect)

        # --- Draw expanded list ---
        if self.expanded:
            # Auto-detect expand direction based on available space
            total_options_height = len(self.options) * self.option_height
            space_below = surface.get_height() - (self.rect.y + self.rect.height)
            space_above = self.rect.y
            
            if total_options_height > space_below and space_above > space_below:
                self._expand_direction = "up"
            else:
                self._expand_direction = "down"
                
            for i, option in enumerate(self.options):
                option_rect = self._get_option_rect(i)

                # Background: hover highlight or normal
                bg_color = DROPDOWN_HOVER if i == self.hover_index else PANEL_BG
                pygame.draw.rect(surface, bg_color, option_rect)
                pygame.draw.rect(surface, PANEL_BORDER, option_rect, 1)

                # Text
                text_surf = font.render(option, True, TEXT_NORMAL)
                text_rect = text_surf.get_rect(
                    midleft=(option_rect.x + 10, option_rect.centery)
                )
                surface.blit(text_surf, text_rect)

    # -----------------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------------
    def _get_option_rect(self, index: int) -> pygame.Rect:
        """
        Compute the screen rectangle for the option at *index*
        when the dropdown is expanded.
        """
        if self._expand_direction == "up":
            y = self.rect.y - (index + 1) * self.option_height
        else:
            y = self.rect.y + (index + 1) * self.option_height
        return pygame.Rect(
            self.rect.x,
            y,
            self.rect.width,
            self.option_height,
        )


# ===========================================================================
# InputField
# ===========================================================================
class InputField:
    """
    A reusable text input field for numeric values.
    Supports integer and float input with optional range validation.
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        value,
        text_input_type: str = "int",
        min_value=None,
        max_value=None,
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.text_input_type = text_input_type
        self.min_value = min_value
        self.max_value = max_value

        # Ensure initial value is a valid number
        if self.text_input_type == "int":
            self.value = int(value)
        else:
            self.value = float(value)

        self.text = str(self.value)
        self.editing = False
        self.cursor_visible = True
        self.cursor_timer = 0

    # -----------------------------------------------------------------------
    # Event handling
    # -----------------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            was_editing = self.editing
            self.editing = self.rect.collidepoint(event.pos)

            if was_editing and not self.editing:
                # Clicked outside while editing → commit
                self._commit()

        if self.editing and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self._commit()
                self.editing = False

            elif event.key == pygame.K_BACKSPACE:
                if len(self.text) > 0:
                    self.text = self.text[:-1]

            elif event.key == pygame.K_ESCAPE:
                # Cancel editing, revert to stored value
                self.text = str(self.value)
                self.editing = False

            else:
                # Append character
                char = event.unicode
                self._handle_char_input(char)

    def _handle_char_input(self, char: str) -> None:
        """
        Filter and append a single character based on input type.
        """
        if not char:
            return

        allowed = set("0123456789")
        if self.text_input_type == "float":
            allowed.add(".")

        # Allow negative sign only at the start
        if char == "-":
            if len(self.text) == 0:
                self.text = "-"
            return

        if char not in allowed:
            return

        # Prevent multiple decimal points for floats
        if char == "." and "." in self.text:
            return

        # For ints: try parsing to prevent garbage accumulation
        if self.text_input_type == "int":
            new_text = self.text + char
            try:
                int(new_text)
                self.text = new_text
            except ValueError:
                pass
        else:
            self.text += char

    def _commit(self) -> None:
        """
        Try to parse text into a valid value.
        If invalid or out of range, revert to the previous value.
        """
        try:
            if self.text_input_type == "int":
                new_value = int(self.text)
            else:
                new_value = float(self.text)
        except ValueError:
            self.text = str(self.value)
            return

        if self.min_value is not None and new_value < self.min_value:
            self.text = str(self.value)
            return
        if self.max_value is not None and new_value > self.max_value:
            self.text = str(self.value)
            return

        self.value = new_value
        self.text = str(self.value)

    # -----------------------------------------------------------------------
    # Rendering
    # -----------------------------------------------------------------------
    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        # Cursor blink timer
        if self.editing:
            self.cursor_timer += 1
            if self.cursor_timer >= 1200:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0

        # Border color: blue when editing, gray when normal
        border_color = INPUT_ACTIVE_BORDER if self.editing else PANEL_BORDER
        pygame.draw.rect(surface, PANEL_BG, self.rect)
        pygame.draw.rect(surface, border_color, self.rect, 2)

        # Determine display text: editing shows self.text, normal shows value
        display_text = self.text if self.editing else str(self.value)
        text_color = TEXT_NORMAL if self.editing else TEXT_DIM

        # Render text
        text_surf = font.render(display_text, True, text_color)
        max_text_width = self.rect.width - 20
        if text_surf.get_width() > max_text_width:
            display_text = display_text[: len(display_text) - 1]
            text_surf = font.render(display_text, True, text_color)

        text_rect = text_surf.get_rect(
            midleft=(self.rect.x + 10, self.rect.centery)
        )
        surface.blit(text_surf, text_rect)

        # Draw cursor if editing
        if self.editing and self.cursor_visible:
            cursor_x = self.rect.x + 10 + text_surf.get_width()
            cursor_top = self.rect.y + 8
            cursor_bottom = self.rect.y + self.rect.height - 8
            pygame.draw.line(
                surface,
                WHITE,
                (cursor_x, cursor_top),
                (cursor_x, cursor_bottom),
                2,
            )

    # -----------------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------------
    def get_value(self):
        """Return the current validated value."""
        return self.value

    def set_value(self, value) -> None:
        """Programmatically set the value and text."""
        if self.text_input_type == "int":
            self.value = int(value)
        else:
            self.value = float(value)
        self.text = str(self.value)