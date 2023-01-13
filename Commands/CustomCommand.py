from MouseInterfaces.Draggable import Draggable
from MouseInterfaces.Clickable import Clickable
from MouseInterfaces.Hoverable import Hoverable
from Commands.Command import Command, CommandSlider, CommandToggle
from SingletonState.UserInput import UserInput
import graphics, Utility, pygame, colors, texteditor
from typing import Iterable

from Simulation.ControllerInputState import ControllerInputState
from Simulation.SimulationState import SimulationState
from Simulation.Simulator import Simulator
from Simulation.PID import PID

class DeleteButton(Clickable):

    def __init__(self, program, command):

        self.program = program
        self.command = command

        self.image = graphics.getImage("Images/trash.png", 0.05)
        self.imageH = graphics.getImage("Images/trashH.png", 0.05)

        self.dx = 220
        self.dy = Command.COMMAND_HEIGHT / 2

        super().__init__()

    def computePosition(self, x, y):
        self.x = x + self.dx
        self.y = y + self.dy

    def click(self):
        self.program.deleteCommand(self.command)

    def checkIfHovering(self, userInput: UserInput) -> bool:
        return Utility.distanceTuples(userInput.mousePosition.screenRef, (self.x, self.y)) < 20

    def draw(self, screen: pygame.Surface):
        image = self.imageH if self.isHovering else self.image
        graphics.drawSurface(screen, image, self.x, self.y)



class CustomCommand(Draggable, Command):
    def __init__(self, color, program, icon, nextCustomCommand = None):
        
        Command.__init__(self, None, color, program = program, nextCustomCommand = nextCustomCommand)
        self.icon = icon
        self.delete: DeleteButton = DeleteButton(program, self)

    def updatePosition(self, x, y):
        super().updatePosition(x,y)
        self.delete.computePosition(x, y)

    def getOtherHoverables(self) -> Iterable[Hoverable]:
        return
        yield

    def getHoverables(self) -> Iterable[Hoverable]:

        for hoverable in self.getOtherHoverables():
            yield hoverable

        yield self.delete
        yield self

    def getIcon(self) -> pygame.Surface:
        return self.icon

    def drawOther(self, screen: pygame.Surface):
        pass

    def drawInfo(self, screen: pygame.Surface):
        self.delete.draw(screen)
        self.drawOther(screen)

    def initSimulationController(self, simulationState: SimulationState):
        pass

    def simulateTick(self, simulationState: SimulationState) -> ControllerInputState:
        return ControllerInputState(0, 0, True)

    # Callback when the dragged object was just released
    def stopDragging(self):
        self.program.stopDragCustomCommand(self)

    # Called when the object was just pressed at the start of a drag
    def startDragging(self, userInput: UserInput):
        pass
    
    # Called every frame that the object is being dragged. Most likely used to update the position of the object based
    # on where the mouse is
    def beDraggedByMouse(self, userInput: UserInput):
        self.program.dragCustomCommand(userInput)


class Textbox(Clickable):

    def __init__(self, command: 'CustomCommand', text):

        self.command = command
        
        self.width = 120
        self.height = 24

        self.updateCode(text)

        super().__init__()

    def computePosition(self, commandX, commandY):

        self.x = commandX + 62
        self.y = commandY + Command.COMMAND_HEIGHT // 2 - self.height / 2

    def checkIfHovering(self, userInput: UserInput) -> bool:

        mx, my = userInput.mousePosition.screenRef

        if mx < self.x or mx > self.x + self.width:
            return False
        if my < self.y or my > self.y + self.height:
            return False
        return True

    def updateCode(self, code):
        self.code: str = code
        lines = self.code.split("\n")
        if len(lines) >= 2:
            lines = lines[0:4]

        self.surfaces = []
        for opacity in [150, 128]:
            self.surfaces.append(pygame.Surface((self.width, self.height)))
            self.surfaces[-1].set_alpha(opacity)
            self.surfaces[-1].fill([255,255,255])

            for i in range(0, len(lines)):
                graphics.drawText(self.surfaces[-1], graphics.FONTCODE, lines[i], colors.BLACK, 7, 2 + i * 9, 0, 0)

    def click(self):

        if Utility.IS_MAC:
            newCode = texteditor.open(self.code)
        else:

            newCode = ""

            # For windows computers, just poll user input on command line
            print("Type out your custom command manually. For each prompt, type in your line of code and press enter. Or, press 'q' to cancel or just enter to submit.")
            i = 1
            while True:
                string = input(f"Input line {i}: ").strip()
                if string == 'q':
                    print("Operation cancelled.")
                    return # exit
                elif string == '':
                    break
                newCode += string + "\n"
                i += 1

            newCode = newCode[:-1]

            print(f"Command now set to following code:\n{newCode}")

        self.updateCode(newCode)
        self.command.program.recomputeGeneratedCode()

    def draw(self, screen: pygame.Surface):
        surf = self.surfaces[1] if self.isHovering else self.surfaces[0]
        screen.blit(surf, (self.x,self.y))


class CodeCommand(CustomCommand):

    commandColors = [[181, 51, 255], [209, 160, 238]]
    text = "code"

    def __init__(self, program, nextCustomCommand = None, text = "// [insert code here]"):

        icon = graphics.getImage("Images/Commands/Custom.png", 0.08)
        super().__init__(self.commandColors, program, icon, nextCustomCommand)

        self.textbox: Textbox = Textbox(self, text)

    def updatePosition(self, x, y):
        super().updatePosition(x,y)
        self.textbox.computePosition(x, y)

    def getOtherHoverables(self) -> Iterable[Hoverable]:
        yield self.textbox

    def drawOther(self, screen: pygame.Surface):
        self.textbox.draw(screen)

    def getCode(self) -> str:
        return "\n" + self.textbox.code + "\n"


class TimeCommand(CustomCommand):

    commandColors = [[120, 120, 120], [190, 190, 190]]
    text = "time"

    def __init__(self, program, nextCustomCommand = None, time = 1):


        icon = graphics.getImage("Images/Commands/time.png", 0.08)
        super().__init__(self.commandColors, program, icon, nextCustomCommand)

        self.time = time
        self.slider = CommandSlider(self, 0.01, 4, 0.01, "Time (sec)", 1, dx = -100, color = [180, 180, 180])

    def getOtherHoverables(self) -> Iterable[Hoverable]:
        yield self.slider

    def updatePosition(self, x, y):
        super().updatePosition(x,y)
        self.slider.compute()

    def drawOther(self, screen: pygame.Surface):
        self.slider.draw(screen)

    def getCode(self) -> str:
        num = int(self.slider.getValue() * 1000)
        return f"pros::delay({num});"

class IntakeCommand(CustomCommand):

    commandColors = [[248, 128, 34], [251, 172, 110]]
    text = "intake"

    def __init__(self, program, nextCustomCommand = None, intakeSpeed = 1):

        icon = graphics.getImage("Images/Commands/intake.png", 0.08)
        super().__init__(self.commandColors, program, icon, nextCustomCommand)

        self.slider = CommandSlider(self, -1, 1, 0.05, "Intake speed", intakeSpeed, dx = -80)

    def getOtherHoverables(self) -> Iterable[Hoverable]:
        yield self.slider

    def drawOther(self, screen: pygame.Surface):
        self.slider.draw(screen)

    def getCode(self) -> str:
        return f"setEffort(*robot.intake, {round(self.slider.getValue(), 2)});"