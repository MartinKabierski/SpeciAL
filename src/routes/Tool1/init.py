from typing import Any

import faicons
from htmltools import Tag
from shiny import ui
from shiny.ui import CardItem
from src.layouts.layout_definition import SimpleLayout, SidebarOptions, BaseLogicView, BasicCardItem
from src.utils.base_tab import BaseTab
from src.utils.constants import HTMLBody
from src.utils.functions import center, text_bold, row, text_icon


class Tab1(BaseTab):
    def __init__(self) -> None:
        super().__init__()

    def init_component(self) -> HTMLBody:
        return self._create_layout()

    def _create_layout(self) -> HTMLBody:
        sidebar: SidebarOptions = SidebarOptions()
        sidebar.add_section("header1", "Settings")

        sidebar.add_select_input("tool1_select_retrival", "Species Retrieval Functions",
                                 [
                                            "1-gram",
                                            "2-gram",
                                            "3-gram",
                                            "4-gram",
                                            "5-gram",
                                            "trace_variants",
                                            "2-gram_complete_log",
                                            "2-gram_all_metrics",
                                        ],
                                 selected="1-gram")

        sidebar.add_subsection("diversity_indices", "Diversity Indices")
        sidebar.add_checkbox("tool1_d0", "Species Richness (D0)", True)
        sidebar.add_checkbox("tool1_d1", "Exponential Shannon Entropy (D1)", False)
        sidebar.add_checkbox("tool1_d2", "Simpson Diversity Index (D2)", False)

        sidebar.add_subsection("completeness_coverage", "Completeness & Coverage")
        sidebar.add_checkbox("tool1_c0", "Completeness (C0)", False)
        sidebar.add_checkbox("tool1_c1", "Coverage (C1)", False)

        # sidebar.add_section("completeness_values", "Desired Completeness Values")
        # for i, value in enumerate(self.l_n):
        #     sidebar.add_numeric_input(f"l_n_{i}", f"Completeness Value {i + 1}", value, min_value=0.0, max_value=1.0)

        sidebar.add_subsection("step_size", "Step Size")
        sidebar.add_slider("tool1_step_size", "Number of added traces", min_value=0, max_value=1000, value=100)

        logic_view = BaseLogicView("Updated Results", [
            BasicCardItem("Event Log Length", text_icon("tool1_event_log_length", "ellipsis")),
            BasicCardItem("Average Trace Length", text_icon("tool1_event_log_avg_trace_length", "calculator")),
            BasicCardItem("Degree of Spatial Aggregation", text_icon("tool1_degree_of_aggregation", "chart-bar")),
            BasicCardItem("Interesting Metric 1", "Some Content"),
            BasicCardItem("Interesting Metric 1", "Some Content"),
        ], ui.div(
            center(
                row(
                    ui.input_switch("tool1_set_grid_mode", "Grid?"),
                    ui.download_button("tool1_download_pdf","Download PDF", icon=faicons.icon_svg("download"), style="margin-left: 10px;")
                )
            ),
            ui.output_ui("tool1_plot_view")
        )
        )

        content = logic_view.apply()
        simple_layout = SimpleLayout(content, sidebar.apply())
        self.component: CardItem = simple_layout.apply()
        self.component.id = __name__
        self.component.style = self.STYLE
        self.component.script = "() => {console.log('Script executed')}"
        self.component.class_ = "MAIN_COMPONENT"
        return self.component

    def on_rerender(self) -> None:
        pass
