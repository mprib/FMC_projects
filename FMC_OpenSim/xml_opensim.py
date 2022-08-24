from pathlib import Path
import xml.etree.ElementTree as ET
import xml.dom.minidom as md

# Don't worry about this yet, Mac.
# Dive straight into the object model when you know what you are doing
# class OsimModel():

#     def __init__(self, osim_path):
#         self.osim_path = osim_path
#         self.model_tree = ET.parse(self.osim_path)
    
#     def get_markers(self):
#         pass

osim_model = open(Path("tests\osim_models\mediapipe_fullbody_model.osim"))

xmlparse = md.parse(osim_model)

# markers = xmlparse.get

print(xmlparse)

markers = xmlparse.getElementsByTagName("Marker")

model_markers = []

for m in markers:
    model_markers.append(m.getAttribute("name"))

print(model_markers)