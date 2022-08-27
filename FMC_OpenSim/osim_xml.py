
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
        
        column_names =  ["JointName", "Segment", "Location_in_Segment"]

        return pd.DataFrame(joint_locations, columns=column_names)

    def create_joint_loc_csv(self, csv_path):
        """save a csv of joint centers and parent bodies"""
        joint_loc_df = self.get_joint_locations()
        joint_loc_df.to_csv(csv_path, index=False)

    def create_joint_loc_xlsx(self, xlsx_path):
        """save an xlsx of joint centers and parent bodies"""
        joint_loc_df = self.get_joint_locations()
        joint_loc_df.to_excel(xlsx_path, index=False)

    def add_marker(self, marker_name, location_text, parent_frame):
        """add a single marker to an osim file, saving new results"""

        # go to parent of markers
        marker_parent = self.root.xpath("Model/MarkerSet/objects")[0]
        marker_parent.text = None #necessary for maintaining new lines and tabs, still unsure why
        
        # specify new marker info
        new_marker = etree.SubElement(marker_parent, "Marker")
        
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

    def add_ModelLandmarkMap(self, model_landmark_map_path, map_sheet_name="Sheet1"):
        """given a spreadsheet of landmark positions relative to a segment, add them"""
        # remove all markers from element tree
        for marker in self.root.xpath("Model/MarkerSet/objects")[0]:
            # print(marker.attrib['name'])
            marker.getparent().remove(marker)

        landmark_map = pd.read_excel(model_landmark_map_path, map_sheet_name)

        for index, row in landmark_map.iterrows():
            # JointName = row['JointName']
            Segment = row['Segment']
            Location_in_Segment = row['Location_in_Segment']
            Location_in_Segment = Location_in_Segment.replace("'", "")
            Landmark = row['Landmark']

            self.add_marker(Landmark, Location_in_Segment, Segment)


class ScaleXML():

    def __init__(self, scale_template, new_scale_path=""):
        """based on a model template, create a new model"""
        parser = etree.XMLParser(remove_blank_text=True)
        
        if new_scale_path == "":
            self.path = scale_template
        else:
            self.path = new_scale_path

        self.tree = etree.parse(scale_template, parser)
        self.root = self.tree.getroot()

##########################################################
# Prototyping OsimModel.add_ModelLandmarkMap(config_xlsx)
##########################################################
