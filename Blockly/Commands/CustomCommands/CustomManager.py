from Blockly.Commands.CustomCommands.CustomCommand import CustomCommand
from Blockly.Commands.CustomCommands.CodeCommand import CodeCommand
from Blockly.Commands.CustomCommands.IntakeCommand import IntakeCommand
from Blockly.Commands.CustomCommands.RollerCommand import RollerCommand
from Blockly.Commands.CustomCommands.TimeCommand import TimeCommand

def getCustomClasses() -> list:
    return [
        CodeCommand,
        IntakeCommand,
        RollerCommand,
        TimeCommand
    ]

def getCustomCommandClass(id: str):
    for cls in getCustomClasses():
        if cls.id == id:
            return cls
    return None

def deserializeCustomCommand(id: str, info: dict) -> CustomCommand:
    command: CustomCommand = getCustomCommandClass(id)
    command.deserialize(info)
    return command