from AbstractCommand import Command

"""
Stores a list of commands, which make up the path
"""

class Program:

    def __init__(self):

        self.commands: list[Command] = []