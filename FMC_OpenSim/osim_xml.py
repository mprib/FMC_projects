
# %%
from pathlib import Path
import shutil
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

    
        # self.osim_tree = etree.parse(osim_template, self.parser)
        # self.osim_path = new_osim_path

        # self.osim_root = self.osim_tree.getroot()
        # etree.ElementTree(self.osim_root).write(self.osim_path, pretty_print=True)


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
        """Use the temp/scale.xml file to scale the template model"""



        pass

    def configure_ik(self):

        pass

    def run_ik(self):
    
        self




    def set_scaling_params(self, scale_xml_template, new_scale_xml_path, trc, time_range, scaled_osim_path):
        """
        based on an input scaling xml template, create a new template using the
        provided trc file

        I suspect that I may be overloading this class and function, but am concerned
        about over
        """
    

        self.scaling_tree = etree.parse(scale_xml_template, self.parser)
        self.osim_path = new_scale_xml_path

        self.scaling_root = self.scaling_tree.getroot()
        etree.ElementTree(self.scaling_root).write(self.osim_path, pretty_print=True)



    def scale_model(self):
        """run the scale.xml file using opensim-cmd"""

        exe_file = str(Path("C:\\", "OpenSim 4.4", "bin", "opensim-cmd.exe"))
        scale_xml = str(self.osim_path)

        scale_output = subprocess.call([exe_file, "run-tool", scale_xml], 
                                shell=True,  stdout=subprocess.PIPE, text=True)
        if scale_output:
            print(">>>>>>>>>>>>>> SCALED MODEL NOT PRODUCED <<<<<<<<<<<<<<<<<<")
        else:
            print("scaled model stored at: ", self.osim_path)


    def update_xml(self):
        etree.ElementTree(self.scaling_root).write(self.osim_path, pretty_print=True)

    def configure_xml(self, template, trc, scale_time_range, xml_outout):


        pass

    def scale_model(self):
        """run the scale.xml file using opensim-cmd"""

        exe_file = str(Path("C:\\", "OpenSim 4.4", "bin", "opensim-cmd.exe"))
        scale_xml = str(self.osim_path)

        scale_output = subprocess.call([exe_file, "run-tool", scale_xml], 
                                shell=True,  stdout=subprocess.PIPE, text=True)
        if scale_output:
            print(">>>>>>>>>>>>>> SCALED MODEL NOT PRODUCED <<<<<<<<<<<<<<<<<<")
        else:
            print("scaled model stored at: ", self.osim_path)



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



# %%
# I am realizing that the model placer component may be minimally important here
# as there is not human variability in marker placement
# the ms and mp models are currently the same

# ms refers to "ModelScaler"
ms_ref_model, ms_output_model = get_reference_and_output_paths("test_configure_xml", ".osim")
ms_time_range = [0, 15]


# mp refers to "MarkerPlacer"
mp_ref_model, mp_output_model = get_reference_and_output_paths("test_configure_xml", ".osim")
mp_time_range = [0, 15]



newScaleXML = (xml_template, xml_output)

newScaleXML.root.xpath('ScaleTool/GenericModelMaker/model_file')[0].text = str(input_model_path)
newScaleXML.root.xpath('ScaleTool/ModelScaler/marker_file')[0].text = str(trc_input)
newScaleXML.root.xpath('ScaleTool/ModelScaler/output_model_file')[0].text = str(input_model_path)
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
