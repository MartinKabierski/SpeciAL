import abc
from abc import ABC
from typing import Any, Callable, List, Optional, Literal

from htmltools import Tag
from shiny import ui, reactive
from shinywidgets import output_widget

from src import shared
from src.utils.constants import HTMLBody


class AbstractComponent(ABC):

    @abc.abstractmethod
    def apply(self) -> HTMLBody: ...


class AbstractLayout(abc.ABC):

    def __init__(self, main_component: HTMLBody, sidebar_component: HTMLBody) -> None:
        self.main_component: HTMLBody = main_component
        self.sidebar_component: HTMLBody | AbstractLayout = sidebar_component

    @abc.abstractmethod
    def apply(self) -> HTMLBody: ...


class SimpleLayout(AbstractLayout):

    def __init__(self, main_component: HTMLBody, sidebar_component: HTMLBody):
        super().__init__(main_component, sidebar_component)

    def apply(self) -> HTMLBody:
        layout = ui.layout_sidebar(
            ui.panel_sidebar(
                self.sidebar_component,
                width=2,
                # style="background-color: lightgray; padding: 15px; border-right: 1px solid black;"
            ),
            self.main_component
        )
        return layout


class SidebarOptions:
    def __init__(self) -> None:
        self.elements: dict[str, HTMLBody] = {}

    def add_section(self, key: str, label: str) -> None:
        self.elements[key] = ui.div(ui.h4(label, style="margin: 0px; font-weight: bold"),
                                    ui.hr(style="margin: 15px 0 0 0;"))

    def add_subsection(self, key: str, label: str) -> None:
        self.elements[key] = ui.div(ui.h6(label, style="margin: 0px; font-weight: bold"),
                                    ui.hr(style="margin: 15px 0 0 0;"))

    def add_slider(self, key: str, label: str, min_value: float, max_value: float, value: float) -> None:
        self.elements[key] = ui.input_slider(id=key, label=label, value=value, min=min_value, max=max_value)

    def add_input_text(self, key: str, label: str, value: str) -> None:
        self.elements[key] = ui.input_text(id=key, label=label, value=value)

    def add_numeric_input(self, key: str, label: str, value: float, min_value: float = None,
                          max_value: float = None) -> None:
        self.elements[key] = ui.input_numeric(id=key, label=label, value=value, min=min_value, max=max_value)

    def add_checkbox(self, key: str, label: str, value: bool = False) -> None:
        self.elements[key] = ui.input_checkbox(key, label, value)

    def add_radio_buttons(self, key: str, label: str, choices: list[str], selected: str = None) -> None:
        self.elements[key] = ui.input_radio_buttons(id=key, label=label, choices=choices, selected=selected)

    def add_select_input(self, key: str, label: str, choices: list[str], selected: str = None) -> None:
        self.elements[key] = ui.input_select(id=key, label=label, choices=choices, selected=selected)

    def add_text_area(self, key: str, label: str, value: str, rows: int = 3, cols: int = 40) -> None:
        self.elements[key] = ui.input_text_area(id=key, label=label, value=value, rows=rows, cols=cols)

    def add_date_input(self, key: str, label: str, value: str) -> None:
        self.elements[key] = ui.input_date(id=key, label=label, value=value)

    def add_input_switch(self, key: str, label: str, value: bool = False) -> None:
        self.elements[key] = ui.input_switch(id=key, label=label, value=value)

    def apply(self) -> list[HTMLBody]:
        return list(self.elements.values())

    def __getitem__(self, item: str):
        return self.elements[item].value

    def add_event_listener(self, key: str, callback: Callable[[Any], None]) -> None:
        @reactive.effect
        @reactive.event()
        def _():
            print("inner: ")


