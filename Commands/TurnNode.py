from Commands.Node import *

def init():
    global turnCImage, turnCCImage, turnCImageH, turnCCImageH
    turnCImage = graphics.getImage("Images/Buttons/PathButtons/clockwise.png", 0.07)
    turnCCImage = graphics.getImage("Images/Buttons/PathButtons/counterclockwise.png", 0.07)
    turnCImageH = graphics.getLighterImage(turnCImage, 0.8)
    turnCCImageH = graphics.getLighterImage(turnCCImage, 0.8)

class TurnNode(Node):

    def __init__(self, program, position: PointRef):

        super().__init__(program, position, 15)
        self.clockwise: bool = False
        self.hasTurn: bool = False
        self.afterHeading = 0

    # Given previous heading, return the resultant heading after the turn
    def computeSubclass(self) -> float:
        if self.afterHeading is None or math.isclose(self.beforeHeading, self.afterHeading):
            self.hasTurn = False
        else:
            self.hasTurn = True
            self.clockwise = Utility.deltaInHeading(self.afterHeading, self.beforeHeading) < 0

    def draw(self, screen: pygame.Surface):

        isHovering = self.isHovering or self.command.isAnyHovering()

        # draw turn node
        if self.hasTurn:

            if self.clockwise:
                image = turnCImageH if isHovering else turnCImage
            else:
                image = turnCCImageH if isHovering else turnCCImage

            graphics.drawSurface(screen, image, *self.position.screenRef)

        else:
            # draw black node
            graphics.drawCircle(screen, *self.position.screenRef, colors.BLACK, 7 if self.isHovering else 5)