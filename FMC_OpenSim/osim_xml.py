
# %%
from pathlib import Path
from tkinter.filedialog import test
import lxml.etree as etree
import pandas as pd
import subprocess


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

    def scale_model(self, scale_xml, scaled_model_path, trc, time_range_sec):
        """run the scale.xml file using opensim-cmd"""

        exe_file = str(Path("C:\\", "OpenSim 4.4", "bin", "opensim-cmd.exe"))
        scale_xml = str(self.path)
        print(exe_file)
        print(scale_xml)


        # in the process of writing this up.
        self.update_scaling_config(scale_xml, scaled_model_path, trc, time_range_sec)

        scale_output = subprocess.call([exe_file, "run-tool", scale_xml], 
                                shell=True,  stdout=subprocess.PIPE, text=True)
        if scale_output!=0:
            print(">>>>>>>>>>>>>> SCALED MODEL NOT PRODUCED <<<<<<<<<<<<<<<<<<")
        else:
            print("scaled model stored at: ", self.path)


    def update_scaling_config(self, scale_xml, scaled_model_path, trc, time_range_sec):

        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(scale_xml, parser)
        root = tree.getroot()

        # Assign variables to the original osim model, the new model name,
        # the .trc file and the time range being used.







        etree.ElementTree(root).write(scale_xml, pretty_print=True)



        pass

class ScaleXML():

    def __init__(self,  scale_xml, trc_file):
        """based on a model template, create a new model"""
        
        self.trc_file = trc_file
        
        self.path = scale_xml
        





# %%
################################################################################
################################ PROTOTYPING ###################################
################################################################################

# ------------------------------------------------------------------------------
# Create some helper functions that will integrate with tests 
# and make them more succinct

repo = Path(__file__).parent.parent
def get_input_path(*args):
    return Path(repo,"tests",  "input", *args)

def get_reference_and_output_paths(test_name, filetype):

    test_name = test_name.replace(" ", "_")

    if filetype.startswith("."):
        pass
    else:
        filetype = "." + filetype

    ref_path = Path(repo,"tests", "reference", test_name+"_reference" + filetype)
    out_path = Path(repo,"tests", "output", test_name+"_output" + filetype)

    return ref_path, out_path
# %%
# ------------------------------------------------------------------------------
# Create new scale_xml
in_trc = get_input_path("trc", "dao_yin.trc")
in_xml = get_input_path("scale_ik_xml", "scaling_mediapipe_model.xml")
ref_xml, out_xml = get_reference_and_output_paths("test_scale_model", "xml")

# test_scale_xml = ScaleXML(in_xml, out_xml, in_trc)
# # print(out_xml)
# # %%
# test_scale_xml.scale_model()
# Navigate xml to find model file