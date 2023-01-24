from Commands.Node import *
from MouseInterfaces.Draggable import Draggable

def init():
    global startImage
    startImage = graphics.getImage("Images/Buttons/PathButtons/start.png", 0.1)

class StartHeadingPoint(Draggable):

    def __init__(self, node: 'StartNode'):

        self.distanceToNode = 5
        self.drawRadius = 4
        self.drawRadiusBig = 5
        self.hoverRadius = 15
        self.distanceToNode = 6.5

        self.node = node

        super().__init__()
    
    def compute(self):
        self.position: PointRef = self.node.position + VectorRef(Ref.FIELD, magnitude = self.distanceToNode, heading = self.node.startHeading)

    def checkIfHovering(self, userInput: UserInput) -> bool:
        return Utility.distanceTuples(self.position.screenRef, userInput.mousePosition.screenRef) < self.hoverRadius

    def beDraggedByMouse(self, userInput: UserInput):
        
        # heading from startNode to mouse
        self.node.startHeading = Utility.thetaTwoPoints(self.node.position.fieldRef, userInput.mousePosition.fieldRef)

        # Snap to edge if close
        if self.node.next is not None:
            if Utility.headingDiff(self.node.next.beforeHeading, self.node.startHeading) < 0.12:
                self.node.startHeading = self.node.next.beforeHeading

        # snap to cardinal directions
        for i in [0, 3.1415/2, 3.1415, 3*3.1415/2]:
            if Utility.headingDiff(i, self.node.startHeading) < 0.12:
                self.node.startHeading = i

        self.node.program.recompute()


    def draw(self, screen: pygame.Surface):

        graphics.drawRoundedLine(screen, colors.GREEN, *self.node.position.screenRef, *self.position.screenRef, 2)

        r = self.drawRadiusBig if self.isHovering else self.drawRadius
        graphics.drawCircle(screen, *self.position.screenRef, colors.GREEN, r)
    

class StartNode(Node):

    def __init__(self, program, previous: 'Edge' = None, next: 'Edge' = None):

        defaultStartPosition: PointRef = PointRef(Ref.FIELD, (24, 48))
        super().__init__(program, defaultStartPosition, 20, previous = previous, next = next)

        self.startHeading = 0

        self.headingPoint: StartHeadingPoint = StartHeadingPoint(self)

    def compute(self):

        super().compute()
        self.headingPoint.compute()

        self.goalHeading = (self.next.beforeHeading) if self.next is not None else self.startHeading
        self.goalHeadingStr = Utility.headingToString(self.goalHeading)

        if self.next is None or Utility.headingsEqual(self.startHeading, self.goalHeading):
            self.direction = 0
        elif Utility.deltaInHeading(self.startHeading, self.goalHeading) > 0:
            self.direction = 1
        else:
            self.direction = -1
        

        if self.next is None:
            self.rotatedImage = startImage
        else:
            self.rotatedImage = pygame.transform.rotate(startImage, self.startHeading * 180 / 3.1415)
        self.rotatedImageH = graphics.getLighterImage(self.rotatedImage, 0.8)

    def draw(self, screen: pygame.Surface):

        super().draw(screen)

        self.headingPoint.draw(screen)

        isHovering = self.isHovering or self.command.isAnyHovering()

        image = self.rotatedImageH if isHovering else self.rotatedImage
        graphics.drawSurface(screen, image, *self.position.screenRef)

        