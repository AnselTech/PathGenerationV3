from Simulation.ControllerInputState import ControllerInputState
from Simulation.SimulationState import SimulationState
import Utility, math
from SingletonState.ReferenceFrame import PointRef, Ref
import numpy as np

class Simulator:

    TRACK_WIDTH = 10 # in inches
    MAX_VELOCITY = 25 # linear velocity of a wheel / robot, inches per second
    TIMESTEP = 0.05 # the duration of each timestep in seconds

    MAX_ACCEL = 2 # maximum change in velocity in inches/sec per second
    LATERAL_FRICTION = 0.1 # coefficient of friction perpendicular to heading of robot (Between 0 and 1)

    def __init__(self, start: SimulationState):

        self.xPosition, self.yPosition = start.robotPosition.fieldRef
        self.heading = start.robotHeading
        self.deltaX, self.deltaY = 0,0
        self.xVelocity, self.yVelocity = 0,0
        self.angularVelocity = 0
        self.leftVelocity, self.rightVelocity = 0,0
        self.leftEncoderDistance, self.rightEncoderDistance = start.robotLeftEncoder, start.robotRightEncoder

    def simulateTick(self, input: ControllerInputState) -> SimulationState:

            # Clamp velocities within realistic range
            clampedLeftVelocity = Utility.clamp(input.leftVelocity, -self.MAX_VELOCITY, self.MAX_VELOCITY)
            clampedRightVelocity = Utility.clamp(input.rightVelocity, -self.MAX_VELOCITY, self.MAX_VELOCITY)

            # Limit the acceleration of the robot to robotSpecs.maximumAcceleration
            clampedLeftVelocity = Utility.clamp(clampedLeftVelocity, self.leftVelocity - 
            self.MAX_ACCEL, self.leftVelocity + self.MAX_ACCEL)
            clampedRightVelocity = Utility.clamp(clampedRightVelocity, self.rightVelocity - 
            self.MAX_ACCEL, self.rightVelocity + self.MAX_ACCEL)

            # update encoder distances
            self.leftEncoderDistance += clampedLeftVelocity * self.TIMESTEP
            self.rightEncoderDistance += clampedRightVelocity * self.TIMESTEP

            # Store the left and right velocities for the next tick
            self.leftVelocity = clampedLeftVelocity
            self.rightVelocity = clampedRightVelocity

            # Save the start locations to calculate the change in position later
            prevX, prevY = self.xPosition, self.yPosition
            
            if clampedLeftVelocity == clampedRightVelocity:
                # Special case where we have no rotation
                # radius = "INFINITE"
                omega = 0
                velocity = clampedLeftVelocity # left and right velocities are the same
                distance = velocity * self.TIMESTEP

                self.xPosition = self.xPosition + distance * math.cos(self.heading)
                self.yPosition = self.yPosition + distance * math.sin(self.heading)
                self.heading = self.heading # no change in heading
                
            else:   
                # Normal case where we have rotation

                # Calculate the radius of the circle we are turning on
                radius = (self.TRACK_WIDTH)*((clampedLeftVelocity+clampedRightVelocity)/
                (clampedLeftVelocity-clampedRightVelocity))
                
                # Calculate the angular velocity of the robot about the center of the circle
                omega = (clampedLeftVelocity-clampedRightVelocity)/self.TRACK_WIDTH
            
                # Calculate the center of the circle we are turning on (Instantaneous center of curvature)
                icc = np.array([self.xPosition - radius*math.sin(self.heading),
                self.yPosition + radius*math.cos(self.heading)])

                # Calculate the new position of the robot after the timestep

                #TransformMat:
                #[cos(omega*t) -sin(omega*t) 0]
                #[sin(omega*t) cos(omega*t)  0]
                #[0            0             1]
                transformMat = np.array([math.cos(omega*self.TIMESTEP),
                -math.sin(omega*self.TIMESTEP),0, math.sin(omega*self.TIMESTEP),
                math.cos(omega*self.TIMESTEP),0,0,0,1]).reshape(3,3)
                # print(transformMat)

                #[x-ICCx, y-ICCy, heading]
                matrixB = np.array([self.xPosition-icc[0],self.yPosition-icc[1],self.heading]).reshape(3,1)

                #[ICCx, ICCy, omega*t]
                matrixC = np.array([icc[0],icc[1],omega*self.TIMESTEP]).reshape(3,1)

                # The output is the new position of the robot after the timestep
                outputMatrix = np.matmul(transformMat,matrixB) + matrixC
                # print("Output: ",outputMatrix)

                # Set the new position of the robot
                self.xPosition = outputMatrix[0][0]
                self.yPosition = outputMatrix[1][0]
                self.heading = outputMatrix[2][0]

            # Unit vector in the direction of the robot's heading
            robotHeadingVector = np.array([math.cos(self.heading), math.sin(self.heading)])

            # Vector for the robot's velocity from the last timestep
            robotVelocityVector = np.array([self.xVelocity, self.yVelocity])

            # Calculate the lateral velocity of the robot
            lateralVelocity = np.cross(robotHeadingVector, robotVelocityVector)
            
            #Find the x and y components of the lateral velocity
            lateralX = lateralVelocity * math.cos(self.heading + math.pi/2)
            lateralY = lateralVelocity * math.sin(self.heading + math.pi/2)
            
            # Add the slip multiplied by friction coefficient
            self.xPosition += lateralX * (1-self.LATERAL_FRICTION)
            self.yPosition += lateralY * (1-self.LATERAL_FRICTION)

            # Calculate the velocity of the robot after the timestep
            self.xVelocity = self.xPosition - prevX
            self.yVelocity = self.yPosition - prevY
            self.angularVelocity = omega

            # TEMPORARY: clamp walls
            self.xPosition = Utility.clamp(self.xPosition, 0, 144)
            self.yPosition = Utility.clamp(self.yPosition, 0, 144)

            position = PointRef(Ref.FIELD, (self.xPosition, self.yPosition))
            return SimulationState(position, self.heading, self.leftEncoderDistance, self. rightEncoderDistance)