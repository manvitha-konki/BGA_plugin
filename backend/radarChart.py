import matplotlib.pyplot as plt
import numpy as np
import os
from .DirectionalRingGenerator import DirectionalRingGenerator

class radarChart:
    """
    This class generates a radar chart (polar plot) based on directional segment values.
    Used to visualize directional growth or intensity around a centroid point.
    """

    def __init__(self, city, raster_paths, centroid, datasets, no_of_sectors, colors, output_path, titles = None):
        """
        Initializes the radarChart instance with all necessary data and triggers plotting.

        :param city: Name of the region
        :param raster_paths: List of raster file paths
        :param centroid: Tuple representing centroid coordinates (x, y)
        :param datasets: List of data lists (one per year/layer)
        :param no_of_sectors: Number of directional sectors (e.g., 4, 8, 16)
        :param colors: List of RGBA strings for each dataset
        :param outputPath: Directory path to save the output image
        :param titles: Optional list of titles for each dataset
        """
        self.city = city
        self.no_of_sectors = no_of_sectors

        # Directional categories: reduced to match number of sectors
        self.categories = ['E', 'ENE', 'NE', 'NNE', 'N', 'NNW', 'NW', 'WNW', 'W', 'WSW', 'SW', 'SSW', 'S', 'SSE', 'SE', 'ESE']
        self.categories = self.categories[::(16 // self.no_of_sectors)]

        self.raster_paths = raster_paths
        self.centroid = centroid
        self.titles = titles
        self.datasets = datasets
        self.colors = colors
        self.output_path = output_path

        self.plot()  # Plot the radar chart upon initialization

    def parse_rgba_string(self, rgba_str):
        """
        Converts a comma-separated RGBA string into a matplotlib-compatible tuple.

        :param rgba_str: String in the format "R,G,B,A"
        :return: Tuple of (R, G, B, A) with each channel normalized to [0, 1]
        """
        r, g, b, a = map(int, rgba_str.split(','))
        return (r / 255, g / 255, b / 255, a / 255)

    def plot(self):
        """
        Generates and saves the radar chart based on provided datasets and configuration.
        """
        # Create angles for radar sectors
        angles = np.linspace(0, 2 * np.pi, self.no_of_sectors, endpoint=False)
        angles = np.concatenate((angles, [angles[0]]))  # Close the loop for radar plot

        # Create polar subplot
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

        for i, data in enumerate(self.datasets):
            # Close loop in data for radar polygon
            data = np.concatenate((data, [data[0]]))
            # Plot each dataset as a line on radar
            ax.plot(
                angles,
                data,
                label=self.titles[i] if self.titles else f'Data {i+1}',
                linewidth=2,
                color=self.parse_rgba_string(self.colors[i])
            )
            # Optional: fill area under the curve
            # ax.fill(angles, data, alpha=0.25)

        # Set grid labels and plot title
        ax.set_thetagrids(np.degrees(angles[:-1]), self.categories)
        ax.set_ylim(0, max(max(d) for d in self.datasets))
        ax.set_title('Direction and Magnitude')
        ax.grid(True)
        ax.legend(loc='upper right', bbox_to_anchor=(1.1, 1.1))

        # Add centroid coordinates as footnote
        plt.figtext(0.98, 0.02, f'centroid: ({self.centroid[0]:.5f}, {self.centroid[1]:.5f})',
                    ha='right', va='bottom', fontsize=10)

        # Save radar chart as image
        self.output_path = os.path.join(self.output_path, 'radarChart.png')
        plt.savefig(self.output_path, dpi=350, bbox_inches='tight')