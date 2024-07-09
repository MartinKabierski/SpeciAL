import abc
from abc import ABC
from typing import Any, Callable, List, Optional, Literal

import faicons
import pandas as pd
from htmltools import Tag
from shiny import ui, reactive
from shinywidgets import output_widget

from src import shared
from src.utils.constants import HTMLBody
from src.utils.storage import StorageManager


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
        self.info_keys: list[str] = []

    def add_section(self, key: str, label: str) -> None:
        self.elements[key] = ui.div(
            ui.h4(label, style="margin: 0px; font-weight: bold"),
            ui.hr(style="margin: 15px 0 0 0;")
        )

    def add_subsection(self, key: str, label: str) -> None:
        self.elements[key] = ui.div(
            ui.h6(label, style="margin: 0px; font-weight: bold"),
            ui.hr(style="margin: 15px 0 0 0;")
        )

    def _wrap_with_button(self, key: str, input_element: HTMLBody) -> HTMLBody:
        return ui.div(
            ui.div(
                input_element,
                class_="col-10 d-flex align-items-center justify-content-center"
            ),
            ui.div(
                ui.input_action_button(
                    f"{key}_info",
                    None, icon=faicons.icon_svg("circle-info"),
                    style="padding: 0; margin: 0;border: none; background-color: transparent; font-size: 26px"),
                class_="col-2 d-flex align-items-center justify-content-center",
            ),
            class_="row"
        )

    def add_slider(self, key: str, label: str, min_value: float, max_value: float, value: float) -> None:
        slider = ui.input_slider(id=key, label=label, value=value, min=min_value, max=max_value)
        self.elements[key] = self._wrap_with_button(key, slider)
        self.info_keys.append(f"{key}_info")

    def add_input_text(self, key: str, label: str, value: str) -> None:
        input_text = ui.input_text(id=key, label=label, value=value)
        self.elements[key] = self._wrap_with_button(key, input_text)
        self.info_keys.append(f"{key}_info")

    def add_numeric_input(self, key: str, label: str, value: float, min_value: float = None,
                          max_value: float = None) -> None:
        numeric_input = ui.input_numeric(id=key, label=label, value=value, min=min_value, max=max_value)
        self.elements[key] = self._wrap_with_button(key, numeric_input)
        self.info_keys.append(f"{key}_info")

    def add_checkbox(self, key: str, label: str, value: bool = False) -> None:
        checkbox = ui.input_checkbox(key, label, value)
        self.elements[key] = self._wrap_with_button(key, checkbox)
        self.info_keys.append(f"{key}_info")

    def add_radio_buttons(self, key: str, label: str, choices: list[str], selected: str = None) -> None:
        radio_buttons = ui.input_radio_buttons(id=key, label=label, choices=choices, selected=selected)
        self.elements[key] = self._wrap_with_button(key, radio_buttons)
        self.info_keys.append(f"{key}_info")

    def add_select_input(self, key: str, label: str, choices: list[str], selected: str = None) -> None:
        select_input = ui.input_select(id=key, label=label, choices=choices, selected=selected)
        self.elements[key] = self._wrap_with_button(key, select_input)
        self.info_keys.append(f"{key}_info")

    def add_text_area(self, key: str, label: str, value: str, rows: int = 3, cols: int = 40) -> None:
        text_area = ui.input_text_area(id=key, label=label, value=value, rows=rows, cols=cols)
        self.elements[key] = self._wrap_with_button(key, text_area)
        self.info_keys.append(f"{key}_info")

    def add_date_input(self, key: str, label: str, value: str) -> None:
        date_input = ui.input_date(id=key, label=label, value=value)
        self.elements[key] = self._wrap_with_button(key, date_input)
        self.info_keys.append(f"{key}_info")

    def add_input_switch(self, key: str, label: str, value: bool = False) -> None:
        input_switch = ui.input_switch(id=key, label=label, value=value)
        self.elements[key] = self._wrap_with_button(key, input_switch)
        self.info_keys.append(f"{key}_info")

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
            style=style + "margin: 10px 20px 0px 20px"
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


def wrap_plot(name: str, body: HTMLBody) -> HTMLBody:
    return ui.div(
        ui.h5(name),
        body,
        class_="col"
    )


