import importlib
import os

from shiny import ui

from src.utils.base_tab import BaseTab
from src.utils.constants import HTMLBody


def load_tabs() -> list[tuple[str, BaseTab]]:
    tabs = []
    base_path = "src/routes"
    for folder_name in os.listdir(base_path):
        folder_path = os.path.join(base_path, folder_name)
        if os.path.isdir(folder_path):
            init_file = os.path.join(folder_path, 'init.py')
            if os.path.exists(init_file):
                module_name = f"src.routes.{folder_name}.init"
                spec = importlib.util.spec_from_file_location(module_name, init_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                for attr in dir(module):
                    cls = getattr(module, attr)
                    if isinstance(cls, type) and issubclass(cls, BaseTab) and cls is not BaseTab:
                        tab_instance = cls()
                        tabs.append((folder_name, tab_instance))
    return tabs


def center(element: HTMLBody) -> HTMLBody:
    return ui.div(element, style="display: flex; justify-content: center; align-items: center; width: 100%")


def text_bold(text: str) -> HTMLBody:
    return ui.span(text, style="font-weight: bold;")


def row(*elements: HTMLBody) -> HTMLBody:
    return ui.div(elements, style="display: flex; gap: 20px;")
