
class TurnCommand(Command):
    def __init__(self, parent, isShoot = False):

        self.isShoot = isShoot

        BLUE = [[57, 126, 237], [122, 169, 245]]
        super().__init__(parent, BLUE)

        self.toggle = CommandToggle(self, ["Tuned for precision", "Tuned for speed"], ["Precise", "Fast"], width = 135, dx = 47)

        self.imageLeft = graphics.getImage("Images/Commands/TurnLeft.png", 0.08)
        self.imageRight = graphics.getImage("Images/Commands/TurnRight.png", 0.08)

        

    def getIcon(self) -> pygame.Surface:
        clockwise = self.parent.direction == 1
        return self.imageRight if clockwise else self.imageLeft

    def drawInfo(self, screen: pygame.Surface):
        x = self.x + self.INFO_DX
        y = self.y + self.height/2
        
        graphics.drawText(screen, graphics.FONT15, self.parent.goalHeadingStr, colors.BLACK, x, y)
    
    def getCode(self) -> str:
        mode = "GTU_TURN_PRECISE" if self.toggle.get(int) == 0 else "GTU_TURN"
        num = round(self.parent.goalHeading * 180 / 3.1415, 2)
        return f"goTurnU(robot, {mode}, getRadians({num}));"

    def initSimulationController(self, simulationState: SimulationState):
        tolerance = 5 # tolerance interval in degrees
        self.pid = PID(12, 0, 0.2, tolerance = tolerance * 3.1415 / 180)

    # make a PID turn
    def simulateTick(self, simulationState: SimulationState) -> ControllerInputState:
        error = Utility.deltaInHeading(self.parent.goalHeading, simulationState.robotHeading)
        turnVelocity = self.pid.tick(error)
        return ControllerInputState(turnVelocity, -turnVelocity, self.pid.isDone())

    def _serialize(self, info: dict) -> None:
        info["toggle"] = self.toggle.get(int)

    # Given serialized data, update object with stored state
    def _deserialize(self, info: dict):
        self.toggle.activeOption = info["toggle"]
