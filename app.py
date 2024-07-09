from typing import List, Any, Dict, Union, Tuple, Optional, Literal, Callable

import faicons
import pandas as pd
import plotly.graph_objects as go
import pm4py
from htmltools import Tag
from shiny import App, ui, render, Inputs, Outputs, Session, reactive, run_app
from shiny.types import NavSetArg, FileInfo
from shinywidgets import render_plotly

from special.estimation import species_estimator
from special.visualization.visualization import plot_expected_sampling_effort, plot_completeness_profile, \
    plot_diversity_profile, plot_diversity_series_all, plot_diversity_series, plot_diversity_sample_vs_estimate, \
    plot_rank_abundance
from src import shared
from src.layouts.layout_definition import NoFileLayout, basic_plot_profile_layout, basic_plot_rank_layout, \
    build_species_table
from src.shared import app_dir
from src.utils.base_tab import BaseTab
from src.utils.constants import HTMLBody, RETRIVAL_MAP, INFO_BUTTON_TEXT
from src.utils.functions import load_tabs

loaded_tabs: List[tuple[str, BaseTab]] = load_tabs()


def refresh_log_profile_cache(species_retrival: str) -> None:
    """
    Refresh the log profile cache
    :param species_retrival:
    :return:
    """

    if shared.LOG_PROFILE_CACHE.exists(species_retrival):
        return

    step_size = int(len(shared.EVENT_LOG_REF) / 200)
    estimator = species_estimator.SpeciesEstimator(d0=True, d1=True, d2=True, c0=True, c1=True, step_size=step_size)
    estimator.register(species_retrival, RETRIVAL_MAP[species_retrival])

    estimator.apply(shared.EVENT_LOG_REF)
    df = estimator.to_dataFrame()
    shared.LOG_PROFILE_CACHE.add(df)
    shared.ESTIMATOR_REFERENCE = estimator


def _decorator(name: str, ui_body: HTMLBody) -> Any:
    return ui.div(
        ui.panel_title(name), ui_body, class_="special-main-panel"
    )


def generate_nav_controls(tabs: List[tuple[str, BaseTab]], nfl: HTMLBody = None) -> List[NavSetArg]:
    results: List[NavSetArg] = []

    for i, tab in enumerate(tabs):
        if nfl:
            results.append(
                ui.nav_panel(
                    tab[0],
                    _decorator(tab[0], nfl if i == 0 else None),
                    icon=tab[1].ICON,
                )
            )
        else:
            results.append(
                ui.nav_panel(
                    tab[0],
                    _decorator(tab[0], tab[1].init_component()),
                    icon=tab[1].ICON,
                )
            )
    return results


def create_app_ui_navbar(nfl: HTMLBody = None) -> Tag:
    return ui.page_navbar(
        *generate_nav_controls(loaded_tabs, nfl=nfl),

    )


app_ui: Tag = ui.page_fluid(
    ui.head_content(
        ui.tags.link(
            rel="stylesheet",
            href="https://cdn.jsdelivr.net/npm/bootstrap@3.4.1/dist/css/bootstrap.min.css",
            integrity="sha384-HSMxcRTRxnN+Bdg0JdbxYKrThecOKuH5zCYotlSAcp1+c8xmyTe9GYg1l9a69psu",
            crossorigin="anonymous"
        )
    ),
    ui.output_ui("basic_layout"),
    ui.include_css(app_dir / "styles.css", method="link_files"),
    class_="overall-page"
)




