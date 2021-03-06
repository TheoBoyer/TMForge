"""

    Telemetry wrapper you can use to handle your metrics.
    Stores the data you append to it in memory and in a csv file

"""

import numpy as np
import pandas as pd
from shutil import copyfile
import os

class Telemetry:
    """
        Telemetry wrapper you can use to handle your metrics.
    """
    def __init__(self, metrics, dump_file_path="metrics.csv"):
        """
            params:
                metrics: list of the name of the metrics you want to keep track of
                dump_file_path: File in which you want to write the data
        """
        self.dump_file_path = dump_file_path
        self.metrics = metrics
        # The actual data
        self._data = {k: [] for k in metrics}
        # Create the file
        self.createDumpFile()

    def createDumpFile(self):
        """
            Create a csv file to dump the data in
        """
        if not os.path.isfile(self.dump_file_path):
            with open(self.dump_file_path, 'w') as f:
                f.write(",".join(self.metrics) + "\n")

    def append(self, new_row):
        """
            params:
                new_row (Dict):
                    append a new Row to the data. Missing values and np.NaNs will be ignored in the data and blank_spaces in the csv file
        """
        new_str_values= []
        for m in self.metrics:
            v = new_row.get(m, np.NaN)
            new_str_values.append("" if np.isnan(v) else str(v))
            if not np.isnan(v):
                self._data[m].append(v)
        # Write the new line
        with open(self.dump_file_path, 'a') as f:
            f.write(",".join(new_str_values) + "\n")

    def get(self, column):
        """
            Return the colun having the name specified by the "column" argument
        """
        return self._data[column]

    def setState(self, state):
        self.dump_file_path = state["dump_file_path"]
        copyfile(state["backup_path"], self.dump_file_path)
        data = pd.read_csv(self.dump_file_path)

        self.metrics = list(data.columns)
        self._data = {}
        for k in self.metrics:
            col = data[k].values
            self._data[k] = col[col == col].tolist()


    def getState(self):
        """
            Return the internal state for backup
        """
        print("Saving telemetry")
        copyfile(self.dump_file_path, "./metrics_backup.csv")
        return {
            "dump_file_path": self.dump_file_path,
            "backup_path": "./metrics_backup.csv"
        }