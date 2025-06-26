from .loadLayers import loadLayers
from .SaveRasterImages import SaveRasterImages
from .SaveOverLaidLayer import SaveOverLaidLayer
from .ZonalStatisticsProcessor import ZonalStatisticsProcessor
from .BarGraph import BarGraph
from .radarChart import radarChart
from .DirectionalRingGenerator import DirectionalRingGenerator
from .YearWiseZonalSectorStatsProcessor import YearWiseZonalSectorStatsProcessor
from .LayoutImageExporter import LayoutImageExporter

import os
import shutil

from qgis.PyQt.QtCore import QCoreApplication

class CityRasterProcessor:
    """
    Main processor class for performing multiple geospatial operations on raster and vector layers
    including loading layers, saving images, generating statistics, and exporting visualizations.
    """
    
    def __init__(self, output_path, dlg, iface, city, raster_paths, aoi_path, labels, no_of_sectors, colors, centroid_point=None):
        """
        Initializes the processor and immediately triggers the full pipeline.

        Parameters:
            output_path (str): Base output directory path.
            dlg (QDialog): Reference to the plugin dialog for UI updates.
            iface (QgsInterface): Reference to the QGIS interface.
            city (str): Name of the city or project.
            raster_paths (list): List of paths to input raster files.
            aoi_path (str): Path to the AOI vector layer.
            labels (list): Year or category labels corresponding to rasters.
            no_of_sectors (int): Number of sectors for directional statistics.
            colors (list): Color list for radar chart sectors.
            centroid_point (QgsPointXY, optional): Center point for directional rings.
        """
        self.output_path = os.path.join(output_path, city)
        # Delete the folder if it exists
        if os.path.exists(self.output_path):
            shutil.rmtree(self.output_path)

        # Create the folder
        os.makedirs(self.output_path)
        self.city = city
        self.dlg = dlg
        self.iface = iface
        self.raster_paths = raster_paths
        self.noOfRasterLayers = len(raster_paths)
        self.aoi_path = aoi_path
        self.labels = labels
        self.no_of_sectors = no_of_sectors
        self.colors = colors
        self.centroid_point = centroid_point
        self.run_all()

    def load_layers(self):
        """
        Loads raster and AOI layers into the QGIS project.
        """
        loadLayers(
            self.iface,
            self.raster_paths,
            self.aoi_path,
            self.city,
            self.no_of_sectors,
            self.noOfRasterLayers,
            self.colors,
            self.centroid_point
        )

    def save_raster_images(self):
        """
        Saves raster images one by one using SaveRasterImages.
        """
        for _ in range(self.noOfRasterLayers):
            SaveRasterImages(self.city, self.output_path, self.labels)

    def save_overlay_layer(self):
        """
        Saves a composite image by overlaying all raster and AOI layers.
        """
        SaveOverLaidLayer(self.city, self.noOfRasterLayers, self.output_path)

    def yearArea(self):
        """
        Performs zonal statistics to calculate built-up area for each year.
        """
        ZonalStatisticsProcessor(self.raster_paths, self.aoi_path)

    def generate_bar_graph(self):
        """
        Generates and saves a bar graph showing built-up area by year.
        """
        obj_bargraph = BarGraph(self.labels, self.city, self.noOfRasterLayers, self.output_path)
        obj_bargraph.plot_chart()

    def generate_radar_chart(self):
        """
        Generates directional radar charts representing built-up area spread per sectors.
        """
        obj_ring_gen = DirectionalRingGenerator(self.iface, self.city, self.no_of_sectors, self.centroid_point)

        if self.centroid_point is None:
            centroid = obj_ring_gen.get_centroid()
        else:
            centroid = self.centroid_point

        obj_yr_zonal_stats = YearWiseZonalSectorStatsProcessor(
            self.iface,
            self.city,
            self.raster_paths[::-1],
            self.labels[::-1],
            self.no_of_sectors,
            self.centroid_point,
            self.output_path
        )

        each_zonal_stats = obj_yr_zonal_stats.run()
        datasets = [list(attr.values()) for attr in each_zonal_stats]

        radarChart(
            city=self.city,
            raster_paths=self.raster_paths[::-1],
            centroid=centroid,
            datasets=datasets,
            titles=self.labels[::-1],
            no_of_sectors=self.no_of_sectors,
            colors=self.colors,
            output_path=self.output_path
        )

    def export_layout(self):
        """
        Exports a pre-designed QGIS layout as an image.
        """
        LayoutImageExporter(self.output_path, self.labels, self.noOfRasterLayers, self.city)

    def run_all(self):
        """
        Executes the entire processing pipeline in sequence and updates the progress bar in the UI.
        """
        self.load_layers()
        QCoreApplication.processEvents()
        self.dlg.progressBar.setValue(10)
        
        self.save_raster_images()
        QCoreApplication.processEvents()
        self.dlg.progressBar.setValue(30)
        
        self.save_overlay_layer()
        QCoreApplication.processEvents()
        self.dlg.progressBar.setValue(35)
        
        self.yearArea()
        
        self.generate_bar_graph()
        QCoreApplication.processEvents()
        self.dlg.progressBar.setValue(55)
        
        self.generate_radar_chart()
        QCoreApplication.processEvents()
        self.dlg.progressBar.setValue(85)
        
        self.export_layout()