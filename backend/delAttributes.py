from qgis.core import QgsProject, QgsVectorLayer
from qgis.utils  import iface

# To clear any data present before

class delAttributes:
    """
    A class to delete all attributes from a vector layer except 'FID' and 'geometry'.
    """

    def __init__(self, layer=None):
        """
        Initializes the class with the provided vector layer or defaults to the active layer.
        """
        self.layer = layer or iface.activeLayer()  # Use provided layer or fallback to the active layer
        self.clean_attributes()                    # Start the cleaning process

    def clean_attributes(self):
        """
        Deletes all fields from the vector layer except 'FID' and 'geometry'.
        """
        # Check if layer is valid and is a vector layer
        if self.layer and self.layer.isValid() and self.layer.type() == QgsVectorLayer.VectorLayer:
            self.layer.startEditing()  # Start editing the layer

            fields = self.layer.fields()
            # Create a list of field names to delete (excluding 'FID' and 'geometry')
            fields_to_delete = [field.name() for field in fields if field.name() not in ['FID', 'geometry']]

            # Delete each selected attribute
            for field_name in fields_to_delete:
                self.layer.deleteAttribute(self.layer.fields().indexOf(field_name))

            self.layer.commitChanges()  # Commit changes to make them permanent
        else:
            print("The layer is not a valid vector layer.")  # Fallback message if layer is invalid