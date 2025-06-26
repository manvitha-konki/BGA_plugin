from qgis.core import (
    QgsProject, QgsMapSettings, QgsRectangle, QgsMapRendererCustomPainterJob, QgsLayoutUtils
)
from qgis.utils import iface
from PyQt5.QtGui import QImage, QPainter, QColor
from PyQt5.QtCore import QSize

import os, math

class SaveRasterImages:
    count = 0

    def __init__(self, city, output_path, years, image_size=(5000, 5000), background_color=(255, 255, 255, 0)):
        """
        Initialize the SaveRasterImages object and immediately save the raster image for the current count.

        :param city: Name of the city (not used directly but can be useful contextually)
        :param outputPath: Directory where the raster image should be saved
        :param years: List of year labels used in naming output files
        :param image_size: Tuple representing image width and height in pixels
        :param background_color: Tuple (R, G, B, A) defining background color for the image
        """
        self.image_size = QSize(*image_size)
        self.output_path = output_path
        self.years = years
        self.bg_color = QColor(*background_color)
        self.aoi_layer_name = 'AOI'
        self.project = QgsProject.instance()
        SaveRasterImages.count += 1
        self.save_image(SaveRasterImages.count, f'{years[SaveRasterImages.count - 1]}')

    def save_image(self, raster_index, file_name):
        """
        Renders the specified raster layer and AOI with MultiRingView into an image and saves it as PNG.

        :param raster_index: Index used to identify the raster layer (expects layer named like 'rasterImage1')
        :param file_name: File name (without extension) for the output image
        :param output_dir: Directory path where the image should be saved
        :return: None
        """
        # Fetch layers from the project
        
        raster_layer = self.project.mapLayersByName(f"rasterImage{raster_index}")[0]
        aoi_layer = self.project.mapLayersByName(self.aoi_layer_name)[0]
        multiRingView_layer = self.project.mapLayersByName('MultiRingsView')[0]

        if not raster_layer:
            print(f"[ERROR] Raster layer 'rasterImage{raster_index}' not found.")
            return

        # Create the output image with transparent background
        img = QImage(self.image_size, QImage.Format_ARGB32_Premultiplied)
        img.fill(self.bg_color.rgba())

        # Set up the painter to draw on the image
        painter = QPainter()
        painter.begin(img)
        painter.setRenderHint(QPainter.Antialiasing)

        # Configure map rendering settings
        ms = QgsMapSettings()
        ms.setBackgroundColor(self.bg_color)

        # Layers to include in rendering        
        layers_to_render = [raster_layer]
        if aoi_layer:
            layers_to_render.append(aoi_layer)
        layers_to_render.append(multiRingView_layer)
        
        ms.setLayers(layers_to_render)

        # Use extent of MultiRingsView layer to define rendering area
        rect = multiRingView_layer.extent()
        rect.scale(1)
        ms.setExtent(rect)

        # Set output image size
        ms.setOutputSize(self.image_size)

        # Perform the rendering job
        job = QgsMapRendererCustomPainterJob(ms, painter)
        job.start()
        job.waitForFinished()

        painter.end()

        # Save the image as PNG
        full_path = f"{self.output_path}/{file_name}.png"
        img.save(full_path)
        print(f"[INFO] Image saved: {full_path}")