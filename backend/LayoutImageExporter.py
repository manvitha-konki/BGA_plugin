import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from qgis.core import (
    QgsProject, QgsPrintLayout, QgsLayoutItemPicture, QgsLayoutItemLabel,
    QgsLayoutPoint, QgsLayoutSize, QgsUnitTypes, QgsLayoutExporter
)
from PyQt5.QtGui import QFont

from .BarGraph import BarGraph

class LayoutImageExporter:
    """
    Exports a composite layout containing raster snapshots, AOI, bar and radar charts,
    and a growth rate analysis as a single PDF and image.
    """

    def __init__(self, output_path, labels, noOfRasterLayers, city):
        """
        Initializes the exporter and triggers the layout export process.

        Parameters:
            output_path (str): Directory where images and layout will be saved.
            labels (list): List of year labels corresponding to rasters.
            noOfRasterLayers (int): Number of raster layers/images to place.
            city (str): Name of the city or study area.
        """
        self.project = QgsProject.instance()
        self.manager = self.project.layoutManager()
        self.layout_name = 'ImageLayout'
        self.layout = None
        self.output_path = output_path
        self.city = city
        self.labels = labels
        self.noOfRasterLayers = noOfRasterLayers

        # Image paths by rows
        self.image_paths_row1 = [os.path.join(self.output_path, f'{labels[i]}.png') for i in range(self.noOfRasterLayers)]
        self.image_paths_row2 = [
            os.path.join(self.output_path, f'{self.city}_AOI.png'),
            os.path.join(self.output_path, 'barGraph.png'),
            os.path.join(self.output_path, 'radarChart.png')
        ]
        self.image_path_row3 = os.path.join(self.output_path, 'Growth Rate Analysis.png')

        # Image positions in millimeters (x, y, width, height)
        self.image_positions_row1 = [(i * 20, 20, 70, 70) for i in range(self.noOfRasterLayers)]
        self.image_positions_row2 = [
            (30, 50, 70, 70),
            (60, 50, 70, 70),
            (90, 50, 70, 70)
        ]
        self.image_positions_row3 = [(30, 50, 70, 70)]

        self.run()

    def setup_layout(self):
        """
        Initializes a new QGIS print layout after removing any existing layout with the same name.
        """
        for layout in self.manager.printLayouts():
            if layout.name() == self.layout_name:
                self.manager.removeLayout(layout)

        self.layout = QgsPrintLayout(self.project)
        self.layout.setName(self.layout_name)
        self.manager.addLayout(self.layout)
        self.layout.initializeDefaults()

    def save_percentage_image(self):
        """
        Generates and saves a horizontal arrow plot showing percentage change between built-up areas
        of different years.
        """
        obj_values = BarGraph(self.labels, self.city, self.noOfRasterLayers, self.output_path)
        yearStats = obj_values.get_values()
        yearStats = [float(val) for val in yearStats]

        # Calculate percentage change
        changeStats = []
        for i in range(1, len(yearStats)):
            prev = yearStats[i - 1]
            curr = yearStats[i]
            change = ((curr - prev) / prev) * 100 if prev != 0 else 0
            changeStats.append(f"{change:.2f}%")

        fig, ax = plt.subplots(figsize=(10, 2))

        # Arrows and text
        for i in range(len(changeStats)):
            ax.annotate('', xy=(i + 1, 0), xytext=(i, 0),
                        arrowprops=dict(arrowstyle='->,head_width=0.4', lw=5, color='steelblue'))
            ax.text(i + 0.5, 0.1, changeStats[i], ha='center', va='center', fontsize=12,
                    bbox=dict(facecolor='white', edgecolor='steelblue'))

        for i, year in enumerate(self.labels):
            ax.text(i, -0.3, f'Builtup ({year})', ha='center', fontsize=11, fontweight='bold')

        ax.set_xlim(-0.5, len(self.labels) - 0.5)
        ax.set_ylim(-1, 1)
        ax.axis('off')

        plt.tight_layout()
        plt.savefig(self.image_path_row3, dpi=300, transparent=True)

    def add_images_and_labels(self):
        """
        Adds all relevant images and labels to the layout including city title,
        raster snapshots, AOI, bar chart, radar chart, and growth rate chart.
        """
        # Title label
        label = QgsLayoutItemLabel(self.layout)
        label.setText(self.city)
        label.setFont(QFont('Arial', 20))
        label.adjustSizeToText()
        self.layout.addLayoutItem(label)

        page = self.layout.pageCollection().page(0)
        center_x = (page.pageSize().width() - label.sizeForText().width()) / 2
        label.attemptMove(QgsLayoutPoint(center_x, 5, QgsUnitTypes.LayoutMillimeters))

        # First row images (raster snapshots)
        for i, image_path in enumerate(self.image_paths_row1):
            picture_item = QgsLayoutItemPicture(self.layout)
            picture_item.setPicturePath(image_path)
            picture_item.setRect(*self.image_positions_row1[i])
            picture_item.attemptMove(QgsLayoutPoint(20 + i * 70, 20, QgsUnitTypes.LayoutMillimeters))
            picture_item.attemptResize(QgsLayoutSize(50, 50, QgsUnitTypes.LayoutMillimeters))
            self.layout.addLayoutItem(picture_item)

            # Label for each image
            label = QgsLayoutItemLabel(self.layout)
            label.setText(str(self.labels[i]))
            label.adjustSizeToText()
            self.layout.addLayoutItem(label)
            label.attemptMove(QgsLayoutPoint(40 + i * 70, 15, QgsUnitTypes.LayoutMillimeters))

        # Second row: Growth rate plot
        picture_item = QgsLayoutItemPicture(self.layout)
        picture_item.setPicturePath(self.image_path_row3)
        picture_item.setRect(*self.image_positions_row3[0])
        picture_item.attemptMove(QgsLayoutPoint(170, 180, QgsUnitTypes.LayoutMillimeters))
        picture_item.attemptResize(QgsLayoutSize(100, 100, QgsUnitTypes.LayoutMillimeters))
        self.layout.addLayoutItem(picture_item)

        # Third row: AOI, bar graph, radar chart
        for i, image_path in enumerate(self.image_paths_row2):
            picture_item = QgsLayoutItemPicture(self.layout)
            picture_item.setPicturePath(image_path)
            picture_item.setRect(*self.image_positions_row2[i])
            picture_item.attemptMove(QgsLayoutPoint(20 + i * 90, 100, QgsUnitTypes.LayoutMillimeters))
            picture_item.attemptResize(QgsLayoutSize(70, 70, QgsUnitTypes.LayoutMillimeters))
            self.layout.addLayoutItem(picture_item)

    def export_to_pdf(self):
        """
        Exports the final layout as both a high-resolution JPEG and PDF.
        """
        image_settings  = QgsLayoutExporter.ImageExportSettings()
        pdf_settings = QgsLayoutExporter.PdfExportSettings()
        image_settings.dpi = 1500

        jpeg_path = os.path.join(self.output_path, f"{self.city}_UBA.jpeg")
        pdf_path = os.path.join(self.output_path, f"{self.city}_UBA.pdf")

        exporter = QgsLayoutExporter(self.layout)
        exporter.exportToImage(jpeg_path, image_settings)
        exporter.exportToPdf(pdf_path, pdf_settings)

    def run(self):
        """
        Full pipeline to:
        - Set up layout
        - Create percentage change image
        - Add all visual components to layout
        - Export final layout as PDF and image
        """
        self.setup_layout()
        self.save_percentage_image()
        self.add_images_and_labels()
        self.export_to_pdf()
        print("Layout exported to PDF.")