def server(input: Inputs, output: Outputs, session: Session) -> None:
    file_uploaded = reactive.Value(False)
    refresh_plots = reactive.Value(False)
    current_retrival_function = reactive.Value[
        Literal["1-gram", "2-gram", "3-gram", "4-gram", "5-gram", "trace_variants"]
    ]("1-gram")

    # ############################
    # RENDER UI
    # ############################
    @output
    @render.ui
    def basic_layout() -> Tag:
        if file_uploaded():
            return create_app_ui_navbar()
        else:
            nfl: NoFileLayout = NoFileLayout()
            return create_app_ui_navbar(nfl.apply())

    @output
    @render.ui
    def tool1_plot_view_profiles() -> Tag:
        layout: HTMLBody = basic_plot_profile_layout(current_retrival_function.get())
        return layout

    @output
    @render.data_frame
    def tool1_plot_view_species_table() -> pd.DataFrame:
        return build_species_table(shared.LOG_PROFILE_CACHE)

    @output
    @render.ui
    def tool1_plot_view_ranks() -> Tag:
        return basic_plot_rank_layout()

    # ############################
    # EVENT HANDLERS
    # ############################
    @reactive.Effect
    @reactive.event(input.file_upload)
    def handle_file_upload() -> None:
        file_infos: List[FileInfo] = input.file_upload()
        if file_infos:
            file_info: FileInfo = file_infos[0]
            file_path: str = file_info["datapath"]
            shared.FILE_SELECTED = True

            shared.EVENT_LOG_REF = pm4py.read_xes(file_path)

            refresh_log_profile_cache("1-gram")

            file_uploaded.set(True)
        else:
            shared.FILE_SELECTED = False
            file_uploaded.set(False)

    @reactive.Effect
    def update_tab():
        print("Updating tab", input.tool1_nav_set())
        refresh_log_profile_cache(input.tool1_nav_set())
        current_retrival_function.set(input.tool1_nav_set())

    # ############################
    # RENDER TEXT
    # ############################
    @render.text
    def tool1_event_log_length() -> str:
        return f"{len(shared.EVENT_LOG_REF) if not shared.EVENT_LOG_REF.empty else 'MISSING'}"

    @render.text
    def tool1_degree_of_aggregation() -> str:
        values: pd.Series = shared.LOG_PROFILE_CACHE.get_value_by_metric("degree_of_aggregation")
        return str(round(values.mean(), 3) if not values.empty else "MISSING")

    @render.text
    def tool1_event_log_avg_trace_length() -> str:
        df: pd.DataFrame = shared.EVENT_LOG_REF
        return f"{round(df.groupby('case:concept:name').size().mean(), 3) if not shared.EVENT_LOG_REF.empty else 'MISSING'}"

    @render.text
    def tool1_rank_abundance() -> str:
        values: pd.Series = shared.LOG_PROFILE_CACHE.get_value_by_metric("rank_abundance")
        return str(round(values.mean(), 3) if not values.empty else "MISSING")

    @render.text
    def tool1_rank_incidence() -> str:
        values: pd.Series = shared.LOG_PROFILE_CACHE.get_value_by_metric("degree_of_aggregation")
        return str(round(values.mean(), 3) if not values.empty else "MISSING")

    # ############################
    # RENDER PLOTS
    # ############################
    @render_plotly
    def tool1_plot_1():  #

        key: str = current_retrival_function.get()
        return plot_diversity_profile(shared.ESTIMATOR_REFERENCE, key,
                                      "", True)

    @render_plotly
    def tool1_plot_2():
        key: str = current_retrival_function.get()
        return plot_diversity_profile(shared.ESTIMATOR_REFERENCE, key,
                                      "", False)

    @render_plotly
    def tool1_plot_3():
        key: str = current_retrival_function.get()
        return plot_diversity_series_all(shared.ESTIMATOR_REFERENCE, key,
                                         ["d0", "d1", "d2", "c1", "c0"], "",
                                         True)

    @render_plotly
    def tool1_plot_4():
        key: str = current_retrival_function.get()
        return plot_diversity_series_all(shared.ESTIMATOR_REFERENCE, key,
                                         ["d0", "d1", "d2", "c1", "c0"], "",
                                         False)

    @render_plotly
    def tool1_plot_5():
        key: str = current_retrival_function.get()
        return plot_completeness_profile(shared.ESTIMATOR_REFERENCE, key,
                                         "", True)

    @render_plotly
    def tool1_plot_6():
        key: str = current_retrival_function.get()
        return plot_completeness_profile(shared.ESTIMATOR_REFERENCE, key,
                                         "", False)

    @render_plotly
    def tool1_plot_7():
        key: str = current_retrival_function.get()
        return plot_expected_sampling_effort(shared.ESTIMATOR_REFERENCE, key,
                                             "", True)

    @render_plotly
    def tool1_plot_8():
        key: str = current_retrival_function.get()
        return plot_expected_sampling_effort(shared.ESTIMATOR_REFERENCE, key,
                                             "", False)

    @render_plotly
    def tool1_plot_abundance_curve():
        key: str = current_retrival_function.get()
        return plot_rank_abundance(shared.ESTIMATOR_REFERENCE, key, "", True)

    @render_plotly
    def tool1_plot_incidence_curve():
        key: str = current_retrival_function.get()
        return plot_rank_abundance(shared.ESTIMATOR_REFERENCE, key, "", False)

    def show_modal(content: HTMLBody):
        m = ui.modal(
            ui.hr(style="margin: 0; padding:0;"),
            ui.div(
                content,
                ui.p("", style="min-height: 150px;"),
                ui.img(src="bird.png", alt="Placeholder image",
                       style="position: absolute; bottom: 0; left: 0; opacity: 0.5; width: 100px;"),

                ui.img(src="glasses.png", alt="Placeholder image",
                       style="position: absolute; bottom: 0; right: 0; opacity: 0.5; width: 150px;"),
                style="position: relative; height: 100%; width: 100%;"
            ),
            title=f"INFO",
            easy_close=True,
            footer=None,
            size="l"
        )
        ui.modal_show(m)

    for button_id, key in INFO_BUTTON_TEXT.items():
        @reactive.effect
        @reactive.event(getattr(input, button_id))
        def handle_click(b_id=button_id, k=key):
            show_modal(k)


app: App = App(app_ui, server, static_assets=app_dir / "www")
