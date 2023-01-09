from dataclasses import dataclass

"""
A ControllerInputState object describes the controller's velocity inputs to the robot for one
timestep.
Units in inch/sec
"""

@dataclass
class ControllerInputState:
    leftVelocity: float
    rightVelocity: float
    isDone: bool # whether the controller is finished