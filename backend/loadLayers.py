from qgis.core import QgsPalettedRasterRenderer, QgsGradientColorRamp, QgsFillSymbol, QgsRasterLayer, QgsVectorLayer, QgsProject
from PyQt5.QtGui import QColor
from .DirectionalRingGenerator import DirectionalRingGenerator
import matplotlib.pyplot as plt

class loadLayers:
    """
    This class handles loading and styling of raster and vector (AOI) layers in QGIS, 
    and generates a directional ring overlay for visualizing urban segmentation.

    :param iface: QGIS interface object
    :param raster_paths: List of file paths to raster layers
    :param vector_path: Path to vector layer (e.g., AOI)
    :param city: Name of the city (used for layer naming and folder structure)
    :param no_of_sectors: Number of directional segments (e.g., 4, 8, 16)
    :param no_of_raster_layers: Total number of raster layers
    :param colors: List of RGBA color strings for each raster layer
    :param centroid_point: Optional centroid point to center the directional rings
    """
    def __init__(self, iface, raster_paths, vector_path, city, no_of_sectors, no_of_raster_layers, colors, centroid_point):
        self.iface = iface
        self.raster_paths = raster_paths
        self.vector_path = vector_path
        self.city = city
        self.no_of_sectors = no_of_sectors
        self.no_of_raster_layers = no_of_raster_layers
        self.colors = colors
        self.centroid_point = centroid_point

        # Optional: color map from matplotlib (not used directly)
        cmap = plt.get_cmap('tab20')

        # Apply styles and load layers
        self.apply_styling_raster()
        self.apply_styling_AOI()
        self.applyMultiRingsView()

    def applyMultiRingsView(self):
        """
        Loads and displays the directional ring view (MultiRingsView) based on centroid and segment count.
        Also sets the map canvas extent to fit the new layer.
        """
        generator = DirectionalRingGenerator(self.iface, self.city, self.no_of_sectors, self.centroid_point, view=True)
        generator.generate_layer()

        layer = QgsProject.instance().mapLayersByName('MultiRingsView')[0]
        canvas = self.iface.mapCanvas()
        canvas.setExtent(layer.extent())
        canvas.refresh()

    def create_props(self, color2):
        """
        Creates a gradient color ramp dictionary with defined stops and endpoints.

        :param color2: RGBA color string (e.g., "255,0,0,255")
        :return: Dictionary of color ramp properties
        """
        return {
            'color1': '43,131,186,0',  # Start color
            'color2': color2,          # End color (input)
            'discrete': '0',           # Smooth gradient
            'rampType': 'gradient',
            'stops': '0.25;171,221,164,255:0.5;255,255,191,255:0.75;253,174,97,255'
        }

    def apply_styling_raster(self):
        """
        Loads all raster layers in reverse order and applies a gradient-based styling using a color ramp.
        """
        for i, raster_path in enumerate(self.raster_paths[::-1]):
            # Create color ramp properties using custom color for this layer
            props = self.create_props(self.colors[i])
            color_ramp = QgsGradientColorRamp().create(props)

            # Load the raster layer
            layer = QgsRasterLayer(raster_path, f"rasterImage{self.no_of_raster_layers-i}")
            if layer.isValid():
                QgsProject.instance().addMapLayer(layer)

            # Generate and apply paletted renderer from gradient (used here per original logic)
            classes = QgsPalettedRasterRenderer.classDataFromRaster(layer.dataProvider(), 1, color_ramp)
            renderer = QgsPalettedRasterRenderer(layer.dataProvider(), 1, classes)
            layer.setRenderer(renderer)
            layer.triggerRepaint()

            print(f"[INFO] Styled layer: {raster_path}")

    def apply_styling_AOI(self):
        """
        Loads the AOI vector layer and applies a transparent fill with thick outline styling.
        """
        vector_layer = QgsVectorLayer(self.vector_path, "AOI", "ogr")
        if not vector_layer.isValid():
            print(f"[ERROR] Failed to load vector layer: {self.vector_path}")
            return

        QgsProject.instance().addMapLayer(vector_layer)
        print(f"[INFO] Loaded AOI layer for: {self.city}")

        # Apply "No Brush" fill style (outline only)
        symbol = QgsFillSymbol.createSimple({
            'outline_width': '2.0',
            'style': 'no'  # "No brush" fill
        })
        vector_layer.renderer().setSymbol(symbol)
        vector_layer.triggerRepaint()

        print(f"[INFO] Styled AOI layer for: {self.city} (No Brush)")
