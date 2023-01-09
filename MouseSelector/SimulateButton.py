from MouseSelector.SelectorButton import SelectorButton

"""
The SelectorButton class is specifically overidden for playback to run simulation code
"""

class SimulateButton(SelectorButton):

    # Simulation code
    def toggleButtonOn(self) -> None:
        self.program.generateSimulation()