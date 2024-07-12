import importlib
import os
from typing import Optional

import faicons
from shiny import ui

from src.utils.base_tab import BaseTab
from src.utils.constants import HTMLBody
import faicons as fa


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


def row(*elements: HTMLBody, gap: str = "5px") -> HTMLBody:
    return ui.div(elements, style=f"display: flex; align-items: center; gap: {gap};")


def text_icon(text_key: str, icon: str) -> HTMLBody:
    return center(row(fa.icon_svg(icon), ui.output_text(text_key)))


def wrapped_div_to_container(*elements: HTMLBody, title: str = "", button_key: Optional[str] = None) -> HTMLBody:
    container_style = (
        "margin-left: 20px; "
        "margin-right: 20px; "
        "border: 1px solid black; "
        "padding: 10px; "
        "border-radius: 10px; "
        "background-color: white; "
        "margin-top: 25px; "
        "position: relative;"
    )

    legend_style = (
        "font-weight: bold; "
        "padding: 0 10px; "
        "position: absolute; "
        "top: -12px; "
        "left: 20px; "
        "background-color: white;"
    )

    title_html = ui.span(title, style=legend_style) if title else ""

    if button_key:
        title_html: HTMLBody = ui.div(title_html, create_info_button(button_key, "15px"),
                                      style="display: flex; align-items: center;")

    return ui.div(
        ui.div(title_html, ui.div(elements, style="padding-top: 10px;")),
        style=container_style
    )


def wrap_with_button(key: str, input_element: HTMLBody) -> HTMLBody:
    return ui.div(
        ui.div(
            input_element,
            class_="col-4 d-flex"
        ),
        ui.div(
            create_info_button(key),
            class_="col-8 d-flex",
        ),
        class_="row"
    )


def create_info_button(key: str, size: str = "26px") -> HTMLBody:
    return ui.input_action_button(
        f"{key}",
        None, icon=faicons.icon_svg("circle-info"),
        style=f"padding: 0 0 0 15px; margin: 0;border: none; background-color: transparent; font-size: {size};")


#         .prescript {
#             position: relative;
#             top: -0.5em;
#             font-size: 0.75em;
#         }
#         .operator {
#             display: inline-block;
#             position: relative;
#             top: 0;
#         }
#     </style>
# </head>
# <body>
#     <p>
#         Hier ist der Ausdruck direkt in HTML dargestellt:
#         <span class="prescript">0</span><span class="operator">D</span>

def mathematical_typesetting(prescript: str, operator: str) -> HTMLBody:
    return ui.span(
        ui.span(prescript, style="position: relative; top: -0.5em; font-size: 0.75em"),
        ui.span(operator, style="display: inline-block; position: relative; top: 0;")
    )
