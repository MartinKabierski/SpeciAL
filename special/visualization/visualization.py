from enum import Enum
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
from plotly.subplots import make_subplots
from special.estimation.species_estimator import SpeciesEstimator
import plotly.graph_objects as go

LAYOUT_TEMPLATE = "simple_white"
FILL_COLOR = 'rgba(0,100,80,0.2)'
LINE_COLOR = 'rgb(0,100,80)'
MARKER_COLOR = 'grey'
MARKER_SIZE = 10


RANK_ABUNDANCE_LAYOUT = go.Layout(
    xaxis=dict(title='Species Rank'),
    yaxis=dict(title='Occurrences'),
    template=LAYOUT_TEMPLATE,
    autosize=True,
)

DIVERSITY_LAYOUT = go.Layout(
    autosize=True,
    template=LAYOUT_TEMPLATE,
    showlegend=True,
)

DIVERSITY_PROFILE_LAYOUT = go.Layout(
    xaxis=dict(title='Order q'),
    yaxis=dict(title='Diversity'),
    template=LAYOUT_TEMPLATE,
    autosize=True
)

COMPLETENESS_PROFILE_LAYOUT = go.Layout(
    xaxis=dict(title='Sample Size'),
    yaxis=dict(title='Value'),
    template=LAYOUT_TEMPLATE,
    autosize=True
)

EXPECTED_SAMPLING_EFFORT_LAYOUT = go.Layout(
    xaxis=dict(title='Sample Size'),
    yaxis=dict(title='Effort'),
    template=LAYOUT_TEMPLATE,
    autosize=True
)


def plot_rank_abundance(estimator: SpeciesEstimator, species_id: str, file_name: str, abundance: bool) -> go.Figure:
    reference_sample = estimator.metrics[species_id].reference_sample_abundance if abundance \
        else estimator.metrics[species_id].reference_sample_incidence
    reference_values_sorted = sorted(list(reference_sample.values()), reverse=True)
    no_species = len(reference_sample)

    trace1 = go.Scatter(
        x=list(range(1, no_species + 1)),
        y=reference_values_sorted,
        mode='lines',
        fill='tozeroy',
        fillcolor=FILL_COLOR,
        line=dict(color=LINE_COLOR)
    )

    fig = go.Figure(data=[trace1], layout=RANK_ABUNDANCE_LAYOUT)

    return fig


def plot_diversity_sample_vs_estimate(estimator: SpeciesEstimator, species_id: str, metrics: list[str], file_name: str,
                                      abundance: bool) -> go.Figure:
    fig = make_subplots(rows=1, cols=3, shared_yaxes=True, subplot_titles=("D0", "D1", "D2"))

    for i, (metric, title) in enumerate(zip(metrics, ("D0", "D1", "D2")), start=1):
        key_sample = "abundance_sample_" + metric if abundance else "incidence_sample_" + metric
        key_estimate = "abundance_estimate_" + metric if abundance else "incidence_estimate_" + metric

        series_sample = estimator.metrics[species_id][key_sample]
        series_estimate = estimator.metrics[species_id][key_estimate]

        series_observations_ids = estimator.metrics[species_id]["abundance_no_observations"] if abundance else \
            estimator.metrics[species_id]["incidence_no_observations"]

        no_data_points = len(series_sample)

        fig.add_trace(go.Scatter(x=list(range(no_data_points)), y=series_sample, mode='lines', name='observed'), row=1,
                      col=i)
        fig.add_trace(go.Scatter(x=list(range(no_data_points)), y=series_estimate, mode='lines', name='estimated'),
                      row=1, col=i)

        fig.update_xaxes(title_text="Sample Size", row=1, col=i, tickvals=[0, no_data_points - 1],
                         ticktext=[0, series_observations_ids[-1]])
        fig.update_yaxes(title_text="Diversity", row=1, col=1)

    fig.update_layout(DIVERSITY_LAYOUT)

    return fig


def plot_diversity_series(estimator: SpeciesEstimator, species_id: str, metric: str, file_name: str,
                          abundance: bool) -> go.Figure:
    key_sample = "abundance_sample_" + metric if abundance else "incidence_sample_" + metric
    key_estimate = "abundance_estimate_" + metric if abundance else "incidence_estimate_" + metric

    series_sample = estimator.metrics[species_id][key_sample]
    series_estimate = estimator.metrics[species_id][key_estimate]

    series_observations_ids = estimator.metrics[species_id]["abundance_no_observations"] if abundance else \
        estimator.metrics[species_id]["incidence_no_observations"]

    no_data_points = len(series_sample)

    trace_sample = go.Scatter(
        x=list(range(no_data_points)),
        y=series_sample,
        mode='lines',
        name=f'{metric} observed'
    )

    trace_estimate = go.Scatter(
        x=[no_data_points - 1],
        y=[series_estimate[-1]],
        mode='markers',
        name=f'{metric} estimated',
        marker=dict(color=MARKER_COLOR, size=MARKER_SIZE)
    )

    layout = go.Layout(
        title=metric,
        xaxis=dict(title='Sample Size', tickvals=[0, no_data_points - 1], ticktext=[0, series_observations_ids[-1]]),
        yaxis=dict(title='Diversity'),
        template=LAYOUT_TEMPLATE,
    )

    fig = go.Figure(data=[trace_sample, trace_estimate], layout=layout)

    return fig


