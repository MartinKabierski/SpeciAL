from typing import List, Any, Dict, Union, Tuple, Optional

import pandas as pd
import plotly.graph_objects as go
import pm4py
from htmltools import Tag
from shiny import App, ui, render, Inputs, Outputs, Session, reactive
from shiny.types import NavSetArg, FileInfo
from shinywidgets import render_plotly

from special.estimation import species_estimator
from src import shared
from src.layouts.layout_definition import NoFileLayout, basic_plot_layout
from src.shared import app_dir
from src.utils.base_tab import BaseTab
from src.utils.constants import HTMLBody, RETRIVAL_MAP
from src.utils.functions import load_tabs

loaded_tabs: List[tuple[str, BaseTab]] = load_tabs()


def refresh_log_profile_cache(species_retrival: str, d0=True, d1=True, d2=True, c0=True, c1=True,
                              step_size=100) -> None:
    if shared.LOG_PROFILE_CACHE.exists(species_retrival):
        return

    estimator = species_estimator.SpeciesEstimator(d0=d0, d1=d1, d2=d2, c0=c0, c1=c1, step_size=step_size)
    estimator.register(species_retrival, RETRIVAL_MAP[species_retrival])

    estimator.apply(shared.EVENT_LOG_REF)
    df = estimator.to_dataFrame()
    shared.LOG_PROFILE_CACHE.add(df)


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
    ui.output_ui("basic_layout"),
    ui.include_css(app_dir / "styles.css", method="link_files"),
    class_="overall-page"
)


def get_array_from_key(
        data: Dict[str, Dict[str, Union[List[Union[int, float]], List[float]]]], key: str) \
        -> dict[str, list[int | float]]:
    return data.get(key, {})


def server(input: Inputs, output: Outputs, session: Session) -> None:
    file_uploaded = reactive.Value(False)
    refresh_plots = reactive.Value(False)

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
    def tool1_plot_view() -> Tag:
        return basic_plot_layout(
            input.tool1_d0(),
            input.tool1_d1(),
            input.tool1_d2(),
            input.tool1_c0(),
            input.tool1_c1(),
            False,
            input.tool1_set_grid_mode()
        )

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
    @reactive.event(input.tool1_select_retrival)
    def tool1_select_retrival() -> None:
        select_retrival_value: str = input.tool1_select_retrival()
        print(f"Select retrival: {select_retrival_value}")
        refresh_log_profile_cache(select_retrival_value)

    @render.download(filename="report.pdf")
    def tool1_download_pdf():
        plot_layout: Tag = basic_plot_layout(
            True, True, True, True, True, True, True
        )

        # html_str: str = plot_layout.get_html_string()
        # print(html_str)
        # pdf: bytes = convert_html_to_pdf(html_str)
        # print(pdf)
        # yield pdf

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

    # ############################
    # RENDER PLOTS
    # ############################

    @render_plotly
    def tool1_d0_plot():
        if refresh_plots():
            print("Refreshing plots d0")
        key: str = input.tool1_select_retrival()
        plot_data: Dict[str, List[Union[int, float]]] = shared.LOG_PROFILE_CACHE.filter_for_metric(key, "d0")
        return basic_plot_function(plot_data, "Species Richness Plot")

    @render_plotly
    def tool1_d1_plot():
        if refresh_plots():
            print("Refreshing plots d1")
        key: str = input.tool1_select_retrival()
        plot_data: Dict[str, List[Union[int, float]]] = shared.LOG_PROFILE_CACHE.filter_for_metric(key, "d1")
        return basic_plot_function(plot_data, "Exponential Shannon Entropy Plot")

    @render_plotly
    def tool1_d2_plot():
        if refresh_plots():
            print("Refreshing plots d2")
        key: str = input.tool1_select_retrival()
        plot_data: Dict[str, List[Union[int, float]]] = shared.LOG_PROFILE_CACHE.filter_for_metric(key, "d2")
        return basic_plot_function(plot_data, "Simpson Diversity Index Plot")

    @render_plotly
    def tool1_c0_plot():
        if refresh_plots():
            print("Refreshing plots c0")
        key: str = input.tool1_select_retrival()
        plot_data: Dict[str, List[Union[int, float]]] = shared.LOG_PROFILE_CACHE.filter_for_metric(key, "c0")
        return basic_plot_function(plot_data, "Completeness Plot", (
            ["abundance_sample"],
            ["incidence_sample"]
        ))

    @render_plotly
    def tool1_c1_plot():
        if refresh_plots():
            print("Refreshing plots c1")
        key: str = input.tool1_select_retrival()
        plot_data: Dict[str, List[Union[int, float]]] = shared.LOG_PROFILE_CACHE.filter_for_metric(key, "c1")
        return basic_plot_function(plot_data, "Coverage Plot", (
            ["abundance_sample"],
            ["incidence_sample"]
        ))


def basic_plot_function(
        plot_data: Dict[str, List[Union[int, float]]],
        title: str,
        chart_group: Tuple[List[str], List[str]] = (
                ["abundance_sample", "abundance_estimate"],
                ["incidence_sample", "incidence_estimate"]
        )
) -> go.Figure:
    plot_data = {k: v for k, v in plot_data.items() if v}
    df: pd.DataFrame = pd.DataFrame(plot_data)
    trace1: List[go.Scatter] = []
    for key in chart_group[0]:
        s: go.Scatter = go.Scatter(
            x=df.index,
            y=df[key],
            mode='lines',
            name='Abundance Sample' if key == 'abundance_sample' else 'Abundance Estimate',
            yaxis='y1'
        )
        trace1.append(s)

    trace2: List[go.Scatter] = []

    for key in chart_group[1]:
        s: go.Scatter = go.Scatter(
            x=df.index,
            y=df[key],
            mode='lines',
            name='Incidence Sample' if key == 'incidence_sample' else 'Incidence Estimate',
            yaxis='y2'
        )
        trace2.append(s)

    layout = go.Layout(
        title=title,
        xaxis=dict(
            title='Sample Size'
        ),
        yaxis=dict(
            title='Abundance',
            side='left'
        ),
        yaxis2=dict(
            title='Incidence',
            side='right',
            overlaying='y'
        ),
        template="simple_white",
    )

    fig = go.Figure(data=trace1 + trace2, layout=layout)

    return fig


app: App = App(app_ui, server)
