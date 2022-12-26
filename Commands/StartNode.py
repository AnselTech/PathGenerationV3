from Commands.Node import *

def init():
    global startImage
    startImage = graphics.getImage("Images/Buttons/PathButtons/start.png", 0.1)

class StartNode(Node):

    def __init__(self, program):

        defaultStartPosition: PointRef = PointRef(Ref.FIELD, (24, 48))
        super().__init__(program, defaultStartPosition, 20)
        self.afterHeading = 0

    def computeSubclass(self):
        if self.afterHeading is None:
            self.rotatedImage = startImage
        else:
            self.rotatedImage = pygame.transform.rotate(startImage, self.afterHeading * 180 / 3.1415)
        self.rotatedImageH = graphics.getLighterImage(self.rotatedImage, 0.8)

    def draw(self, screen: pygame.Surface): 
        image = self.rotatedImageH if self.isHovering else self.rotatedImage
        graphics.drawSurface(screen, image, *self.position.screenRef)