def basic_plot_rank_layout() -> HTMLBody:
    html_plot_list: List[HTMLBody] = [
        wrap_plot("Rank Abundance Curve for Abundance Model", output_widget(f"tool1_plot_abundance_curve")),
        wrap_plot("Rank Abundance Curve for Incidence Model", output_widget("tool1_plot_incidence_curve")),
    ]

    grid_layout: List[HTMLBody] = []
    for i in range(0, len(html_plot_list), 2):
        row: HTMLBody = ui.div(
            html_plot_list[i:i + 2],
            class_="row",
        )
        grid_layout.append(row)
    return ui.div(grid_layout)


def basic_plot_profile_layout(
        for_variant: Literal["1-gram", "2-gram", "3-gram", "4-gram", "5-gram", "trace_variants"]) -> HTMLBody:
    html_plot_list: List[HTMLBody] = [
        wrap_plot("Diversity Profile for Abundance Model", output_widget(f"tool1_plot_1")),
        wrap_plot("Diversity Profile for Incidence Model", output_widget("tool1_plot_2")),
        wrap_plot("Sample Diversity for Abundance Model", output_widget("tool1_plot_3")),
        wrap_plot("Sample Diversity for Incidence Model", output_widget("tool1_plot_4")),
        wrap_plot("Completeness & Coverage for Abundance Model", output_widget("tool1_plot_5")),
        wrap_plot("Completeness & Coverage for Incidence Model", output_widget("tool1_plot_6")),
        wrap_plot("Expected Sampling Effort for Abundance Model", output_widget("tool1_plot_7")),
        wrap_plot("Expected Sampling Effort for Incidence Model", output_widget("tool1_plot_8"))
    ]

    # html_plot_list = [x for xs in html_plot_list for x in xs]

    grid_layout: List[HTMLBody] = []
    for i in range(0, len(html_plot_list), 2):
        row: HTMLBody = ui.div(
            html_plot_list[i:i + 2],
            class_="row",
        )
        grid_layout.append(row)

    grid_layout.insert( 0, ui.h3("Diversity Profiles"))
    grid_layout.insert( 3, ui.h3("Completeness Profiles"))
    return ui.div(grid_layout)


def build_species_table(storage: StorageManager) -> pd.DataFrame:
    """
    Build a DataFrame to display species metrics in the required format.

    Abundance:
    D0: speciesEstimator.metrics["abundance_estimate_d0"][-1]
    D1: speciesEstimator.metrics["abundance_estimate_d1"][-1]
    D2: speciesEstimator.metrics["abundance_estimate_d2"][-1]

    C0: speciesEstimator.metrics["abundance_c0"][-1]
    C1: speciesEstimator.metrics["abundance_c1"][-1]

    Incidence:
    D0: speciesEstimator.metrics["incidence_estimate_d0"][-1]
    D1: speciesEstimator.metrics["incidence_estimate_d1"][-1]
    D2: speciesEstimator.metrics["incidence_estimate_d2"][-1]

    C0: speciesEstimator.metrics["incidence_c0"][-1]
    C1: speciesEstimator.metrics["incidence_c1"][-1]

    :return: pd.DataFrame
    """
    # Abundance
    d0_a = storage.get_value_by_metric("abundance_estimate_d0").iloc[-1]
    d1_a = storage.get_value_by_metric("abundance_estimate_d1").iloc[-1]
    d2_a = storage.get_value_by_metric("abundance_estimate_d2").iloc[-1]
    c0_a = storage.get_value_by_metric("abundance_c0").iloc[-1]
    c1_a = storage.get_value_by_metric("abundance_c1").iloc[-1]

    # Incidence
    d0_i = storage.get_value_by_metric("incidence_estimate_d0").iloc[-1]
    d1_i = storage.get_value_by_metric("incidence_estimate_d1").iloc[-1]
    d2_i = storage.get_value_by_metric("incidence_estimate_d2").iloc[-1]
    c0_i = storage.get_value_by_metric("incidence_c0").iloc[-1]
    c1_i = storage.get_value_by_metric("incidence_c1").iloc[-1]

    # Constructing the DataFrame
    data = {
        "°": ["D0", "D1", "D2", "C0", "C1"],
        "Abundance Model": [d0_a, d1_a, d2_a, c0_a, c1_a],
        "Incidence Model": [d0_i, d1_i, d2_i, c0_i, c1_i]
    }

    result = pd.DataFrame(data)

    return result