def plot_diversity_series_all(estimator: SpeciesEstimator, species_id: str, metrics: list[str], file_name: str,
                              abundance: bool) -> go.Figure:
    traces = []

    for metric, title in zip(metrics, ("D0", "D1", "D2")):
        key_sample = "abundance_sample_" + metric if abundance else "incidence_sample_" + metric
        key_estimate = "abundance_estimate_" + metric if abundance else "incidence_estimate_" + metric

        series_sample = estimator.metrics[species_id][key_sample]
        series_estimate = estimator.metrics[species_id][key_estimate]

        series_observations_ids = estimator.metrics[species_id]["abundance_no_observations"] if abundance else \
            estimator.metrics[species_id]["incidence_no_observations"]

        no_data_points = len(series_sample)

        trace_sample = go.Scatter(
            x=list(range(no_data_points)),
            y=series_sample,
            mode='lines',
            name=f'{metric} observed'
        )

        trace_estimate = go.Scatter(
            x=[no_data_points - 1],
            y=[series_estimate[-1]],
            mode='markers',
            name=f'{metric} estimated',
            marker=dict(color=MARKER_COLOR, size=MARKER_SIZE)
        )

        traces.extend([trace_sample, trace_estimate])

    layout = go.Layout(
        xaxis=dict(title='Sample Size', tickvals=[0, no_data_points - 1], ticktext=[0, series_observations_ids[-1]]),
        yaxis=dict(title='Diversity'),
        template=LAYOUT_TEMPLATE,
    )

    fig = go.Figure(data=traces, layout=layout)
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )
    return fig


def plot_diversity_profile(estimator: SpeciesEstimator, species_id: str, file_name: str, abundance: bool) -> go.Figure:
    key = "abundance_estimate_" if abundance else "incidence_estimate_"

    profile = [estimator.metrics[species_id][key + "d0"][-1],
               estimator.metrics[species_id][key + "d1"][-1],
               estimator.metrics[species_id][key + "d2"][-1]]

    trace = go.Scatter(
        x=["q=0", "q=1", "q=2"],
        y=profile,
        mode='lines+markers',
        name='Diversity Profile',
    )

    fig = go.Figure(data=[trace], layout=DIVERSITY_PROFILE_LAYOUT)
    return fig


def plot_completeness_profile(estimator: SpeciesEstimator, species_id: str, abundance: bool,
                              save_to: Optional[str] = None) -> go.Figure:
    """
    Plots the time series for both completeness and coverage using Plotly.
    :param estimator: The species estimator object.
    :param species_id: The ID of the species.
    :param abundance: Boolean indicating whether to use abundance or incidence.
    :param save_to: Optional path to save the plot.
    :return: None
    """

    key_completeness = "abundance_c0" if abundance else "incidence_c0"
    key_coverage = "abundance_c1" if abundance else "incidence_c1"

    series_completeness = estimator.metrics[species_id][key_completeness]
    series_coverage = estimator.metrics[species_id][key_coverage]
    series_observations_ids = estimator.metrics[species_id]["abundance_no_observations"] if abundance else \
        estimator.metrics[species_id]["incidence_no_observations"]

    no_data_points = len(series_completeness)
    series_ticks = [0, series_observations_ids[-1]]

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=list(range(no_data_points)), y=series_completeness, mode='lines', name='Completeness'))
    fig.add_trace(go.Scatter(x=list(range(no_data_points)), y=series_coverage, mode='lines', name='Coverage'))

    fig.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=[0, no_data_points - 1],
            ticktext=series_ticks
        ),
        xaxis_title="Sample Size",
        yaxis_title="Completeness",
        template=LAYOUT_TEMPLATE,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        autosize=True
    )

    return fig


def plot_expected_sampling_effort(estimator: SpeciesEstimator, species_id: str, abundance: bool,
                                  save_to: Optional[str] = None) -> go.Figure:
    """
    Plots the time series for expected sampling efforts
    :param estimator: SpeciesEstimator object
    :param species_id: ID of the species to plot
    :param abundance: Boolean flag to determine if abundance or incidence should be used
    :param save_to: File path to save the plot as a PDF, if None plot is shown interactively
    """

    key = "abundance_l_" if abundance else "incidence_l_"
    fig = make_subplots()

    for n in estimator.l_n:
        series_effort = estimator.metrics[species_id][key + str(n)]
        series_observations_ids = estimator.metrics[species_id]["abundance_no_observations"] if abundance else \
            estimator.metrics[species_id]["incidence_no_observations"]
        no_data_points = len(series_effort)
        series_ticks = [0, series_observations_ids[-1]]

        fig.add_trace(go.Scatter(x=list(range(no_data_points)), y=series_effort, mode='lines', name=f"l={n}"))

    fig.update_layout(
        xaxis_title="Sample Size",
        xaxis=dict(tickmode='array', tickvals=[0, no_data_points - 1], ticktext=series_ticks),
        yaxis_title="Effort",
        template=LAYOUT_TEMPLATE,
        autosize=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )

    return fig
