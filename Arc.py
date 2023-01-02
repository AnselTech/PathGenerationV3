from SingletonState.ReferenceFrame import PointRef, Ref
from dataclasses import dataclass
import Utility

@dataclass
class Arc:
    fro: PointRef = None
    to: PointRef = None
    center: PointRef = None
    theta1: float = None
    theta2: float = None
    radius: float = None
    heading1: float = None
    heading2: float = None
    parity: bool = None

    def __init__(self, fro: PointRef = None, to: PointRef = None, heading1: float = None):
        if fro is not None and to is not None and heading1 is not None:
            self.set(fro, to, heading1)

    def set(self, fro: PointRef, to: PointRef, heading1: float):

        self.fro = fro
        self.to = to

        dx = to.fieldRef[0] - fro.fieldRef[0]
        dy = to.fieldRef[1] - fro.fieldRef[1]
        
        self.center = PointRef(Ref.FIELD, Utility.circleCenterFromTwoPointsAndTheta(*fro.fieldRef, *to.fieldRef, heading1))
        self.radius = Utility.distanceTuples(fro.screenRef, self.center.screenRef)

        self.theta1 = Utility.thetaTwoPoints(self.center.fieldRef, fro.fieldRef)
        self.theta2 = Utility.thetaTwoPoints(self.center.fieldRef, to.fieldRef)

        self.heading1 = heading1
        self.heading2 = Utility.thetaFromArc(heading1, dx, dy)

        self.parity = Utility.lineParity(*to.fieldRef, *fro.fieldRef, heading1)
