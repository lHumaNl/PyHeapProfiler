import logging
import json
from PySide6.QtWidgets import QVBoxLayout, QWidget
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


logger = logging.getLogger(__name__)


class ChartWindow(QWidget):
    """
    Window for displaying memory usage charts over time.
    """

    def __init__(self, dump_data, parent=None):
        super().__init__(parent)
        self.dump_data = dump_data
        self.setWindowTitle("Memory Usage Over Time")
        self.resize(800, 600)
        self.setup_ui()
        self.plot_charts()

    def setup_ui(self):
        """
        Set up the UI components.
        """
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

    def plot_charts(self):
        """
        Plot memory usage charts based on dump data.
        """
        try:
            self.figure.clear()

            # Check if data has temporal information
            time_series = self._extract_time_series()

            if time_series:
                # Plot temporal chart
                ax = self.figure.add_subplot(111)
                self._plot_time_series(ax, time_series)
            else:
                # Plot memory distribution charts instead
                self._plot_memory_distribution()

            self.figure.tight_layout()
            self.canvas.draw()
            logger.info("Charts plotted successfully")
        except Exception as e:
            logger.exception("Failed to plot charts")
            raise

    def _plot_time_series(self, ax, time_series):
        """Plot time series data on the given axes."""
        timestamps = [ts for ts, _ in time_series]
        sizes = [size for _, size in time_series]

        ax.plot(timestamps, sizes, marker='o', linewidth=2, markersize=6)
        ax.set_xlabel('Time', fontsize=10)
        ax.set_ylabel('Memory Size (bytes)', fontsize=10)
        ax.set_title('Memory Usage Over Time', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='both', which='major', labelsize=9)

    def _plot_memory_distribution(self):
        """Plot memory distribution charts when no temporal data is available."""
        # Get aggregated data by type
        type_sizes = []

        for obj_type, objects in self.dump_data.data.items():
            total_size = sum(obj.get('size', 0) for obj in objects.values())
            count = len(objects)
            type_sizes.append((obj_type, total_size, count))

        # Sort by size and take top 10
        type_sizes.sort(key=lambda x: x[1], reverse=True)
        top_types = type_sizes[:10]

        if not top_types:
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center',
                    transform=ax.transAxes, fontsize=12)
            return

        # Create two subplots
        ax1 = self.figure.add_subplot(121)
        ax2 = self.figure.add_subplot(122)

        # Truncate long type names
        def truncate_name(name, max_len=25):
            if len(name) > max_len:
                return name[:max_len-3] + '...'
            return name

        types = [truncate_name(t[0]) for t in top_types]
        sizes = [t[1] for t in top_types]

        # Plot 1: Memory size by type (horizontal bar chart)
        y_pos = range(len(types))
        colors = ['#2a82da', '#4a9ae6', '#6ab2f2', '#8acaff', '#aae2ff',
                  '#caf0ff', '#e0f4ff', '#f0f8ff', '#f5faff', '#fafcff']
        ax1.barh(y_pos, sizes, color=colors[:len(types)])
        ax1.set_yticks(y_pos)
        ax1.set_yticklabels(types, fontsize=8)
        ax1.set_xlabel('Size (bytes)', fontsize=10)
        ax1.set_title('Memory Usage by Type (Top 10)', fontsize=11, fontweight='bold')
        ax1.invert_yaxis()

        # Format x-axis with K/M/G suffixes
        def format_size(x, pos):
            if x >= 1e9:
                return f'{x/1e9:.1f}G'
            elif x >= 1e6:
                return f'{x/1e6:.1f}M'
            elif x >= 1e3:
                return f'{x/1e3:.1f}K'
            return f'{x:.0f}'

        from matplotlib.ticker import FuncFormatter
        ax1.xaxis.set_major_formatter(FuncFormatter(format_size))

        # Plot 2: Pie chart of memory distribution (top 5 + other)
        pie_types = type_sizes[:5]
        other_size = sum(s[1] for s in type_sizes[5:])

        pie_sizes = [t[1] for t in pie_types]
        pie_labels = [truncate_name(t[0], 20) for t in pie_types]

        if other_size > 0:
            pie_sizes.append(other_size)
            pie_labels.append('Other')

        pie_colors = ['#2a82da', '#4a9ae6', '#6ab2f2', '#8acaff', '#aae2ff', '#cccccc']
        ax2.pie(pie_sizes, labels=pie_labels, autopct='%1.1f%%', startangle=90,
                colors=pie_colors[:len(pie_sizes)], textprops={'fontsize': 8})
        ax2.set_title('Memory Distribution', fontsize=11, fontweight='bold')

    def _extract_time_series(self):
        """
        Extract time series data from the heap dump.

        Returns:
            list: List of (timestamp, size) tuples.
        """
        time_series = []

        for obj_type, objects in self.dump_data.data.items():
            for obj_id, obj_data in objects.items():
                # Check for timestamp field (common variations)
                timestamp = obj_data.get('timestamp') or obj_data.get('time') or obj_data.get('created_at')
                size = obj_data.get('size', 0)

                if timestamp is not None:
                    try:
                        time_series.append((timestamp, size))
                    except (TypeError, ValueError) as e:
                        logger.debug(f"Invalid timestamp data for object {obj_id}: {e}")

        # Sort by timestamp and aggregate by unique timestamps
        if time_series:
            time_series.sort(key=lambda x: x[0])
            aggregated = {}
            for ts, size in time_series:
                if ts in aggregated:
                    aggregated[ts] += size
                else:
                    aggregated[ts] = size
            time_series = list(aggregated.items())

        return time_series
