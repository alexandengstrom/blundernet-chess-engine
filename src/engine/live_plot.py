import matplotlib.pyplot as plt
import numpy as np

class LivePlot:
    def __init__(self):
        self.accuracies = []
        self.losses = []

        plt.ion()
        self.fig, (self.ax_acc, self.ax_loss) = plt.subplots(2, 1, sharex=True, figsize=(8, 6))
        self.fig.canvas.manager.set_window_title("Live Model Accuracy and Loss")

        self.line_acc, = self.ax_acc.plot([], [], marker='o', color='green', label="Accuracy")
        self.trend_acc, = self.ax_acc.plot([], [], 'g--', label="Trend")
        self.ax_acc.set_ylabel("Accuracy")
        self.ax_acc.set_title("Model Accuracy Progress")
        self.ax_acc.grid(True)
        self.ax_acc.legend()

        self.line_loss, = self.ax_loss.plot([], [], marker='o', color='red', label="Loss")
        self.trend_loss, = self.ax_loss.plot([], [], 'r--', label="Trend")
        self.ax_loss.set_xlabel("Game chunks")
        self.ax_loss.set_ylabel("Loss")
        self.ax_loss.set_title("Model Loss Progress")
        self.ax_loss.grid(True)
        self.ax_loss.legend()

        self.fig.tight_layout()

    def update(self, acc, loss):
        self.accuracies.append(acc)
        self.losses.append(loss)
        x = np.arange(1, len(self.accuracies) + 1)

        self.line_acc.set_data(x, self.accuracies)
        self.ax_acc.set_xlim(1, len(self.accuracies) + 1)
        self.ax_acc.set_ylim(min(self.accuracies) - 0.01, max(self.accuracies) + 0.01)

        if len(x) >= 2:
            coeffs = np.polyfit(x, self.accuracies, 1)
            trend = np.poly1d(coeffs)
            self.trend_acc.set_data(x, trend(x))

        self.line_loss.set_data(x, self.losses)
        self.ax_loss.set_xlim(1, len(self.losses) + 1)
        self.ax_loss.set_ylim(min(self.losses) - 0.1, max(self.losses) + 0.1)

        if len(x) >= 2:
            coeffs = np.polyfit(x, self.losses, 1)
            trend = np.poly1d(coeffs)
            self.trend_loss.set_data(x, trend(x))

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
