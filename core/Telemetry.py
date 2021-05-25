import numpy as np

class Telemetry:
    def __init__(self, metrics, dump_file_path="metrics.csv"):
        self.dump_file_path = dump_file_path
        self.metrics = metrics
        self._data = {k: [] for k in metrics}

        self.createDumpFile()

    def createDumpFile(self):
        with open(self.dump_file_path, 'w') as f:
            f.write(",".join(self.metrics) + "\n")

    def append(self, new_row):
        new_str_values= []
        for m in self.metrics:
            v = new_row.get(m, np.NaN)
            new_str_values.append("" if np.isnan(v) else str(v))
            if not np.isnan(v):
                self._data[m].append(v)

        with open(self.dump_file_path, 'a') as f:
            f.write(",".join(new_str_values) + "\n")

    def get(self, column):
        return self._data[column]

    def getState(self):
        return {
            "data_path": self.dump_file_path
        }