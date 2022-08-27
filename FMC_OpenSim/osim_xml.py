
# %%
from pathlib import Path
from tkinter.filedialog import test
import lxml.etree as etree
import pandas as pd



class OsimModel():

    def __init__(self, osim_template, new_osim_path=""):
        """based on a model template, create a new model"""
        parser = etree.XMLParser(remove_blank_text=True)
        
        if new_osim_path == "":
            self.path = osim_template
        else:
            self.path = new_osim_path

        self.tree = etree.parse(osim_template, parser)
        self.root = self.tree.getroot()


    def get_joint_locations(self):
        """return a dataframe of joints, parent bodies, and translations"""
        joint_locations = []

        for joint in self.root.xpath('Model/JointSet/objects')[0]:
            joint_name = joint.attrib['name']

            for frame in joint.xpath("frames/PhysicalOffsetFrame"):
                # physical_offset_frame = frame.attrib['name']
                translation = frame.xpath("translation")[0].text
                socket_parent = frame.xpath("socket_parent")[0].text
                # addition of the ' in translation is to avoid errors if opened in excel
                joint_locations.append([joint_name, socket_parent, "'" + translation])
        
        
        columns = [["JointName", "Segment", "Location_in_Segment"]]

        return pd.DataFrame(joint_locations, columns=columns)


    def create_joint_loc_csv(self, csv_path):
        """save a csv of joint centers and parent bodies"""
        joint_loc_df = self.get_joint_locations()
        joint_loc_df.to_csv(csv_path, index=False)


    def add_marker(self, marker_name, location_text, parent_frame):
        """add a single marker to an osim file, saving new results"""

        # go to parent of markers
        marker_parent = self.root.xpath("Model/MarkerSet/objects")[0]
        marker_parent.text = None #necessary for maintaining new lines and tabs, still unsure why
        
        # specify new marker info
        new_marker = etree.SubElement(marker_parent, "Marker")
        
        # marker_name = 'left_eye'
        # location_text = '0.069857071913979135 0.55697305173123246 -0.029007770243867158'
        # parent_frame = "/bodyset/head"

        new_marker.attrib['name'] = marker_name

        socket_parent_frame = etree.SubElement(new_marker, "socket_parent_frame")
        location = etree.SubElement(new_marker, "location")
        fixed = etree.SubElement(new_marker, "fixed")

        new_marker.text = None
        socket_parent_frame.text = parent_frame
        location.text = location_text
        fixed.text = "true"

        new_marker.attrib['name'] = marker_name
        new_marker.attrib['name'] = marker_name
        etree.ElementTree(self.root).write(self.path, pretty_print=True)

    def add_ModelLandmarkMap(self, model_landmark_map_path):
        pass



#####################################
# Prototyping OsimModel.add_ModelLandmarkMap(config_xlsx)
#####################################

# %%
repo = Path(__file__).parent.parent

test_model_path =  Path(repo, "tests","osim_models", "mediapipe_fullbody_model_no_markers.osim")
test_model = OsimModel(test_model_path)
model_landmark_map_path = Path(repo, "FMC_OpenSim", "ModelLandmarkMap.xlsx")
# create a dictionary from the xlsx following https://www.marsja.se/your-guide-to-reading-excel-xlsx-files-in-python/


# %%
# remove markers from element tree
for marker in test_model.root.xpath("Model/MarkerSet/objects")[0]:
    print(marker.attrib['name'])
    marker.getparent().remove(marker)

etree.ElementTree(test_model.root).write(test_model_path, pretty_print=True)


# %%
# add markers back into osim file
marker_parent = test_model.root.xpath("Model/MarkerSet/objects")[0]

marker_parent.text = None

new_marker = etree.SubElement(marker_parent, "Marker")

marker_name = 'left_eye'
location_text = '0.069857071913979135 0.55697305173123246 -0.029007770243867158'
parent_frame = "/bodyset/head"

new_marker.attrib['name'] = marker_name

socket_parent_frame = etree.SubElement(new_marker, "socket_parent_frame")
location = etree.SubElement(new_marker, "location")
fixed = etree.SubElement(new_marker, "fixed")

new_marker.text = None
socket_parent_frame.text = parent_frame
location.text = location_text
fixed.text = "true"

new_marker.attrib['name'] = marker_name
new_marker.attrib['name'] = marker_name
etree.ElementTree(test_model.root).write(test_model_path, pretty_print=True)
# %%