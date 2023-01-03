from Commands.Node import *

def init():
    global turnCImage, turnCCImage, turnCImageH, turnCCImageH
    turnCImage = graphics.getImage("Images/Buttons/PathButtons/clockwise.png", 0.07)
    turnCCImage = graphics.getImage("Images/Buttons/PathButtons/counterclockwise.png", 0.07)
    turnCImageH = graphics.getLighterImage(turnCImage, 0.8)
    turnCCImageH = graphics.getLighterImage(turnCCImage, 0.8)

class TurnNode(Node):

    def __init__(self, program, position: PointRef, previous: 'Edge' = None, next: 'Edge' = None):

        super().__init__(program, position, 15, previous = previous, next = next)
        self.direction = 0 # -1 for counterclockwise, 0 for no turn, 1 for clockwise

    # Given previous heading, return the resultant heading after the turn
    def compute(self) -> float:
        if self.next is None or Utility.headingDiff(self.previous.afterHeading, self.next.beforeHeading) < 0.005:
            self.direction = 0
        elif Utility.deltaInHeading(self.next.beforeHeading, self.previous.afterHeading) < 0:
            self.direction = 1
        else:
            self.direction = -1

    def draw(self, screen: pygame.Surface):

        isHovering = self.isHovering or self.command.isAnyHovering()

        if self.direction == 0:
            # draw black node
            graphics.drawCircle(screen, *self.position.screenRef, colors.BLACK, 7 if self.isHovering else 5)
        else:
            if self.direction == 1:
                image = turnCImageH if isHovering else turnCImage
            else:
                image = turnCCImageH if isHovering else turnCCImage

            graphics.drawSurface(screen, image, *self.position.screenRef)
            