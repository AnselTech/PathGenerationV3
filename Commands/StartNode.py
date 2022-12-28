from Commands.Node import *

def init():
    global startImage
    startImage = graphics.getImage("Images/Buttons/PathButtons/start.png", 0.1)

class StartNode(Node):

    def __init__(self, program, previous: 'Edge' = None, next: 'Edge' = None):

        defaultStartPosition: PointRef = PointRef(Ref.FIELD, (24, 48))
        super().__init__(program, defaultStartPosition, 20, previous = previous, next = next)
        self.afterHeading = 0

    def compute(self):
        if self.next is None:
            self.rotatedImage = startImage
        else:
            self.rotatedImage = pygame.transform.rotate(startImage, self.next.beforeHeading * 180 / 3.1415)
        self.rotatedImageH = graphics.getLighterImage(self.rotatedImage, 0.8)

    def draw(self, screen: pygame.Surface): 

        isHovering = self.isHovering or self.command.isAnyHovering()

        image = self.rotatedImageH if isHovering else self.rotatedImage
        graphics.drawSurface(screen, image, *self.position.screenRef)