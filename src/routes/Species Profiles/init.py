from typing import Any, List, Sequence, Literal

import faicons
from htmltools import Tag
from shiny import ui
from shiny.types import NavSetArg
from shiny.ui import CardItem
from shiny.ui._navs import NavSetCard, NavPanel, NavSet

from src.layouts.layout_definition import SimpleLayout, SidebarOptions, BaseLogicView, BasicCardItem
from src.utils.base_tab import BaseTab
from src.utils.constants import HTMLBody, RETRIVAL_MAP
from src.utils.functions import center, text_bold, row, text_icon, wrapped_div_to_container


class Tab1(BaseTab):

    def __init__(self) -> None:
        super().__init__()

    def init_component(self) -> HTMLBody:
        return self._create_layout()

    def _create_layout(self) -> HTMLBody:
        nav_set_class_ref: NavSet = ui.navset_tab(
            ui.nav_panel("1-gram"),
            ui.nav_panel("2-gram"),
            ui.nav_panel("3-gram"),
            ui.nav_panel("4-gram"),
            ui.nav_panel("5-gram"),
            ui.nav_panel("Trace Variants", value="trace_variants"),
            id="tool1_nav_set",
        )
        # nav_set_class_ref.ul_class = "ul-for-species"

        return ui.div(
            ui.div(nav_set_class_ref, style=""),
            self.build_main_ui_content(),
        )

    def build_main_ui_content(self) -> HTMLBody:
        logic_view = BaseLogicView("Updated Results", [
            BasicCardItem("Number Traces", text_icon("tool1_event_log_length", "ellipsis")),
            BasicCardItem("Mean Length", text_icon("tool1_event_log_avg_trace_length", "calculator")),
            BasicCardItem("Degree of Spatial Aggregation", text_icon("tool1_degree_of_aggregation", "chart-bar")),
            # BasicCardItem("Rank Abundance Curve for Abundance Model", text_icon("tool1_rank_abundance", "chart-bar")),
            # BasicCardItem("Rank Abundance Curve for Incidence Model", text_icon("tool1_rank_incidence", "chart-bar")),
        ], ui.div(
            # center(
            #     row(
            #         ui.input_switch("tool1_set_grid_mode", "Grid?"),
            #         ui.download_button("tool1_download_pdf", "Download PDF", icon=faicons.icon_svg("download"),
            #                            style="margin-left: 10px;")
            #     )
            # ),

            wrapped_div_to_container(ui.output_ui("tool1_plot_view_ranks"), title="Rank"),
            wrapped_div_to_container(ui.div(
                ui.output_data_frame("tool1_plot_view_species_table"),
                style="display: flex; justify-content: center; align-items: center; padding: 10px;",
            ), title="Species Table"),
            wrapped_div_to_container(ui.output_ui("tool1_plot_view_profiles"), title="Profiles"),
        ))

        self.component: CardItem = logic_view.apply()
        self.component.id = __name__
        self.component.style = self.STYLE
        return self.component

    def on_rerender(self) -> None:
        pass
