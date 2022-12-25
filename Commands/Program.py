from Edge import Edge, StraightEdge, CurveEdge
from Node import Node, StartNode, TurnNode
from MouseInterfaces.Hoverable import Hoverable
from SingletonState.ReferenceFrame import PointRef, Ref
from SingletonState.SoftwareState import SoftwareState
import pygame, Utility
from typing import Iterator

"""
Stores a list of commands, which make up the path
"""

class Program:

    def __init__(self):
        self.nodes: list[Node] = [ StartNode() ]
        self.edges: list[Edge] = []
        