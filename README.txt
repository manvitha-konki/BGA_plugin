# Plugin Name: BGA

A QGIS plugin to analyze built-up area growth over time using multi-temporal raster layers and a polygon vector layer (e.g., administrative boundaries or AOI). This plugin was developed using QGIS Plugin Builder.

---

## 🧭 Overview

This plugin allows users to:
- Load raster layers representing built-up areas for different years
- Load a vector polygon layer (such as districts or wards)
- Map each raster to its corresponding year
- Calculate growth of built-up area over time within each polygon
- Export and them view results 

---

## 🛠 Requirements

- QGIS 3.34 or later
- Input data:
  - Multi-temporal binary raster layers (0: non-built-up, 1: built-up)
  - One polygon vector layer (e.g., districts or AOIs)

---

## 🧪 How to Use

1. Open the plugin from the **Raster** menu in QGIS.
2. Add raster layers to project, if not present already, by clicking on file browser.
3. Select the required raster layer(s) from dropdown.
4. Similarly, add required vector(polygon representing area of interest) layer to project, if not present, by clicking on file browser.
5. Select from dropdown the said vector layer.
6. Click on upload data button.
7. Inside the table, add years and optionally, colors for respective years.
8. Select number of sectors representing directions.
9. Optionally, enter a centroid of AOI.
10. Using file browser, select output path.
11. Click "Ok" to process and generate built-up statistics.
12. Results can be viewed in the path given by the user.


## 📂 Folder Structure

Typical plugin structure:
BGA/
├── __init__.py                       
├── BGA.py                             
├── BGA_dialog.py                       
├── BGA_dialog_base.ui                 
├── core/                             
│   ├── BarGraph.py
│   ├── CityRasterProcessor.py
│   ├── delAttributes.py
│   ├── DirectionalRingGenerator.py
│   ├── LayoutImageExporter.py
│   ├── loadLayers.py
│   ├── radarChart.py
│   ├── SaveOverLaidLayer.py
│   ├── SaveRasterImages.py
│   ├── YearWiseZonalSectorStatsProcessor.py
│   └── ZonalStatisticsProcessor.py
├── icon.png                            
├── i18n/
├── LICENSE.txt                          
├── Makefile                          
├── metadata.txt                       
├── pb_tool.cfg                       
├── plugin_upload.py                    
├── pylintrc                            
├── README.md                           
├── resources.qrc                      
├── resources.py                        
├── scripts/                 
└── tests/                              
    └── test_processor.py



---

## 👨‍💻 Authors

Developed by:

- **Manvitha Konkimalla**
- **Aadya Mahraur**

---

## 🧾 License

This plugin is licensed under the **GNU General Public License v2 or later**. See [LICENSE.txt](./LICENSE.txt) for details.

