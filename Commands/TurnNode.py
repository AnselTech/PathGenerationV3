from Commands.Node import *
from SingletonState.SoftwareState import Mode, SoftwareState

def init():
    global turnCImage, turnCCImage, turnCImageH, turnCCImageH
    turnCImage = graphics.getImage("Images/Buttons/PathButtons/clockwise.png", 0.07)
    turnCCImage = graphics.getImage("Images/Buttons/PathButtons/counterclockwise.png", 0.07)
    turnCImageH = graphics.getLighterImage(turnCImage, 0.8)
    turnCCImageH = graphics.getLighterImage(turnCCImage, 0.8)


# Every node has the option to shoot discs into the target goal.
# Right click to toggle shooting. Visually appears as a yellow vector
# Draggable to adjust aim
class Shoot(Draggable):

    def __init__(self, program, parent: 'Node'):

        super().__init__()

        self.program = program
        self.parent: 'Node' = parent

        self.turnToShootCommand: TurnCommand = TurnCommand(self, True)
        self.shootCommand: ShootCommand = ShootCommand(self)

        self.target: PointRef = PointRef(Ref.FIELD, point = (132, 132)) # red goal center

        self.active = False
        self.headingCorrection = 0 # [Heading to goal] + self.headingCorrection gives shooting heading
        self.heading = None
        self.magnitude = 10 # magnitude of vector in pixels
        self.hoverRadius = 10

    def compute(self):
        self.heading: float = (self.target - self.parent.position).theta() + self.headingCorrection
        self.headingStr = str(round(self.heading * 180 / 3.1415, 1)) + u"\u00b0"
        self.position: PointRef = self.parent.position + VectorRef(Ref.FIELD, magnitude = self.magnitude, heading = self.heading)
        vector: VectorRef = (self.position - self.parent.position)
        self.hoverPosition1: PointRef = self.parent.position + vector * 0.5
        self.hoverPosition2: PointRef = self.parent.position + vector * 1.2

        if not self.active or Utility.headingsEqual(self.parent.previous.afterHeading, self.heading):
            self.direction = None
        elif Utility.deltaInHeading(self.parent.previous.afterHeading, self.heading) < 0:
            self.direction = 1
        else:
            self.direction = -1

        self.goalHeading = self.heading


    # Hovering if touching the top half of the vector
    def checkIfHovering(self, userInput: UserInput) -> bool:

        if not self.active:
            return False

        return Utility.pointTouchingLine(
            *userInput.mousePosition.screenRef,
            *self.hoverPosition1.screenRef,
            *self.hoverPosition2.screenRef,
            self.hoverRadius
        )

    # Adjust headingCorrection based on where the mouse is dragging the arrow
    def beDraggedByMouse(self, userInput: UserInput):
        # the heading the mouse is dragging the shoot arrow to
        mouseHeading = Utility.thetaTwoPoints(self.parent.position.fieldRef, userInput.mousePosition.fieldRef)
        d = 0.06 * Utility.distanceTuples(self.parent.position.fieldRef, userInput.mousePosition.fieldRef)
        if Utility.headingDiff(mouseHeading, self.parent.previous.afterHeading) < 0.04 / d:
            # Possibly snap mouse heading to previous heading
            mouseHeading = self.parent.previous.afterHeading
        elif self.parent.next is not None and Utility.headingDiff(mouseHeading, self.parent.next.beforeHeading) < 0.04 / d:
            # Possibly snap mouse heading to next heading, if it exists
            mouseHeading = self.parent.next.beforeHeading
        
        shootHeading = (self.target - self.parent.position).theta()
        self.headingCorrection = Utility.deltaInHeading(mouseHeading, shootHeading)
        self.program.recompute()

    def draw(self, screen: pygame.Surface, color: tuple, thick: bool):
        thickness = 3
        a = 1.6
        
        if thick:
            graphics.drawGuideLine(screen, (255,255,0), *self.position.screenRef, self.heading)
        
        graphics.drawVector(screen, color, *self.parent.position.screenRef, *self.position.screenRef, thickness, a)



class TurnNode(Node):

    def __init__(self, program, position: PointRef, previous: 'Edge' = None, next: 'Edge' = None):

        super().__init__(program, position, 15, previous = previous, next = next)
        self.direction = 0 # -1 for counterclockwise, 0 for no turn, 1 for clockwise

        self.shoot: Shoot = Shoot(program, self)

    # Given previous heading, return the resultant heading after the turn
    def compute(self) -> float:

        self.shoot.compute()

        if self.shoot.active:
            before = self.shoot.heading
        else:
            before = self.previous.afterHeading
        
        if self.next is None or Utility.headingsEqual(before, self.next.beforeHeading):
            self.direction = 0
        elif Utility.deltaInHeading(before, self.next.beforeHeading) < 0:
            self.direction = 1
            self.goalHeading = self.next.beforeHeading
        else:
            self.direction = -1
            self.goalHeading = self.next.beforeHeading

       

    def draw(self, screen: pygame.Surface):

        # Draw shoot stuff
        thick = False
        if self.shoot.active:
            color = (255,230,0)
            if self.shoot.isHovering:
                thick = True
        elif self.isHovering:
            color = (255,215,0,150)

        if self.shoot.active or (self.isHovering and self.program.state.mode != Mode.MOUSE_SELECT):
            self.shoot.draw(screen, color, thick)



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
            