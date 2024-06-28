from enum import Enum

import matplotlib.pyplot as plt
import numpy as np
from plotly.subplots import make_subplots

from special.estimation.species_estimator import SpeciesEstimator
import plotly.graph_objects as go


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
        fillcolor='rgba(0,100,80,0.2)',
        line=dict(color='rgb(0,100,80)')
    )

    layout = go.Layout(
        xaxis=dict(title='Species Rank', tickvals=[1, no_species]),
        yaxis=dict(title='Occurrences', tickvals=[0, max(reference_values_sorted)]),
        template="simple_white",
        margin=dict(l=50, r=50, b=50, t=50),
    )

    fig = go.Figure(data=[trace1], layout=layout)

    return fig


def plot_diversity_sample_vs_estimate(estimator: SpeciesEstimator, species_id: str, metrics: [str], file_name: str,
                                      abundance: bool) -> go.Figure:
    """
    Plots the obtained time series of sample-based diversity vs asymptotic diversity
    :param estimator: SpeciesEstimator object
    :param species_id: Identifier for the species
    :param metrics: List of metrics to plot
    :param file_name: Output file name for the plot
    :param abundance: Boolean indicating if abundance data should be used
    :return: Plotly Figure object
    """
    fig = make_subplots(rows=1, cols=3, shared_yaxes=True, subplot_titles=("D0", "D1", "D2"))

    for i, (metric, title) in enumerate(zip(metrics, ("D0", "D1", "D2")), start=1):
        key_sample = "abundance_sample_" + metric if abundance else "incidence_sample_" + metric
        key_estimate = "abundance_estimate_" + metric if abundance else "incidence_estimate_" + metric

        series_sample = estimator.metrics[species_id][key_sample]
        series_estimate = estimator.metrics[species_id][key_estimate]

        series_observations_ids = estimator.metrics[species_id]["abundance_no_observations"] if abundance else \
            estimator.metrics[species_id]["incidence_no_observations"]

        no_data_points = len(series_sample)
        series_ticks = estimator.metrics[species_id]["abundance_no_observations"] if abundance else \
            estimator.metrics[species_id]["incidence_no_observations"]

        fig.add_trace(go.Scatter(x=list(range(no_data_points)), y=series_sample, mode='lines', name='observed'),
                      row=1, col=i)
        fig.add_trace(go.Scatter(x=list(range(no_data_points)), y=series_estimate, mode='lines', name='estimated'),
                      row=1, col=i)

        fig.update_xaxes(title_text="Sample Size", row=1, col=i, tickvals=[0, no_data_points - 1],
                         ticktext=[0, series_observations_ids[-1]])
        fig.update_yaxes(title_text="Diversity", row=1, col=1)

    fig.update_layout(autosize=True, template="simple_white", title_text="Sample-based Diversity vs Asymptotic Diversity",
                      showlegend=True)

    return fig


def plot_diversity_series(estimator: SpeciesEstimator, species_id: str, metric: str, file_name: str,
                          abundance: bool) -> go.Figure:
    """
    Plots the time series of the specified sample-based diversity metric, adding the asymptotic diversity as an indicator
    :param estimator: SpeciesEstimator object
    :param species_id: Identifier for the species
    :param metric: Metric to plot
    :param file_name: Output file name for the plot
    :param abundance: Boolean indicating if abundance data should be used
    :return: Plotly Figure object
    """
    key_sample = "abundance_sample_" + metric if abundance else "incidence_sample_" + metric
    key_estimate = "abundance_estimate_" + metric if abundance else "incidence_estimate_" + metric

    series_sample = estimator.metrics[species_id][key_sample]
    series_estimate = estimator.metrics[species_id][key_estimate]

    series_observations_ids = estimator.metrics[species_id]["abundance_no_observations"] if abundance else \
        estimator.metrics[species_id]["incidence_no_observations"]

    no_data_points = len(series_sample)
    series_ticks = estimator.metrics[species_id]["abundance_no_observations"] if abundance else \
        estimator.metrics[species_id]["incidence_no_observations"]

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
        marker=dict(color='grey', size=10)
    )

    layout = go.Layout(
        title=metric,
        xaxis=dict(title='Sample Size', tickvals=[0, no_data_points - 1], ticktext=[0, series_observations_ids[-1]]),
        yaxis=dict(title='Diversity'),
        template="simple_white",
        margin=dict(l=50, r=50, b=50, t=50),
    )

    fig = go.Figure(data=[trace_sample, trace_estimate], layout=layout)

    return fig


