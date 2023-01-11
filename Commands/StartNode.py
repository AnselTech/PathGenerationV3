from Commands.Node import *

def init():
    global startImage
    startImage = graphics.getImage("Images/Buttons/PathButtons/start.png", 0.1)

class StartNode(Node):

    def __init__(self, program, previous: 'Edge' = None, next: 'Edge' = None):

        defaultStartPosition: PointRef = PointRef(Ref.FIELD, (24, 48))
        super().__init__(program, defaultStartPosition, 20, previous = previous, next = next)

    def compute(self):

        super().compute()

        if self.next is not None:
            self.startHeading = self.next.beforeHeading
            if self.next.reversed:
                self.startHeading += 3.1415
        else:
            self.startHeading = None
        

        if self.next is None:
            self.rotatedImage = startImage
        else:
            self.rotatedImage = pygame.transform.rotate(startImage, self.startHeading * 180 / 3.1415)
        self.rotatedImageH = graphics.getLighterImage(self.rotatedImage, 0.8)

    def draw(self, screen: pygame.Surface):

        super().draw(screen)

        isHovering = self.isHovering or self.command.isAnyHovering()

        image = self.rotatedImageH if isHovering else self.rotatedImage
        graphics.drawSurface(screen, image, *self.position.screenRef)