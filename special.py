from functools import partial

import pandas as pd
import pm4py
import shinyswatch
from cachetools import cached
from shiny import App, render, ui, run_app, reactive
from shiny.types import FileInfo
from shinyswatch.theme import darkly, minty, quartz

from process_completeness_estimation.estimation import species_estimator, species_retrieval

app_ui = ui.page_fluid(
    shinyswatch.theme.minty(),
    ui.panel_title("SpeciAL - Species-based Analysis of Event Logs"),
    #ui.input_slider("n", "N", 0, 100, 20),
    ui.input_file(id="log", label="Upload a .xes file", accept=".xes"),
    ui.input_action_button("button", "Profile Log"),
    ui.output_data_frame("species_data"),
    ui.output_data_frame("species_data2"),
    ui.output_data_frame("species_data3"),
    ui.output_data_frame("species_data4"),
    ui.output_data_frame("species_data5"),
    ui.output_data_frame("species_data_tv")

)


def server(input, output, session):

    #TODO have this be done once upon upload
    def parse_log_file():
        print("log file parsing")

        file: list[FileInfo] | None = input.log()
        if file is None:
            return None
        return pm4py.read_xes(file[0]["datapath"])

    #TODO have this update all views?
    @reactive.event(input.button)
    def get_log_profiles():
        return estimate_species(parse_log_file())

    #TODO have this update only one view if it is wanted
    @render.data_frame
    def species_data():
        log = get_log_profiles()
        if log is None:
            return pd.DataFrame()
        print("estimating")
        return log["1-gram"].to_dataFrame()

    @render.data_frame
    def species_data2():
        log = get_log_profiles()
        if log is None:
            return pd.DataFrame()
        print("estimating")
        return log["2-gram"].to_dataFrame()

    @render.data_frame
    def species_data3():
        log = get_log_profiles()
        if log is None:
            return pd.DataFrame()
        print("estimating")
        return log["3-gram"].to_dataFrame()

    @render.data_frame
    def species_data4():
        log = get_log_profiles()
        if log is None:
            return pd.DataFrame()
        print("estimating")
        return log["4-gram"].to_dataFrame()

    @render.data_frame
    def species_data5():
        log = get_log_profiles()
        if log is None:
            return pd.DataFrame()
        print("estimating")
        return log["5-gram"].to_dataFrame()

    @render.data_frame
    def species_data_tv():
        log = get_log_profiles()
        if log is None:
            return pd.DataFrame()
        print("estimating")
        return log["trace_variants"].to_dataFrame()


def estimate_species(log):
    estimators = \
        {
            # Different Species Retrieval Functions, metrics are updated each 100 traces
            "1-gram": species_estimator.SpeciesEstimator(partial(species_retrieval.retrieve_species_n_gram, n=1), d1=True, d2=True),
            "2-gram": species_estimator.SpeciesEstimator(partial(species_retrieval.retrieve_species_n_gram, n=2), d1=True, d2=True),
            "3-gram": species_estimator.SpeciesEstimator(partial(species_retrieval.retrieve_species_n_gram, n=3), d1=True, d2=True),
            "4-gram": species_estimator.SpeciesEstimator(partial(species_retrieval.retrieve_species_n_gram, n=4), d1=True, d2=True),
            "5-gram": species_estimator.SpeciesEstimator(partial(species_retrieval.retrieve_species_n_gram, n=5), d1=True, d2=True),
            "trace_variants": species_estimator.SpeciesEstimator(species_retrieval.retrieve_species_trace_variant,d1=True, d2=True)
        }
    for est in estimators.values():
        est.profile_log(log)

    return estimators


app = App(app_ui, server)

run_app(app)
