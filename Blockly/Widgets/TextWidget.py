
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
