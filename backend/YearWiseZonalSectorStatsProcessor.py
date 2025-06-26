from qgis.core import (
    QgsRasterLayer, QgsProject, QgsVectorLayer
)
from qgis.analysis import QgsZonalStatistics
from qgis.utils import iface
from .DirectionalRingGenerator import DirectionalRingGenerator

import pandas as pd
import os

class YearWiseZonalSectorStatsProcessor:
    """
    This class computes zonal statistics (sum) for each year and each directional sector 
    based on raster and vector layers, then compiles the results into a single Excel sheet.

    :param iface: QGIS interface object
    :param city: Name of the city (used for layer naming and output structure)
    :param raster_paths: List of file paths to raster layers, each corresponding to a year
    :param years: List of years corresponding to the raster layers
    :param no_of_sectors: Number of directional sectors
    :param centroid_point: Central point used to generate directional ring sectors
    :param output_path: Folder path where Excel output will be saved
    :param vector_layer_name: Name of vector layer with directional sectors (default: 'MultiRings')
    """
    def __init__(self, iface, city, raster_paths, years, no_of_sectors, centroid_point, output_path, vector_layer_name='MultiRings'):
        self.iface = iface
        self.city = city
        self.raster_paths = raster_paths
        self.years = years
        self.no_of_sectors = no_of_sectors
        self.centroid_point = centroid_point
        self.output_path = output_path
        self.vector_layer_name = vector_layer_name
        self.attrTableAllYears = []  # Stores stats for all years
        self.dir_ring_gen()            # Generate directional rings
        self.delete_prev_year_IPVSUM()  # Clean up any previous 'ipv-sum' fields

    def dir_ring_gen(self):
        """
        Generates the directional ring layer without visualizing it.
        """
        generator = DirectionalRingGenerator(self.iface, self.city, self.no_of_sectors, self.centroid_point, False)
        generator.generate_layer()

    def calculate_year_wise_stats(self, raster_path, year):
        """
        Calculates zonal sum statistics for the given raster and year using the vector ring layer.

        :param raster_path: File path to the raster layer for the given year
        :param year: The year associated with this raster
        :return: Dictionary of sector-wise summed values
        """
        raster_layer = QgsRasterLayer(raster_path, 'Raster Layer')
        vector_layer = QgsProject.instance().mapLayersByName(self.vector_layer_name)[0]

        # Perform zonal statistics using SUM
        zoneStat = QgsZonalStatistics(vector_layer, raster_layer, 'ipv-', 1, QgsZonalStatistics.Sum)
        zoneStat.calculateStatistics(None)

        # Extract and normalize (area in km²) stats for each sector (1-indexed)
        attributeTable = {}
        for i in range(1, self.no_of_sectors + 1):
            value = vector_layer.getFeature(i).attributes()
            attributeTable[value[0]] = (value[1] * 900) / 1000000  # Convert cell area sum to km²

        # Get summed area from AOI layer (for footer)
        layer = QgsProject.instance().mapLayersByName("AOI")[0]
        yearStats = layer.getFeature(0).attributes()[::-1]  # Reverse to match ordering

        # Create a DataFrame for this year's zonal statistics
        df = pd.DataFrame(attributeTable.items(), columns=['Sector', str(year)])

        # Merge with cumulative DataFrame
        if not hasattr(self, 'zonal_df') or self.zonal_df.empty:
            self.zonal_df = df
        else:
            self.zonal_df = pd.merge(self.zonal_df, df, on='Sector', how='outer')

        # Add footer row for total area across sectors (AOI)
        sum_row = ['Sum:']
        for y in self.years:
            col_name = str(y)
            if col_name in self.zonal_df.columns:
                idx = self.years.index(y)
                sum_value = yearStats[idx] if idx < len(yearStats) else ""
            else:
                sum_value = ""
            sum_row.append(sum_value)

        # Reindex columns to maintain correct year order and add sum row
        final_df = self.zonal_df.copy()
        final_df = final_df.reindex(columns=['Sector'] + [str(y) for y in self.years])
        final_df.loc[len(final_df)] = sum_row

        # Write to Excel
        path = os.path.join(self.output_path, 'sectoralWiseStats.xlsx')
        os.makedirs(os.path.dirname(path), exist_ok=True)
        final_df.to_excel(path, index=False)

        return attributeTable

    def delete_prev_year_IPVSUM(self):
        """
        Removes the 'ipv-sum' attribute field from the active vector layer 
        (cleanup before recalculating zonal stats).
        """
        layer = iface.activeLayer()

        if layer.isValid() and layer.type() == QgsVectorLayer.VectorLayer:
            layer.startEditing()
            fields_to_delete = ['ipv-sum']

            for field_name in fields_to_delete:
                idx = layer.fields().indexOf(field_name)
                if idx != -1:
                    layer.deleteAttribute(idx)

            layer.commitChanges()
        else:
            print("The layer is not a valid vector layer.")
            pass

    def run(self):
        """
        Main driver that runs zonal statistics for all raster layers/year pairs 
        and returns the final list of attribute tables per year.
        """
        for i, raster_path in enumerate(self.raster_paths):
            self.attrTableAllYears.append(self.calculate_year_wise_stats(raster_path, self.years[i]))
            self.delete_prev_year_IPVSUM()
        return self.attrTableAllYears