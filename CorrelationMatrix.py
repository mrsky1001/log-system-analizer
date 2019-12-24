import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


class CorrelationMatrix:
    def __init__(self, rrd):
        self.rrd = rrd

    def display_matrix(self):
        data = pd.read_csv(self.rrd.csv_export())
        corrmat = data.corr()

        f, ax = plt.subplots(figsize=(12, 8))
        sns.heatmap(corrmat, mask=sns.np.zeros_like(corrmat, dtype=sns.np.bool),
                    cmap=sns.diverging_palette(220, 10, as_cmap=True), square=True, ax=ax)
        plt.savefig('graphs/correlation_matrix.png')
        plt.show()

    # показывает отношения между всеми парами переменных.
    def display_pairplot(self):
        data = pd.read_csv(self.rrd.csv_export())

        plt.subplots(figsize=(12, 8))
        sns.pairplot(data)
        plt.savefig('graphs/correlation_hists.png')
        plt.show()
