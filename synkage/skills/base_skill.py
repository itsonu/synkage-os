"""Skill base class: an atomic, stateless capability with typed input and output.

Skills are called only by agents, and only through the skill registry, which
checks permissions (config/permissions.yaml `agent_skills`). They make no
decisions and touch no tools. A fresh instance is created for every call, so a
skill cannot carry state from one call to the next.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar

from pydantic import BaseModel

from synkage.config import SynkageConfig


class BaseSkill(ABC):
    name: ClassVar[str]
    description: ClassVar[str]
    Input: ClassVar[type[BaseModel]]
    Output: ClassVar[type[BaseModel]]

    def __init__(self, config: SynkageConfig):
        self.config = config  # read-only reference data (vocabulary, tools)

    @abstractmethod
    def run(self, data: BaseModel) -> BaseModel:
        """Pure transformation: validated Input -> Output."""
