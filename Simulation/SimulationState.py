from dataclasses import dataclass
from SingletonState.ReferenceFrame import PointRef

"""
A SimulationState objects describes the state of the robot and the field in one timestep.
This includes the robot's position, heading, number of discs stored, and 
the position of the discs.
This does not include the velocity of the robot
"""

@dataclass
class SimulationState:
    robotPosition: PointRef
    robotHeading: float
    