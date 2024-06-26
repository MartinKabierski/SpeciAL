from pathlib import Path
from typing import Optional

import pandas as pd

import special.estimation.species_estimator
from src.utils.storage import StorageManager

app_dir: Path = Path(__file__).parent
app_dir = app_dir.parent

FILE_SELECTED: bool = False
EVENT_LOG_REF: Optional[pd.DataFrame] = None

LOG_PROFILE_CACHE: StorageManager = StorageManager()
ESTIMATOR_REFERENCE: Optional[special.estimation.species_estimator.SpeciesEstimator] = None
