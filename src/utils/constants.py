import os
from functools import partial
from typing import Sequence

from htmltools import Tagifiable, Tag, MetadataNode
from htmltools._core import ReprHtml, TagList, TagAttrDict

from SpeciAL.estimation import species_estimator, species_retrieval

HTMLBody = Tagifiable | Tag | MetadataNode | ReprHtml | str | TagList | float | None | Sequence | dict[str, str | float | bool | None] | TagAttrDict

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

ESTIMATOR_MAP = \
    {
        "1-gram": species_estimator.SpeciesEstimator(
            partial(species_retrieval.retrieve_species_n_gram, n=1),
            d0=True,
            d1=True,
            d2=True,
            c0=True,
            c1=True,
            l_n=[0.9, 0.95, 0.99],
            step_size=DEFAULT_SET_SIZE
        ),
        "2-gram": species_estimator.SpeciesEstimator(
            partial(species_retrieval.retrieve_species_n_gram, n=2),
                        d0=True,
            d1=True,
            d2=True,
            c0=True,
            c1=True,
            l_n=[0.9, 0.95, 0.99],
            step_size=DEFAULT_SET_SIZE
        ),
        "3-gram": species_estimator.SpeciesEstimator(
            partial(species_retrieval.retrieve_species_n_gram, n=3),
                        d0=True,
            d1=True,
            d2=True,
            c0=True,
            c1=True,
            l_n=[0.9, 0.95, 0.99],
            step_size=DEFAULT_SET_SIZE
        ),
        "4-gram": species_estimator.SpeciesEstimator(
            partial(species_retrieval.retrieve_species_n_gram, n=4),
                        d0=True,
            d1=True,
            d2=True,
            c0=True,
            c1=True,
            l_n=[0.9, 0.95, 0.99],
            step_size=DEFAULT_SET_SIZE
        ),
        "5-gram": species_estimator.SpeciesEstimator(
            partial(species_retrieval.retrieve_species_n_gram, n=5),
                        d0=True,
            d1=True,
            d2=True,
            c0=True,
            c1=True,
            l_n=[0.9, 0.95, 0.99],
            step_size=DEFAULT_SET_SIZE
        ),
        "trace_variants": species_estimator.SpeciesEstimator(
            species_retrieval.retrieve_species_trace_variant,
                        d0=True,
            d1=True,
            d2=True,
            c0=True,
            c1=True,
            l_n=[0.9, 0.95, 0.99],
            step_size=DEFAULT_SET_SIZE
        ),

        "2-gram_complete_log": species_estimator.SpeciesEstimator(
            partial(species_retrieval.retrieve_species_n_gram, n=2),
                        d0=True,
            d1=True,
            d2=True,
            c0=True,
            c1=True,
            l_n=[0.9, 0.95, 0.99],
            step_size=DEFAULT_SET_SIZE
        ),

        "2-gram_all_metrics": species_estimator.SpeciesEstimator(
            partial(species_retrieval.retrieve_species_n_gram, n=2),
                        d0=True,
            d1=True,
            d2=True,
            c0=True,
            c1=True,
            l_n=[0.9, 0.95, 0.99],
            step_size=DEFAULT_SET_SIZE
        ),
    }
