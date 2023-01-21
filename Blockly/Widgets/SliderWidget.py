
from Blockly.Widgets.Widget import Widget
from Sliders.Slider import Slider

class SliderWidget(Slider, Widget):
    def __init__(self, parent, min: float, max: float, step: float, text: str, default: float = 0, dy = 0, dx = 0, program = None, color = None):
        
        self.min = min
        self.max = max
        self.step = step
        self.text = text
        self.default = default
        self.dy = dy
        self.dx = dx

        self.parent: 'Command' = parent
        if program is not None:
            self.program = program
        else:
            self.program = self.parent.program

        width = 65
        if color is None:
            color = self.parent.colors[0]
        super().__init__(self.getX(), self.getY(), width, self.min, self.max, self.step, color, self.text, self.default, textX = width/2, textY = -20, onSet = parent.onSliderUpdate)

    # enter value manually on console
    def onRightClick(self, userInput: UserInput):
        value = input(f"Enter value from {self.min} to {self.max}, or nothing to cancel: ").strip()
        if value != "":
            try:
                self.setValue(float(value))
                print("Value set to:", self.getValue())
            except:
                print("Invalid input.")
        else:
            print("Operation cancelled.")

    def getX(self):
        return self.parent.x + 175 + self.dx

    def getY(self):
        return self.parent.y + self.parent.height / 2 + self.dy

    def compute(self):
        self.x = self.getX()
        self.y = self.getY()