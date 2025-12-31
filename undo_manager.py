# undo_manager.py

from collections import deque
from dataclasses import dataclass
from typing import Tuple

from config import Config
from models import Point


@dataclass
class RegionState:
    min_point: Point
    max_point: Point


class UndoManager:
    """Stores snapshots of region states for undo/redo."""

    def __init__(self):
        self.undo_stack: deque[list[RegionState]] = deque(maxlen=Config.MAX_UNDO_STACK)
        self.redo_stack: deque[list[RegionState]] = deque(maxlen=Config.MAX_UNDO_STACK)

    def snapshot(self, regions: list[Tuple[Point, Point]]) -> None:
        state = [RegionState(p1, p2) for p1, p2 in regions]
        self.undo_stack.append(state)
        self.redo_stack.clear()

    def can_undo(self) -> bool:
        return bool(self.undo_stack)

    def can_redo(self) -> bool:
        return bool(self.redo_stack)

    def push_redo(self, regions: list[Tuple[Point, Point]]) -> None:
        state = [RegionState(p1, p2) for p1, p2 in regions]
        self.redo_stack.append(state)

    def pop_undo(self) -> list[RegionState]:
        return self.undo_stack.pop()

    def pop_redo(self) -> list[RegionState]:
        return self.redo_stack.pop()
