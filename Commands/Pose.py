from dataclasses import dataclass
from SingletonState.ReferenceFrame import PointRef

# x, y, and heading of a robot stored in field units (inches)
@dataclass
class Pose:

    pos: PointRef
    theta: float

    def __init__(self, position: PointRef, theta: float):
        self.pos = position
        self.theta = theta