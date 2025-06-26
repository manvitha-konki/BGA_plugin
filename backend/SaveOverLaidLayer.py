from qgis.core import QgsProject, QgsMapSettings, QgsRectangle, QgsMapRendererCustomPainterJob
from PyQt5.QtGui import QImage, QPainter, QColor
from PyQt5.QtCore import QSize

class SaveOverLaidLayer:
    def __init__(self, city, no_of_raster_layers, output_path):
        """
        Initialize the SaveOverLaidLayer object and start creating the image.

        Parameters:
            city (str): Name of the city, used to name the output image file.
            no_of_raster_layers (int): Number of raster layers to overlay.
            output_path (str): Directory path to save the output image.
        """
        self.output_path = output_path
        self.city = city
        self.file_name = f'{self.city}_AOI'
        self.no_of_raster_layers = no_of_raster_layers
        self.create_image()  # Automatically create the image on initialization
        
    def create_image(self):
        """
        Create and save a composited image by overlaying multiple raster layers
        along with AOI and MultiRingsView layers.
        """
        # Create a blank image with ARGB32 format and given size
        img = QImage(QSize(5000, 5000), QImage.Format_ARGB32_Premultiplied)

        # Set transparent background color
        color = QColor(255, 255, 255, 0)
        img.fill(color.rgba())

        # Initialize QPainter to draw on the image
        p = QPainter()
        p.begin(img)
        p.setRenderHint(QPainter.Antialiasing)

        # Prepare map settings for rendering
        ms = QgsMapSettings()
        ms.setBackgroundColor(color)

        # Get extent from 'MultiRingsView' layer and set it on map settings
        layer = QgsProject.instance().mapLayersByName('MultiRingsView')[0]
        rect = layer.extent()
        rect.scale(1)
        ms.setExtent(rect)

        # List to hold raster layers for rendering
        layers = []

        # Loop from highest raster layer index down to 1
        for i in range(self.no_of_raster_layers, 0, -1):
            layers.append(QgsProject.instance().mapLayersByName(f'rasterImage{i}'))
            # Set the current raster layer on map settings
            ms.setLayers([layers[self.no_of_raster_layers - i][0]])

            # Set output image size
            ms.setOutputSize(img.size())

            # Render current layer onto the image via QPainter
            render = QgsMapRendererCustomPainterJob(ms, p)
            render.start()
            render.waitForFinished()

        # Append AOI and MultiRingsView layers to the layers list
        layers.append(QgsProject.instance().mapLayersByName("AOI"))
        layers.append(QgsProject.instance().mapLayersByName('MultiRingsView'))
    
        # Render AOI layer
        ms.setLayers([layers[self.no_of_raster_layers][0]])
        render = QgsMapRendererCustomPainterJob(ms, p)
        render.start()
        render.waitForFinished()
        
        # Render MultiRingsView layer
        ms.setLayers([layers[self.no_of_raster_layers+1][0]])
        render = QgsMapRendererCustomPainterJob(ms, p)
        render.start()
        render.waitForFinished()

        # Finish painting
        p.end()

        # Construct full output path and save the composited image
        self.output_path = f"{self.output_path}/{self.file_name}.png"
        img.save(self.output_path)