import graphics, pygame
from SingletonState.FieldTransform import FieldTransform
from SingletonState.ReferenceFrame import PointRef
import math

class RobotImage:

    def __init__(self, fieldTransform: FieldTransform):
        self.transform = fieldTransform
        self.raw = graphics.getImage("Images/robot.png", 0.1)
        self.r = self.raw.get_rect()
        self.prevZoom = -1
        self.update()

    def update(self):

        size = (self.r.width * self.transform.zoom, self.r.height * self.transform.zoom)
        self.scaled = pygame.transform.smoothscale(self.raw, size)

    def draw(self, screen: pygame.Surface, position: PointRef, heading: float):

        if not math.isclose(self.prevZoom, self.transform.zoom):
            self.prevZoom = self.transform.zoom
            self.update()
        
        graphics.drawSurface(screen, self.scaled, *position.screenRef, heading * 180 / 3.1415)