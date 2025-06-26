import matplotlib.pyplot as plt
import os
from qgis.core import QgsProject

class BarGraph:
    def __init__(self, years, city, no_of_raster_layers, output_path):
        """
        Initializes the BarGraph class with labels, city name, number of raster layers, and output path.

        :param labels: List of year labels corresponding to raster layers
        :param city: Name of the city being analyzed
        :param no_of_raster_layers: Number of raster layers (years) to process
        :param output_path: Directory where the output chart image will be saved
        """
        self.labels = years
        self.no_of_raster_layers = no_of_raster_layers
        self.output_path = output_path
        self.file_name = 'AOI'

    def get_values(self):
        """
        Retrieves built-up area values from the AOI layer and converts them to square kilometers.

        :return: List of area values in square kilometers for each raster layer
        """
        # Get AOI layer from project
        layer = QgsProject.instance().mapLayersByName(self.file_name)[0]
        # Extract attribute values from the first feature
        values = layer.getFeature(0).attributes()
        # Consider only the number of raster layers specified
        values = values[:self.no_of_raster_layers]
        # Convert pixel count to square kilometers (assuming each pixel = 30x30 = 900 sq.m)
        values = [((v * 900) / 1000000) for v in values]
        return values

    def plot_chart(self):
        """
        Plots a bar chart of built-up area over years and saves it as a PNG image.

        :return: None. Saves the bar chart as an image file named 'barGraph.png' in the specified output directory.
        """
        # Get AOI layer and values similar to get_values
        layer = QgsProject.instance().mapLayersByName(self.file_name)[0]
        values = layer.getFeature(0).attributes()
        values = values[:self.no_of_raster_layers]
        values = [((v * 900) / 1000000) for v in values]  # Get Area (pixel size: 30 x 30)

        # Create a figure and axis for the plot
        fig, ax = plt.subplots(figsize=(6, 6))
        # Plot bar graph
        bars = ax.bar(self.labels, values, color="red")
        # Add grid lines to y-axis
        ax.yaxis.grid(True, linestyle='--', linewidth=0.7, color='gray')

        # Add text labels on top of each bar
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height,
                f'{height:,.2f}',
                ha='center',
                va='bottom'
            )

        # Set labels and title
        ax.set_xlabel('Year')
        ax.set_ylabel('BuiltUp Area (Km²)')
        ax.set_title('Year Wise BuiltUp Area in sqKm')

        # Save the plot to the output directory
        self.output_path = os.path.join(self.output_path, 'barGraph.png')
        plt.savefig(self.output_path, dpi=350, bbox_inches='tight')