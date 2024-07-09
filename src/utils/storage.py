from typing import Optional, List, Dict, Union

import pandas as pd

SPECIES_KEY: str = "species"
METRICS_KEY: str = "metric"


class StorageManager:
    """A singleton class to manage the storage of data."""
    _instance: Optional['StorageManager'] = None

    def __new__(cls) -> 'StorageManager':
        if cls._instance is None:
            cls._instance = super(StorageManager, cls).__new__(cls)
            cls._instance._dataframe = pd.DataFrame()
        return cls._instance

    def __init__(self) -> None:
        """Initialize the StorageManager."""
        if not hasattr(self, '_initialized'):
            self._initialized = True

    def add(self, new_data: pd.DataFrame) -> None:
        """Add a new row to the DataFrame."""
        # remove rows where the species is the same
        self._dataframe = pd.concat([self._dataframe, new_data])
        self._dataframe.drop_duplicates()

    def set_dataframe(self, dataframe: pd.DataFrame) -> None:
        """Set the DataFrame."""
        self._dataframe = dataframe

    def get_dataframe(self) -> pd.DataFrame:
        """Get the DataFrame."""
        return self._dataframe

    def filter_rows(self, for_species: str, for_metric: str) -> pd.DataFrame:
        """Filter the DataFrame based on the species and metric."""
        return self._dataframe[
            (self._dataframe[SPECIES_KEY] == for_species) & (self._dataframe[METRICS_KEY] == for_metric)
            ]

    def get_species(self) -> List[str]:
        """Get the unique species in the DataFrame."""
        if self._dataframe.empty:
            return []
        return self._dataframe[SPECIES_KEY].unique().tolist()

    def get_metrics(self) -> List[str]:
        """Get the unique metrics in the DataFrame."""
        return self._dataframe[METRICS_KEY].unique().tolist()

    def clear(self) -> None:
        """Clear the DataFrame."""
        self._dataframe = pd.DataFrame()

    def is_empty(self) -> bool:
        """Check if the DataFrame is empty."""
        return self._dataframe.empty

    def exists(self, species: str) -> bool:
        """Check if the species is in the DataFrame."""
        return species in self.get_species()

    def filter_for_metric(self, species: str, metric: str) -> Dict[str, List[Union[int, float]]]:
        """Filter the DataFrame based on the species and a substring in the metric, and return the results as a dictionary."""
        filtered_df = self._dataframe[self._dataframe[SPECIES_KEY] == species]
        filtered_df = filtered_df[filtered_df[METRICS_KEY].str.contains(metric, na=False)]

        result: Dict[str, List[Union[int, float]]] = {}

        for metric_value in filtered_df[METRICS_KEY].unique():
            metric_key = metric_value.replace(f'_{metric}', '')

            if metric_key == "abundance":
                metric_key = "abundance_sample"
            if metric_key == "incidence":
                metric_key = "incidence_sample"

            metric_data = filtered_df[filtered_df[METRICS_KEY] == metric_value]
            result[metric_key] = list(metric_data['value'])

        return result

    def get_value_by_metric(self, metric: str) -> pd.Series:
        """Get the value for a species and metric."""
        filtered_df = self._dataframe[self._dataframe[METRICS_KEY] == metric]
        return filtered_df['value']