class BasicCardItem:

    def __init__(self,
                 title: Optional[HTMLBody] = None,
                 content: Optional[HTMLBody] = None,
                 footer: Optional[HTMLBody] = None
                 ) -> None:
        self.title: Optional[HTMLBody] = title
        self.content: Optional[HTMLBody] = content
        self.footer: Optional[HTMLBody] = footer
        self.style: str = "border-radius: 10px"
        self.class_names: str = "hover-effect"

    def apply(self) -> HTMLBody:
        items: List[HTMLBody] = []

        if self.title:
            items.append(ui.card_header(self.title))
        if self.content:
            items.append(self.content)
        if self.footer:
            items.append(ui.card_footer(self.footer))

        return ui.card(
            items,
            full_screen=False,
            style=self.style,
            class_=self.class_names
        )


class BasicCardGroup:
    def __init__(self,
                 cards: List[BasicCardItem],
                 orientation: Literal["row", "column"] = "row",
                 gap: str = "20px",
                 stretch_full_length: bool = False,
                 overflow: bool = False) -> None:
        self.cards: List[BasicCardItem] = cards
        self.orientation: Literal["row", "column"] = orientation
        self.gap: str = gap
        self.stretch_full_length: bool = stretch_full_length
        self.overflow: bool = overflow
        self.style: str = self._generate_style()

    def _generate_style(self) -> str:
        base_style = f"display: flex; gap: {self.gap};"
        if self.orientation == "row":
            base_style += "flex-wrap: nowrap;" if not self.overflow else "flex-wrap: wrap;"
        if self.stretch_full_length:
            base_style += " justify-content: space-between;"
        return base_style

    def apply(self) -> ui.div:
        style = self.style
        if self.orientation == "column":
            style = f"display: flex; flex-direction: column; gap: {self.gap};" \
                    f"{' justify-content: space-between;' if self.stretch_full_length else ''}"
        return ui.div(
            [card.apply() for card in self.cards],
            style=style
        )



class BaseLogicView(AbstractComponent):

    def __init__(self, title: str, cards: List[BasicCardItem], content: HTMLBody) -> None:
        self.cards: list[BasicCardItem] = cards
        self.title: str = title
        self.card_group: BasicCardGroup = BasicCardGroup(cards, orientation="row", gap="20px", stretch_full_length=True)
        self.content: HTMLBody = content

    def apply(self) -> HTMLBody:
        return ui.panel_main(self._apply())
        #return ui.panel_main(ui.div(ui.h4(self.title), ui.hr(style="padding:0;margin:0")), self._apply())

    def _apply(self) -> HTMLBody:
        return ui.div(self.card_group.apply(), self.content)


class NoFileLayout(AbstractComponent):

    def apply(self) -> HTMLBody:
        return ui.card(
            ui.div(
                ui.input_file("file_upload", "Select a file to view", accept=".xes")
            ),
            style="display: flex; flex-direction: column; align-items: center; min-height: 70vh"
        )


def basic_plot_layout(d0: bool, d1: bool, d2: bool, c0: bool, c1: bool, ln: bool, use_grid: bool = False) -> HTMLBody:
    html_plot_list: List[HTMLBody] = []
    if d0:
        html_plot_list.append(output_widget("tool1_d0_plot"))
    if d1:
        html_plot_list.append(output_widget("tool1_d1_plot"))
    if d2:
        html_plot_list.append(output_widget("tool1_d2_plot"))
    if c0:
        html_plot_list.append(output_widget("tool1_c0_plot"))
    if c1:
        html_plot_list.append(output_widget("tool1_c1_plot"))
    if ln:
        html_plot_list.append(output_widget("tool1_l_n_plot"))

    if use_grid:
        grid_layout: List[HTMLBody] = []
        for i in range(0, len(html_plot_list), 2):
            row: HTMLBody = ui.div(
                html_plot_list[i:i+2],
                style="display: flex; justify-content: space-between; margin-bottom: 10px;"
            )
            grid_layout.append(row)
        return ui.div(grid_layout, style="display: flex; flex-direction: column;")
    else:
        return ui.div(html_plot_list)