def plot_diversity_series_all(estimator: SpeciesEstimator, species_id: str, metrics: [str], file_name: str,
                              abundance: bool) -> go.Figure:
    """
    Plots all sample-based diversity metrics with their asymptotic diversity
    :param estimator: SpeciesEstimator object
    :param species_id: Identifier for the species
    :param metrics: List of metrics to plot
    :param file_name: Output file name for the plot
    :param abundance: Boolean indicating if abundance data should be used
    :return: Plotly Figure object
    """
    traces = []

    for metric, title in zip(metrics, ("D0", "D1", "D2")):
        key_sample = "abundance_sample_" + metric if abundance else "incidence_sample_" + metric
        key_estimate = "abundance_estimate_" + metric if abundance else "incidence_estimate_" + metric

        series_sample = estimator.metrics[species_id][key_sample]
        series_estimate = estimator.metrics[species_id][key_estimate]

        series_observations_ids = estimator.metrics[species_id]["abundance_no_observations"] if abundance else \
            estimator.metrics[species_id]["incidence_no_observations"]

        no_data_points = len(series_sample)
        series_ticks = estimator.metrics[species_id]["abundance_no_observations"] if abundance else \
            estimator.metrics[species_id]["incidence_no_observations"]

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
            marker=dict(color='grey', size=10)
        )

        traces.extend([trace_sample, trace_estimate])

    layout = go.Layout(
        title="Sample-based Diversity Metrics",
        xaxis=dict(title='Sample Size', tickvals=[0, no_data_points - 1], ticktext=[0, series_observations_ids[-1]]),
        yaxis=dict(title='Diversity'),
        template="simple_white",
        margin=dict(l=50, r=50, b=50, t=50),
    )

    fig = go.Figure(data=traces, layout=layout)

    return fig


def plot_diversity_profile(estimator: SpeciesEstimator, species_id: str, file_name: str, abundance: bool) -> go.Figure:
    """
    Plots the asymptotic diversity profile
    :param estimator: SpeciesEstimator object
    :param species_id: Identifier for the species
    :param file_name: Output file name for the plot
    :param abundance: Boolean indicating if abundance data should be used
    :return: Plotly Figure object
    """
    key = "abundance_estimate_" if abundance else "incidence_estimate_"

    profile = [estimator.metrics[species_id][key + "d0"][-1],
               estimator.metrics[species_id][key + "d1"][-1],
               estimator.metrics[species_id][key + "d2"][-1]]

    trace = go.Scatter(
        x=["q=0", "q=1", "q=2"],
        y=profile,
        mode='lines+markers',
        name='Diversity Profile'
    )

    layout = go.Layout(
        title="Asymptotic Diversity Profile",
        xaxis=dict(title='Order q'),
        yaxis=dict(title='Diversity'),
        template="simple_white",
        margin=dict(l=50, r=50, b=50, t=50),
    )

    fig = go.Figure(data=[trace], layout=layout)

    return fig


def plot_completeness_profile(estimator: SpeciesEstimator, species_id: str, file_name: str,
                              abundance: bool) -> go.Figure:
    """
    Plots the time series for both completeness and coverage
    :param estimator: SpeciesEstimator object
    :param species_id: Identifier for the species
    :param file_name: Output file name for the plot
    :param abundance: Boolean indicating if abundance data should be used
    :return: Plotly Figure object
    """
    key_completeness = "abundance_c0" if abundance else "incidence_c0"
    key_coverage = "abundance_c1" if abundance else "incidence_c1"

    series_completeness = estimator.metrics[species_id][key_completeness]
    series_coverage = estimator.metrics[species_id][key_coverage]

    series_observations_ids = estimator.metrics[species_id]["abundance_no_observations"] if abundance else \
        estimator.metrics[species_id]["incidence_no_observations"]

    no_data_points = len(series_completeness)

    trace_completeness = go.Scatter(
        x=list(range(no_data_points)),
        y=series_completeness,
        mode='lines',
        name='Completeness'
    )

    trace_coverage = go.Scatter(
        x=list(range(no_data_points)),
        y=series_coverage,
        mode='lines',
        name='Coverage'
    )

    layout = go.Layout(
        title="Completeness Profile",
        xaxis=dict(title='Sample Size', tickvals=[0, no_data_points - 1], ticktext=[0, series_observations_ids[-1]]),
        yaxis=dict(title='Value'),
        template="simple_white",
        margin=dict(l=50, r=50, b=50, t=50),
        legend=dict(x=0.1, y=1.1)
    )

    fig = go.Figure(data=[trace_completeness, trace_coverage], layout=layout)

    return fig


def plot_expected_sampling_effort(estimator: SpeciesEstimator, species_id: str, file_name: str,
                                  abundance: bool) -> go.Figure:
    """
    Plots the time series for expected sampling efforts
    :param estimator: SpeciesEstimator object
    :param species_id: Identifier for the species
    :param file_name: Output file name for the plot
    :param abundance: Boolean indicating if abundance data should be used
    :return: Plotly Figure object
    """
    key = "abundance_l_" if abundance else "incidence_l_"
    traces = []

    for n in estimator.l_n:
        series_effort = estimator.metrics[species_id][key + str(n)]

        series_observations_ids = estimator.metrics[species_id]["abundance_no_observations"] if abundance else \
            estimator.metrics[species_id]["incidence_no_observations"]

        no_data_points = len(series_effort)

        trace = go.Scatter(
            x=list(range(no_data_points)),
            y=series_effort,
            mode='lines',
            name=f'l={n}'
        )
        traces.append(trace)

    layout = go.Layout(
        title="Expected Sampling Effort",
        xaxis=dict(title='Sample Size', tickvals=[0, no_data_points - 1], ticktext=[0, series_observations_ids[-1]]),
        yaxis=dict(title='Effort'),
        template="simple_white",
        margin=dict(l=50, r=50, b=50, t=50),
        legend=dict(x=0.1, y=1.1)
    )

    fig = go.Figure(data=traces, layout=layout)

    return fig
