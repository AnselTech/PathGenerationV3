from SingletonState.ReferenceFrame import PointRef, Ref, ScalarRef
from dataclasses import dataclass
import Utility, math

@dataclass
class Arc:
    fro: PointRef = None
    to: PointRef = None
    center: PointRef = None
    theta1: float = None
    theta2: float = None
    radius: ScalarRef = None
    heading1: float = None
    heading2: float = None
    parity: bool = None
    isStraight: bool = None
    arcLengthField: float = None

    def __init__(self, fro: PointRef = None, to: PointRef = None, heading1: float = None, isStraight: bool = False):
        self.isStraight = isStraight

        if fro is not None and to is not None and heading1 is not None:
            self.set(fro, to, heading1)

    def set(self, fro: PointRef, to: PointRef, heading1: float):

        self.fro = fro
        self.to = to

        if math.isclose(Utility.thetaTwoPoints(fro.fieldRef, to.fieldRef), heading1):
            self.isStraight = True
            self.center = None
            self.theta1 = None
            self.theta2 = None
            self.heading1 = heading1
            self.heading2 = heading1
            self.parity = None
            self.radius = None
            self.radiusF = None
            
            self.arcLengthField = Utility.distanceTuples(fro.fieldRef, to.fieldRef)
            return

        self.isStraight = False

        dx = to.fieldRef[0] - fro.fieldRef[0]
        dy = to.fieldRef[1] - fro.fieldRef[1]
        
        self.center = PointRef(Ref.FIELD, Utility.circleCenterFromTwoPointsAndTheta(*fro.fieldRef, *to.fieldRef, heading1))
        self.radius = ScalarRef(Ref.FIELD, Utility.distanceTuples(fro.fieldRef, self.center.fieldRef))

        self.theta1 = Utility.thetaTwoPoints(self.center.fieldRef, fro.fieldRef)
        self.theta2 = Utility.thetaTwoPoints(self.center.fieldRef, to.fieldRef)

        self.heading1 = heading1
        self.heading2 = Utility.thetaFromArc(heading1, dx, dy)

        self.parity = Utility.lineParity(*to.fieldRef, *fro.fieldRef, heading1)

        self.arcLengthField = abs(self.radius.fieldRef * Utility.deltaInHeadingParity(self.theta2, self.theta1, self.parity))

    def isTouching(self, pos: PointRef):

        # handle base case for straight line
        if self.isStraight:
            return Utility.pointTouchingLine(*pos.screenRef, *self.fro.screenRef, *self.to.screenRef, 13)
        # Otherwise, it's arc

        distance = Utility.distanceTuples(self.center.screenRef, pos.screenRef)
        if abs(self.radius.screenRef - distance) > 13: # no match in distance
            return False

        theta = Utility.thetaTwoPoints(self.center.fieldRef, pos.fieldRef)
        
        #a = Utility.deltaInHeading(self.theta1, self.theta2)
        #b = Utility.deltaInHeading(self.theta1, theta)
        c = Utility.deltaInHeadingParity(self.theta1, self.theta2, self.parity)
        d = Utility.deltaInHeadingParity(self.theta1, theta, self.parity)
        if c > 0:
            return d > c
        else:
            return d < c


