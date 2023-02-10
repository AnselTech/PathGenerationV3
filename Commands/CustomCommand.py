from MouseInterfaces.Draggable import Draggable
from MouseInterfaces.Clickable import Clickable
from MouseInterfaces.Hoverable import Hoverable
from Commands.Command import Command, CommandSlider, CommandToggle, CommandAddon
from SingletonState.UserInput import UserInput
import graphics, Utility, pygame, colors, texteditor
from typing import Iterable

from Simulation.ControllerInputState import ControllerInputState
from Simulation.SimulationState import SimulationState
from Simulation.Simulator import Simulator
from Simulation.PID import PID

class DeleteButton(Clickable, CommandAddon):

    def __init__(self, program, command):

        self.program = program
        self.parent = command

        self.image = graphics.getImage("Images/trash.png", 0.05)
        self.imageH = graphics.getImage("Images/trashH.png", 0.05)

        self.dx = 230
        self.dy = Command.COMMAND_HEIGHT / 2

        super().__init__()

    def computePosition(self, x, y):
        self.x = x + self.dx
        self.y = y + self.dy

    def click(self):
        #print(type(self.parent))
        self.program.deleteCommand(self.parent)

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

    def isAddOnsHovering(self) -> bool:
        return self.delete.isHovering


class Textbox(Clickable, CommandAddon):

    def __init__(self, command: 'CustomCommand', text):

        self.parent = command
        
        self.width = 130
        self.height = 24

        self.updateCode(text)

        super().__init__()

    def computePosition(self, commandX, commandY):

        self.x = commandX + 70
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
            print("Currrent code: ")
            print(self.code)
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
        self.parent.program.recomputeGeneratedCode()

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

    def isAddOnsHovering(self) -> bool:
        return super().isAddOnsHovering() or self.textbox.isHovering


class TimeCommand(CustomCommand):

    commandColors = [[120, 120, 120], [195, 195, 195]]
    text = "time"

    def __init__(self, program, nextCustomCommand = None, time = 1):


        icon = graphics.getImage("Images/Commands/time.png", 0.08)
        super().__init__(self.commandColors, program, icon, nextCustomCommand)

        self.time = time
        self.slider = CommandSlider(self, 0.01, 4, 0.01, "Time (sec)", 1, dx = -50, color = [180, 180, 180])

    def getOtherHoverables(self) -> Iterable[Hoverable]:
        yield self.slider

    def updatePosition(self, x, y):
        super().updatePosition(x,y)
        self.slider.compute()

    def drawOther(self, screen: pygame.Surface):
        num = str(self.slider.getValue())
        graphics.drawText(screen, graphics.FONT15, num + "s", colors.BLACK, self.x + self.INFO_DX, self.y + Command.COMMAND_HEIGHT/2)
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

        self.slider = CommandSlider(self, -1, 1, 0.05, "Intake speed", intakeSpeed, dx = -50)

    def getOtherHoverables(self) -> Iterable[Hoverable]:
        yield self.slider

    def drawOther(self, screen: pygame.Surface):
        text = f"{int(round(self.slider.getValue() * 100))}%"
        graphics.drawText(screen, graphics.FONT15, text, colors.BLACK, self.x + self.INFO_DX, self.y + Command.COMMAND_HEIGHT/2)
        self.slider.draw(screen)

    def getCode(self) -> str:
        return f"setEffort(*robot.intake, {round(self.slider.getValue(), 2)});"


class RollerCommand(CustomCommand):

    commandColors = [[255, 86, 242], [251, 147, 243]]
    text = "roller"

    def __init__(self, program, nextCustomCommand = None, rollerSpeed = 1, toggleMode = 0, rollerDistance = 180, rollerTime = 0.5):

        icon = graphics.getImage("Images/Commands/roller.png", 0.07)
        super().__init__(self.commandColors, program, icon, nextCustomCommand)

        self.toggle = CommandToggle(self, ["Run for distance", "Run for time"], ["D", "T"],  dx = -40)
        self.sliderSpeed = CommandSlider(self, -1, 1, 0.05, "Roller speed", rollerSpeed, dx = -50, dy = -14)
        self.sliderDistance = CommandSlider(self, -360, 360, 10, "Rotations (deg)", rollerDistance, dx = -50, dy = 14)
        self.sliderTime = CommandSlider(self, 0.1, 3, 0.1, "Time (seconds)", rollerTime, dx = -50, dy = 14)

        self.toggle.activeOption = toggleMode

    def getOtherHoverables(self) -> Iterable[Hoverable]:
        yield self.toggle
        yield self.sliderSpeed
        if self.toggle.get(int) == 0:
            yield self.sliderDistance
        else:
            yield self.sliderTime

    def updatePosition(self, x, y):
        super().updatePosition(x,y)
        self.sliderSpeed.compute()
        self.sliderDistance.compute()
        self.sliderTime.compute()

    def drawOther(self, screen: pygame.Surface):
        self.sliderSpeed.draw(screen)
        if self.toggle.get(int) == 0:
            self.sliderDistance.draw(screen)
        else:
            self.sliderTime.draw(screen)

    def getCode(self) -> str:
        if self.toggle.get(int) == 0:
            return f"\nmoveRollerDegrees(robot, {self.sliderDistance.getValue()}, {self.sliderSpeed.getValue()});\n"
        else:
            return f"\nmoveRollerTime(robot, {self.sliderTime.getValue()}, {self.sliderSpeed.getValue()});\n"

    def isAddOnsHovering(self) -> bool:
        return super().isAddOnsHovering() or self.sliderSpeed.isHovering or self.sliderTime.isHovering


class FlapCommand(CustomCommand):

    commandColors = [[34, 245, 231], [152, 237, 232]]
    text = "flap"

    def __init__(self, program, nextCustomCommand = None, flapUp = 0):

        icon = graphics.getImage("Images/Commands/flap.png", 0.07)
        super().__init__(self.commandColors, program, icon, nextCustomCommand)

        self.toggle = CommandToggle(self, ["Pneumatic flap down", "Pneumatic flap up"], ["Down", "Up"],   width = 135, dx = 47)

        self.toggle.activeOption = flapUp

    def getOtherHoverables(self) -> Iterable[Hoverable]:
        yield self.toggle


    def getCode(self) -> str:

        if self.toggle.activeOption == 0:
            value = "false"
        else:
            value = "true"

        return f"\nrobot.shooterFlap->set_value({value});"


class DoRollerCommand(CustomCommand):

    commandColors = [[117, 61, 61], [201, 167, 167]]
    text = "backIntoRoller"

    def __init__(self, program, nextCustomCommand = None):

        icon = graphics.getImage("Images/Commands/roller.png", 0.07)
        super().__init__(self.commandColors, program, icon, nextCustomCommand)

    def drawOther(self, screen: pygame.Surface):
        graphics.drawText(screen, graphics.FONT15, "Back up and do roller", [0,0,0], self.x + self.INFO_DX + 50, self.y + Command.COMMAND_HEIGHT/2)

    def getCode(self) -> str:

        string =  "\n// Back up and do rollers using drivetrain current detection\n"
        string += "robot.drive->setEffort(-0.3, -0.3);\n"
        string += "robot.roller->move_velocity(100);\n"
        string += "uint32_t endTime = pros::millis() + 2000;"
        string += "while (robot.drive->getCurrent() < 1.2 && pros::millis() < endTime) pros::delay(10);\n"
        string += "robot.roller->brake();\n"
        string += "robot.drive->stop();\n"

        return string


