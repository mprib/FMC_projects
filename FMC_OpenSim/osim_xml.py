
# %%
from pathlib import Path
from tkinter.filedialog import test
import lxml.etree as etree
import pandas as pd
import subprocess

from pyrsistent import get_in


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

    def __init__(self, scale_xml_template, new_scale_xml_path):
        """based on an input scaling xml template, create a new template"""
        
        parser = etree.XMLParser(remove_blank_text=True)
    
        self.tree = etree.parse(scale_xml_template, parser)
        self.path = new_scale_xml_path

        self.root = self.tree.getroot()
        etree.ElementTree(self.root).write(self.path, pretty_print=True)


    def update_xml(self):
        etree.ElementTree(self.root).write(self.path, pretty_print=True)

    def configure_xml(self, template, trc, scale_time_range, xml_outout):


        pass

    def scale_model(self):
        """run the scale.xml file using opensim-cmd"""

        exe_file = str(Path("C:\\", "OpenSim 4.4", "bin", "opensim-cmd.exe"))
        scale_xml = str(self.path)

        scale_output = subprocess.call([exe_file, "run-tool", scale_xml], 
                                shell=True,  stdout=subprocess.PIPE, text=True)
        if scale_output:
            print(">>>>>>>>>>>>>> SCALED MODEL NOT PRODUCED <<<<<<<<<<<<<<<<<<")
        else:
            print("scaled model stored at: ", self.path)



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

xml_template = get_input_path("scale_ik_xml", "scale_mediapipe_model.xml")
reference, xml_output = get_reference_and_output_paths("test_configure_xml", ".xml")

trc_input = get_input_path("trc", "dao_yin.trc")
input_model_path = get_input_path("osim_models", "mediapipe_fullbody_model.osim")

# I am realizing that the model placer component may be minimally important here
# as there is not human variability in marker placement
# the ms and mp models are currently the same

# ms refers to "ModelScaler"
ms_ref_model, ms_output_model = get_reference_and_output_paths("test_configure_xml", ".osim")
ms_time_range = [0, 15]


# mp refers to "MarkerPlacer"
mp_ref_model, mp_output_model = get_reference_and_output_paths("test_configure_xml", ".osim")
mp_time_range = [0, 15]



newScaleXML = ScaleXML(xml_template, xml_output)

newScaleXML.root.xpath('ScaleTool/GenericModelMaker/model_file')[0].text = str(input_model_path)
newScaleXML.root.xpath('ScaleTool/ModelScaler/marker_file')[0].text = str(trc_input)
newScaleXML.root.xpath('ScaleTool/ModelScaler/output_model_file')[0].text = str(ms_output_model)
newScaleXML.root.xpath('ScaleTool/ModelScaler/time_range')[0].text = f'{ms_time_range[0]} {ms_time_range[1]}'

newScaleXML.root.xpath('ScaleTool/MarkerPlacer/marker_file')[0].text = str(trc_input)
newScaleXML.root.xpath('ScaleTool/MarkerPlacer/output_model_file')[0].text = str(mp_output_model)
newScaleXML.root.xpath('ScaleTool/MarkerPlacer/time_range')[0].text = f'{mp_time_range[0]} {mp_time_range[1]}'

# etree.ElementTree(newScaleXML.root).write(newScaleXML.path, pretty_print=True)

newScaleXML.update_xml()

# for element in newScaleXML.root.xpath('ScaleTool/GenericModelMaker/model_file'):
#     print(element)obs

# test_scale_xml = ScaleXML(in_xml, out_xml, in_trc)
# # print(out_xml)
# # %%
# test_scale_xml.scale_model()
# Navigate xml to find model file
# %%
newScaleXML.path = xml_output
newScaleXML.scale_model()
# %%
