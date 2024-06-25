import os
import importlib.util
from functools import partial
from typing import List, Any, Dict, Callable, Union
import matplotlib.pyplot as plt
import numpy as np

import pandas as pd
import pm4py
from htmltools import Tag
from shiny import App, ui, render, Inputs, Outputs, Session, reactive
from shiny.types import NavSetArg, FileInfo

from SpeciAL.estimation import species_estimator, species_retrieval
from SpeciAL.estimation.species_estimator import SpeciesEstimator
from src import shared
from src.layouts.layout_definition import NoFileLayout, basic_plot_layout
from src.shared import app_dir
from src.utils.base_tab import BaseTab
from src.utils.constants import HTMLBody, ESTIMATOR_MAP
from src.utils.functions import load_tabs

plt.ioff()
loaded_tabs: List[tuple[str, BaseTab]] = load_tabs()


def refresh_log_profile_cache(select_retrival_value: str):
    estimator: SpeciesEstimator = ESTIMATOR_MAP[select_retrival_value]

    if shared.EVENT_LOG_REF is not None:
        estimator.profile_log(shared.EVENT_LOG_REF)

    # if shared.LOG_PROFILE_CACHE:
    #     shared.LOG_PROFILE_CACHE.clear()

    shared.LOG_PROFILE_CACHE = estimator.metric_manager.get_metrics()


def _decorator(name: str, ui_body: HTMLBody) -> Any:
    return ui.div(
        ui.panel_title(name), ui_body
    )


def generate_nav_controls(tabs: List[tuple[str, BaseTab]], simple: bool) -> List[NavSetArg]:
    results: List[NavSetArg] = []
    for tab in tabs:
        if simple:
            results.append(ui.nav_panel(tab[0]))
        else:
            results.append(ui.nav_panel(tab[0], _decorator(tab[0], tab[1].init_component())))
    return results


def create_app_ui_navbar(simple: bool) -> Tag:
    return ui.page_navbar(
        *generate_nav_controls(loaded_tabs, simple=simple),
    )


app_ui: Tag = ui.page_fluid(
    ui.output_ui("basic_layout"),
    ui.include_css(app_dir / "styles.css", method="link_files"),
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
            return create_app_ui_navbar(False)
        else:
            nfl: NoFileLayout = NoFileLayout()
            return ui.div(
                create_app_ui_navbar(True),
                nfl.apply()
            )

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
        # refresh_plots.set(True)

    @reactive.Effect
    @reactive.event(input.tool1_step_size)
    def tool1_step_size() -> None:
        size: int = int(input.tool1_step_size())
        shared.DEFAULT_SET_SIZE = size
        print(f"Step size: {size}")
        refresh_log_profile_cache("1-gram")
        refresh_plots.set(True)

    # ############################
    # RENDER TEXT
    # ############################
    @render.text
    def tool1_event_log_length() -> str:
        return f"{len(shared.EVENT_LOG_REF) if not shared.EVENT_LOG_REF.empty else 'MISSING'}"

    @render.text
    def tool1_event_log_avg_trace_length() -> str:
        df: pd.DataFrame = shared.EVENT_LOG_REF
        return f"{round(df.groupby('case:concept:name').size().mean(), 3) if not shared.EVENT_LOG_REF.empty else 'MISSING'}"

    # ############################
    # RENDER PLOTS
    # ############################

    @render.plot
    def tool1_d0_plot():
        if refresh_plots():
            print("Refreshing plots d0")
        key: str = input.tool1_select_retrival()
        plot_data: Dict[str, List[Union[int, float]]] = get_array_from_key(shared.LOG_PROFILE_CACHE, "d0")
        return basic_plot_function(plot_data, "Species Richness Plot")

    @render.plot
    def tool1_d1_plot():
        if refresh_plots():
            print("Refreshing plots d1")
        key: str = input.tool1_select_retrival()
        plot_data: Dict[str, List[Union[int, float]]] = get_array_from_key(shared.LOG_PROFILE_CACHE, "d1")
        return basic_plot_function(plot_data, "Exponential Shannon Entropy Plot")

    @render.plot
    def tool1_d2_plot():
        if refresh_plots():
            print("Refreshing plots d2")
        key: str = input.tool1_select_retrival()
        plot_data: Dict[str, List[Union[int, float]]] = get_array_from_key(shared.LOG_PROFILE_CACHE, "d2")
        return basic_plot_function(plot_data, "Simpson Diversity Index Plot")

    @render.plot
    def tool1_c0_plot():
        if refresh_plots():
            print("Refreshing plots c0")
        key: str = input.tool1_select_retrival()
        plot_data: Dict[str, List[Union[int, float]]] = get_array_from_key(shared.LOG_PROFILE_CACHE, "c0")
        return basic_plot_function(plot_data, "Completeness Plot")

    @render.plot
    def tool1_c1_plot():
        if refresh_plots():
            print("Refreshing plots c1")
        key: str = input.tool1_select_retrival()
        plot_data: Dict[str, List[Union[int, float]]] = get_array_from_key(shared.LOG_PROFILE_CACHE, "c1")
        return basic_plot_function(plot_data, "Coverage Plot")


def basic_plot_function(plot_data: Dict[str, List[Union[int, float]]], title: str) -> plt.Figure:
    if shared.LOG_PROFILE_CACHE is None:
        return None

    fig, ax = plt.subplots(figsize=(12, 6))

    for sub_key, values in plot_data.items():
        ax.plot(values, label=sub_key)

    ax.set_title(title)
    ax.set_xlabel("Index")
    ax.set_ylabel("Value")
    ax.legend()
    ax.grid(True)

    return fig


app: App = App(app_ui, server)
