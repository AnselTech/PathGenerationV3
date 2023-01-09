from AbstractButtons.ToggleButton import ToggleButton
from SingletonState.SoftwareState import SoftwareState, Mode
from VisibleElements.Tooltip import Tooltip
import pygame

"""
SelectorButtons change the SoftwareState mode
"""
class SelectorButton(ToggleButton):

    def __init__(self, program, state: SoftwareState, mode: Mode, tooltipString: str, position: tuple, imageOff: pygame.Surface, imageHovered: pygame.Surface, imageOn: pygame.Surface):
        self.program = program
        self.state: SoftwareState = state
        self.myMode: Mode = mode
        self.tooltip: Tooltip = Tooltip(tooltipString)
        super().__init__(position, imageOff, imageHovered, imageOn)

    # Return whether object was toggled on
    def isToggled(self) -> bool:
        return self.state.mode == self.myMode

    # Whether the object is disabled from being toggled on, and thus also does not change color when hovering
    def isDisabled(self) -> bool:
        return False

    # The action to do when the button is toggled on
    def toggleButtonOn(self) -> None:
        self.state.mode = self.myMode

    # The tooltip message
    def drawTooltip(self, screen: pygame.Surface, mousePosition: tuple) -> None:
        self.tooltip.draw(screen, mousePosition)