
# %%
from pathlib import Path
import shutil
from cv2 import scaleAdd
import lxml.etree as etree
import pandas as pd
import subprocess


class OsimModelTemplate():
    """
    A set of tools for interacting with and modifying an .osim template.
    This would be primarily useful for rare template creation/modification. 
    Not as something that would be regularly used in a typical workflow
    """
    
    def __init__(self, osim_template, new_osim_path=""):
        """based on a model template, create a new model"""
        self.xml_parser = etree.XMLParser(remove_blank_text=True)
    
        if new_osim_path == "":
            self.osim_path = osim_template
        else:
            self.osim_path = new_osim_path

        self.osim_tree = etree.parse(osim_template, self.xml_parser)
        self.osim_root = self.osim_tree.getroot()


    def get_joint_locations(self):
        """return a dataframe of joints, parent bodies, and translations"""
        joint_locations = []
        

        for joint in self.osim_root.xpath('Model/JointSet/objects')[0]:
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
        marker_parent = self.osim_root.xpath("Model/MarkerSet/objects")[0]
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
        etree.ElementTree(self.osim_root).write(self.osim_path, pretty_print=True)

    def add_ModelLandmarkMap(self, model_landmark_map_path, map_sheet_name="Sheet1"):
        """given a spreadsheet of landmark positions relative to a segment, add them"""
        # remove all markers from element tree
        for marker in self.osim_root.xpath("Model/MarkerSet/objects")[0]:
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
    


class OsimModel():
    """
    A class to scale a model based on FMC trajectory data (in .trc format), 
    and then run inverse kinematics on it. Scaling and IK template xml files 
    need to be configured in OpenSim prior to initiating these methods, but
    reconfiguration should not be necessary once the original osim model template
    is finalized.

    A working directory is setup to store all created files
    """


    def __init__(self, osim_template, working_directory):
        """based on an input osim template, create a new model"""
        
        self.osim_template = osim_template
        self.working_directory = working_directory
        self.osim_path = Path(self.working_directory, "unscaled_model.osim")

        shutil.copy(self.osim_template, self.osim_path)

        self.parser = etree.XMLParser(remove_blank_text=True)

    
    def configure_scaling(self, scale_xml_template, trc, time_range):
        """
        given a scaling template (which should change little once configured)
        and trc and time range, create a new temp scale.xml
        """

        self.scale_xml = Path(self.working_directory, "scale.xml")
        self.scaled_osim_path = Path(self.working_directory, "scaled_model.osim")
        shutil.copy(scale_xml_template, self.scale_xml)

        self.scaling_tree = etree.parse(self.scale_xml, self.parser)
        self.scaling_root = self.scaling_tree.getroot()
        
        self.scaling_root.xpath('ScaleTool/GenericModelMaker/model_file')[0].text = str(self.osim_path)
        self.scaling_root.xpath('ScaleTool/ModelScaler/marker_file')[0].text = str(trc)
        self.scaling_root.xpath('ScaleTool/ModelScaler/output_model_file')[0].text = str(self.scaled_osim_path)
        self.scaling_root.xpath('ScaleTool/ModelScaler/time_range')[0].text = f'{time_range[0]} {time_range[1]}'
       
        # write scaling tree to workign directory
        etree.ElementTree(self.scaling_root).write(self.scale_xml, pretty_print=True)

    def scale_model(self):
        """create scaled model by runing scale.xml using opensim-cmd"""

        exe_file = str(Path("C:\\", "OpenSim 4.4", "bin", "opensim-cmd.exe"))
        scale_xml = str(self.scale_xml)

        scale_output = subprocess.run([exe_file, "run-tool", scale_xml], 
                                shell=True,  stdout=subprocess.PIPE, text=True)

        print("stdout: " + str(scale_output.stdout))



    def configure_ik(self, ik_template, trc, time_range, mot_path):
        print("trc: " + trc._str)

        self.ik_xml = Path(self.working_directory, "inverse_kinematics.xml")

        shutil.copy(ik_template, self.ik_xml)

        self.ik_tree = etree.parse(self.ik_xml, self.parser)
        self.ik_root = self.ik_tree.getroot()
        
        self.ik_root.xpath('InverseKinematicsTool/model_file')[0].text = str(self.scaled_osim_path)
        self.ik_root.xpath('InverseKinematicsTool/marker_file')[0].text = str(trc)
        self.ik_root.xpath('InverseKinematicsTool/time_range')[0].text = f'{time_range[0]} {time_range[1]}'
        self.ik_root.xpath('InverseKinematicsTool/output_motion_file')[0].text = str(mot_path)

        etree.ElementTree(self.ik_root).write(self.ik_xml, pretty_print=True)

        pass

    def run_ik(self):
        exe_file = str(Path("C:\\", "OpenSim 4.4", "bin", "opensim-cmd.exe"))
        ik_xml = str(self.ik_xml)

        ik_output = subprocess.run([exe_file, "run-tool", ik_xml], 
                                shell=True,  stdout=subprocess.PIPE, text=True)

        print("stdout: " + str(ik_output.stdout))

        


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
working_dir = Path(repo, "tests", "output")
scale_xml_template = get_input_path("osim_models", "mediapipe_fullbody_model.osim")
scale_template = get_input_path("scale_ik_xml", "scale_mediapipe_model.xml")
trc_input = get_input_path("trc", "dao_yin.trc")
scale_time_range = [0, 15]

# %%

newModel = OsimModel(scale_xml_template, working_dir)

# %%

newModel.configure_scaling(scale_template, trc_input, [0,15])


# %%

newModel.scale_model()

# %%

ik_template = get_input_path("scale_ik_xml", "ik_mediapipe_model.xml")
motion_output = Path(repo, "tests", "output", "dao_yin.mot")


newModel.configure_ik(ik_template,trc_input, [0,9], motion_output)


# %%


newModel.run_ik()

