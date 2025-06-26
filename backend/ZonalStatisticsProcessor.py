import processing
from qgis.core import (
    QgsRasterLayer, QgsVectorLayer, QgsProject
)
from qgis.analysis import QgsZonalStatistics
from .delAttributes import delAttributes

class ZonalStatisticsProcessor:
    """
    This class handles the processing of zonal statistics by applying raster layers to a vector AOI layer.
    The output is stored as attribute values within the vector layer.
    """

    def __init__(self, raster_paths, vector_path):
        """
        Initializes the processor and runs the zonal statistics analysis.

        :param raster_paths: List of raster file paths to be used for statistics.
        :param vector_path: Path to the vector layer (AOI) used as zones.
        """
        self.raster_paths = raster_paths
        self.vector_path = vector_path
        self.process()

    def process(self):
        """
        Runs zonal statistics on the vector layer using each raster in the list.
        It clears old attributes before computing new statistics.
        """
        # Load the AOI vector layer from the QGIS project
        layer = QgsProject.instance().mapLayersByName("AOI")[0]

        # Remove existing attributes other than 'FID' and geometry
        delAttributes(layer)

        # Loop through all raster paths
        for i, raster_path in enumerate(self.raster_paths):
            # Create a raster layer
            raster_layer = QgsRasterLayer(raster_path, 'Raster Layer')

            # Create a Zonal Statistics object with prefix 'ipv-'
            zone_stat = QgsZonalStatistics(layer, raster_layer, 'ipv-', 1, QgsZonalStatistics.Sum)

            # Compute statistics and store in the AOI layer
            zone_stat.calculateStatistics(None)

        # Reload layer after modification (optional redundancy)
        layer = QgsProject.instance().mapLayersByName("AOI")[0]