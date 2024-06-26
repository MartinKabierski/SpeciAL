import abc
import os
from functools import wraps
from typing import Optional, Callable, Any

import faicons
from shiny import render
from shiny import ui

from src.utils.constants import HTMLBody


class BaseTab(abc.ABC):

    def __init__(self, label: Optional[str] = None) -> None:
        current_file_path = os.path.abspath(__file__)
        self.FILE_NAME = os.path.basename(os.path.dirname(current_file_path))
        self.LABEL = label or self.FILE_NAME
        self.component: HTMLBody = None
        self.STYLE: str = "opacity: 94%;"
        self.ICON: HTMLBody = faicons.icon_svg("briefcase")

    @abc.abstractmethod
    def init_component(self) -> HTMLBody:
        raise NotImplementedError("Subclasses should implement this!")

