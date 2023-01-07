from enum import Enum

from MouseInterfaces.Hoverable import Hoverable
from MouseInterfaces.Draggable import Draggable
from MouseInterfaces.Clickable import Clickable

""" A class representing global state of the software."""

# Right click to toggle 1-3, buttons for all four at bottom left
class Mode(Enum):
    MOUSE_SELECT = 1 # Can hover over parts of path to see robot model's position.
    #                  Also can select turn/segment/curve/etc to modify it
    #                  If hovering over last node, can add a turn manually by clicking on it
    ADD_SEGMENT = 2 # left click to add segment (will add turn as well)
    ADD_CURVE = 3 # Configure path following parameters and export to robot; import recorded run to program
    PLAYBACK = 4 # run simulation

    # get next mode excluding playback
    def next(self):
        if self == Mode.MOUSE_SELECT:
            return Mode.ADD_SEGMENT
        elif self == Mode.ADD_SEGMENT:
            return Mode.ADD_CURVE
        else:
            return Mode.MOUSE_SELECT

class SoftwareState:

    def __init__(self):
        self.mode: Mode = Mode.MOUSE_SELECT
        self.objectHovering: Hoverable = None # object the mouse is currently hovering over
        self.objectDragged: Draggable = None # object the mouse is currently dragging

        self.isCode = False # whether displaying code (as opposed to block commands)

    def __str__(self):
        return "Software State:\nHovering: {}\nDragged: {}".format(self.objectHovering, self.objectDragged)

    

