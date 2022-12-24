from SingletonState.SoftwareState import SoftwareState, Mode
from MouseSelector.SelectorButton import SelectorButton
from MouseInterfaces.Hoverable import Hoverable
import pygame, Utility, graphics
from typing import Tuple, Iterator

"""
Select the SoftwareState mode / mouse tool
Shown as four toggle buttons at the bottom left corner of the screen

MOUSE_SELECT: Can hover over parts of path to see robot model's position.
              Also can select turn/segment/curve/etc to modify it
              If hovering over last node, can add a turn manually by clicking on it
ADD_SEGMENT:  Left click to add segment (will add turn as well)
ADD_CURVE:    Configure path following parameters and export to robot; import recorded run to program
PLAYBACK:     Run simulation
"""

class MouseSelector:

    # return [imageOff, imageHovered, imageOn]
    def getImage(self, filename: str) -> Tuple[pygame.Surface, pygame.Surface, pygame.Surface]:
        filename = "Images/Buttons/MouseSelector/" + filename + ".png"
        raw = graphics.getImage(filename, 0.1)

        off = graphics.getLighterImage(raw, 0.5)
        hovered = graphics.getLighterImage(raw, 0.8)
        on = graphics.getLighterImage(raw, 1)

        return off, hovered, on
    
    def __init__(self, state: SoftwareState):

        self.state: SoftwareState = state

        # the four buttons
        by = Utility.SCREEN_SIZE - 50
        dx = 45
        bx = Utility.SCREEN_SIZE - dx*4 - 10

        self.mouseSelect: SelectorButton = SelectorButton(state, Mode.MOUSE_SELECT,
            "View or modify the existing path", (bx, by), *self.getImage("select"))

        self.addSegment: SelectorButton = SelectorButton(state, Mode.ADD_SEGMENT,
            "Left click to add a new segment", (bx+dx, by), *self.getImage("straight"))

        self.addCurve: SelectorButton = SelectorButton(state, Mode.ADD_CURVE,
            "Left click to add a new curve", (bx+dx*2, by), *self.getImage("curve"))

        self.playback: SelectorButton = SelectorButton(state, Mode.PLAYBACK,
            "Run a simulation of the current path", (bx+dx*3, by), *self.getImage("play"))

        self.buttons: list[SelectorButton] = [self.mouseSelect, self.addSegment, self.addCurve, self.playback]

    # Returns a generator of the four buttons
    def getHoverables(self) -> Iterator[Hoverable]:

        for button in self.buttons:
            yield button

    # Draw the four buttons
    def draw(self, screen: pygame.Surface):

        for button in self.buttons:
            button.draw(screen)
