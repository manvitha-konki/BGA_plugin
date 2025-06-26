from qgis.core import QgsPointXY, QgsGeometry, QgsFeature, QgsVectorLayer, QgsField, QgsProject, QgsFillSymbol
from qgis.PyQt.QtCore import QVariant
import math, processing

class DirectionalRingGenerator:
    """
    Generates a single ring divided into directional segments (like compass wedges) 
    around a centroid point based on a vector layer's extent. Can optionally display 
    a 'view-only' version or persist a named vector layer.
    """
    def __init__(self, iface, city, no_of_segments, centroid_point, view=True):
        """
        :param iface: QGIS interface instance
        :param city: City name (used for naming or context)
        :param no_of_segments: Number of directional segments (e.g., 4, 8, 16)
        :param centroid_point: User-specified center point, or None to auto-calculate
        :param view: If True, generates a temporary 'MultiRingsView' layer for visualization only
        """
        self.iface = iface
        self.city = city
        self.file_name = 'AOI'
        self.view = view
        self.no_of_segments = no_of_segments
        self.centroid_point = centroid_point
        self.vector_layer = QgsProject.instance().mapLayersByName(self.file_name)[0]

        # Offset ensures segments are centered for statistics; skipped in view mode
        self.offset = 360 / (2 * self.no_of_segments) if not view else 0

        # Compass directions, adjusted based on number of segments
        self.directions = [
            "E", "ENE", "NE", "NNE", "N", "NNW", "NW", "WNW",
            "W", "WSW", "SW", "SSW", "S", "SSE", "SE", "ESE"
        ]
        self.directions = self.directions[::16 // self.no_of_segments]

    def get_radius(self):
        """
        Determines the radius of the ring based on the AOI extent.
        :return: Radius (max distance from centroid)
        """
        ext = self.vector_layer.extent()
        
        # Use max distance from centroid to bounding box corners
        corners = [
            (ext.xMinimum(), ext.yMinimum()),
            (ext.xMaximum(), ext.yMinimum()),
            (ext.xMinimum(), ext.yMaximum()),
            (ext.xMaximum(), ext.yMaximum())
        ]

        distances = [
            math.dist([self.centroid_point.x(), self.centroid_point.y()], [x, y])
            for x, y in corners
        ]

        return max(distances)


    def get_centroid(self):
        """
        Computes the centroid of the AOI layer.
        If the centroid is not inside the polygon, returns a point inside it.
        :return: QgsPointXY representing the centroid or a fallback interior point
        """
        params = {'INPUT': self.vector_layer, 'OUTPUT': 'memory:'}

        if QgsProject.instance().mapLayersByName('centroid') == []:
            resultDict = processing.run("native:centroids", params)
            result = resultDict['OUTPUT']
            result.setName('centroid')
            QgsProject.instance().addMapLayer(result)
        else:
            result = QgsProject.instance().mapLayersByName('centroid')[0]

        centroid_geom = None
        for f in result.getFeatures():
            centroid_geom = f.geometry()

        aoi_feature = next(self.vector_layer.getFeatures())  # Assuming single AOI
        aoi_geom = aoi_feature.geometry()

        # Check if centroid lies within AOI
        if centroid_geom and aoi_geom.contains(centroid_geom):
            return QgsPointXY(centroid_geom.asPoint().x(), centroid_geom.asPoint().y())
        else:
            # Use pointOnSurface() or interiorPoint() as a fallback inside AOI
            interior_point = aoi_geom.pointOnSurface()  # Always returns a point inside
            return QgsPointXY(interior_point.asPoint().x(), interior_point.asPoint().y())

    def create_ring(self, center_point, radius):
        """
        Creates a polygonal ring (circle approximation) using center and radius.
        :param center_point: Center point of the ring
        :param radius: Radius of the ring
        :return: QgsGeometry polygon representing the ring
        """
        angles = [(360 / self.no_of_segments * i) - self.offset for i in range(self.no_of_segments)]
        ring_points = [
            QgsPointXY(
                center_point.x() + radius * math.cos(math.radians(angle)),
                center_point.y() + radius * math.sin(math.radians(angle))
            ) for angle in angles
        ]
        return QgsGeometry.fromPolygonXY([ring_points])

    def create_segment(self, center_point, start_angle, end_angle):
        """
        Creates a triangular segment (wedge) from center outwards.
        :param center_point: Center of the circle
        :param start_angle: Start angle of the wedge
        :param end_angle: End angle of the wedge
        :return: QgsGeometry polygon for the segment
        """
        return QgsGeometry.fromPolygonXY([[  # Triangle from center to outer arc
            QgsPointXY(center_point.x(), center_point.y()),
            QgsPointXY(center_point.x() + math.cos(math.radians(start_angle)),
                       center_point.y() + math.sin(math.radians(start_angle))),
            QgsPointXY(center_point.x() + math.cos(math.radians(end_angle)),
                       center_point.y() + math.sin(math.radians(end_angle))),
            QgsPointXY(center_point.x(), center_point.y())
        ]])

    def cut_ring_into_segments(self, ring):
        """
        Cuts the ring into directional wedge segments using geometric intersection.
        :param ring: The full ring geometry
        :return: List of tuples with (direction name, segment geometry)
        """
        segments = []
        centroid = ring.centroid().asPoint()
        for i in range(self.no_of_segments):
            start_angle = i * (360 / self.no_of_segments) - self.offset
            end_angle = (i + 1) * (360 / self.no_of_segments) - self.offset
            segment_geom = ring.intersection(self.create_segment(centroid, start_angle, end_angle))
            segments.append((self.directions[i], segment_geom))
        return segments

    def create_buffer(self):
        radius = self.get_radius()
        angle = 360 / self.no_of_segments
        distance = radius * math.cos(math.radians(angle / 2))
        return radius - distance

    def generate_layer(self):
        """
        Main method to generate the directional ring vector layer (in memory).
        Adds attributes and symbols, and pushes to the QGIS project.
        """
        # Use provided centroid or compute it
        center = self.centroid_point = QgsPointXY(self.centroid_point) if self.centroid_point else self.get_centroid()
        
        radius = self.get_radius() + self.create_buffer()
        
        # Determine layer name based on view mode
        layer_name = "MultiRingsView" if self.view else "MultiRings"
        vl = QgsVectorLayer("Polygon", layer_name, "memory")
        pr = vl.dataProvider()

        # Add direction field
        pr.addAttributes([QgsField("Direction", QVariant.String)])
        vl.updateFields()

        # Currently generates just 1 ring (can be expanded)
        for r in range(1, 2):
            ring = self.create_ring(center, radius * r)
            segments = self.cut_ring_into_segments(ring)
            for direction, segment in segments:
                if not segment.isEmpty():
                    feat = QgsFeature()
                    feat.setGeometry(segment)
                    feat.setAttributes([direction])
                    pr.addFeature(feat)

        # Add layer to project
        vl = QgsProject.instance().addMapLayer(vl)

        # Optional styling: no fill (for transparent segments)
        symbol = QgsFillSymbol.createSimple({
            'outline_width': '1.0',
            'style': 'no'  # No fill brush
        })
        vl.renderer().setSymbol(symbol)
        vl.triggerRepaint()

