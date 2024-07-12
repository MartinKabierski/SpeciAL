import os
from functools import partial
from typing import Sequence

from htmltools import Tagifiable, Tag, MetadataNode
from htmltools._core import ReprHtml, TagList, TagAttrDict
from shiny import ui

from special.estimation import species_estimator, species_retrieval

HTMLBody = Tagifiable | Tag | MetadataNode | ReprHtml | str | TagList | float | None | Sequence | dict[
    str, str | float | bool | None] | TagAttrDict

DEFAULT_ATTRS = {
    "d0": True,
    "d1": True,
    "d2": True,
    "c0": True,
    "c1": True,
    "l_n": [0.9, 0.95, 0.99],
    # "step_size": DEFAULT_SET_SIZE
}

DEFAULT_SET_SIZE: int = 100

RETRIVAL_MAP = {
    "1-gram": partial(species_retrieval.retrieve_species_n_gram, n=1),
    "2-gram": partial(species_retrieval.retrieve_species_n_gram, n=2),
    "3-gram": partial(species_retrieval.retrieve_species_n_gram, n=3),
    "4-gram": partial(species_retrieval.retrieve_species_n_gram, n=4),
    "5-gram": partial(species_retrieval.retrieve_species_n_gram, n=5),
    "trace_variants": species_retrieval.retrieve_species_trace_variant,
    # "2-gram_complete_log": species_retrieval.retrieve_timed_activity,
    # "2-gram_all_metrics": species_retrieval.retrieve_timed_activity_exponential,
}

INFO_BUTTON_TEXT: dict[str, HTMLBody] = {
    'tool1_main_page_info':ui.p(ui.strong("Species Retrieval Functions"), ui.br(),
        ui.strong("1-gram"), ": Retrieve species based on the frequency of activities in the event log.", ui.br(),
        ui.strong("2-gram"), " : Retrieve species based on the frequency of pairs of activities in the event log.", ui.br(),
        ui.strong("3-gram"), ": Retrieve species based on the frequency of triplets of activities in the event log.", ui.br(),
        ui.strong("4-gram"), ": Retrieve species based on the frequency of quadruplets of activities in the event log.", ui.br(),
        ui.strong("5-gram"), ": Retrieve species based on the frequency of quintuplets of activities in the event log.", ui.br(),
        ui.strong("trace_variants"), ": Retrieve species based on the frequency of trace variants in the event log.", ui.br(),
    ),
    "tool1_rank_info": ui.p(ui.strong("Rank"), ": The rank of the species based on the metric selected."),
    "tool1_species_table_info": ui.p(ui.strong("Species Table"), ": The table of species and the metric selected."),
    "tool1_profiles_info": ui.p(ui.strong("Profiles"), ": The profiles of the species based on the metric selected."),
    "tool1_completeness_profile":
        ui.p(ui.strong("Completeness Profile"), ": The completeness profile of the species based on the metric selected."),
}

