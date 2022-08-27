
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


class ScaleXML():

    def __init__(self,  scale_template, new_scale_path, trc_file ):
        """based on a model template, create a new model"""
        
        # if new_scale_path == "":
        #     self.path = scale_template
        # else:
        
        self.trc_file = trc_file
        
        self.path = new_scale_path
        
        parser = etree.XMLParser(remove_blank_text=True)
        self.tree = etree.parse(scale_template, parser)
        self.root = self.tree.getroot()
        etree.ElementTree(self.root).write(self.path, pretty_print=True)




    def scale_model(self):
        """run the scale.xls file using opensim-cmd"""

        exe_file = str(Path("C", "OpenSim 4.4", "bin", "opensim-cmd.exe"))
        xml_file = str(self.path)
        print(exe_file)
        print(xml_file)

        scale_output = subprocess.run([exe_file, "run-tool", xml_file], 
                                shell=True,  stdout=subprocess.PIPE, text=True)
        print("Return Code: " + str(scale_output.returncode))
        print("Std Err: " + str(scale_output.stderr))
        print(scale_output)
        # pass

    # def assign_trc(self, trc_file):


    # def assign_model(self, osim_file):



# %%
################################################################################
################################ PROTOTYPING ###################################
################################################################################

# ------------------------------------------------------------------------------
# Create some helper functions that will integrate with tests 
# and make them more succinct

repo = Path(__file__).parent.parent
print(repo)
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
ref_xml, out_xml = get_reference_and_output_paths("test_assign_model", "xml")

# print(out_xml)
test_scale_xml = ScaleXML(in_xml, out_xml, in_trc)
test_scale_xml.scale_model()
# %%
# Navigate xml to find model file