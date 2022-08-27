# %%

from pathlib import Path
from pyexpat.errors import XML_ERROR_INCOMPLETE_PE
import sys
import unittest
import filecmp

from pyrsistent import get_in


# add the source directory to the top of sys.path so you can import
# the module correctly
repo = Path(__file__).parent.parent
source = Path(repo, "FMC_OpenSim")
sys.path.insert(0, str(source))

from osim_xml import OsimModel

repo = Path(__file__).parent.parent


# Create some helper functions that will make tests more succinct
# %%
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
def compare_reference_and_output(reference_file, output_file, message="" ):
    """automate the checking of output vs reference and printing an alert"""

    try:
        self.assertTrue(filecmp.cmp(reference_file, output_file, shallow=False))
    except:
        print("---")
        print("<<<<<<<<<<<<<<<<<<<<<FAIL>>>>>>>>>>>>>>>>>>>>>>>>>")
        print("********" + message + "*********")
        print("see test output: " + str(output_file))
        print("see reference output: " + str(reference_file))
        print("---")

class TestOsimModel(unittest.TestCase):

    def test_create_joint_loc_csv(self):
        """this also implicity tests the dataframe creation methodi"""
        osim_template = get_input_path("osim_models", "mediapipe_fullbody_model.osim")
        
        osim_path = Path(repo, "tests","output", "mediapipe_fullbody_model.osim")
        osim_model = OsimModel(osim_template, osim_path)
        csv_output_path = Path(repo, "tests", "output", "test_create_joint_loc_output.csv")
        csv_reference_path =  Path(repo, "tests","reference", "test_create_joint_loc_reference.csv")
        osim_model.create_joint_loc_csv(csv_output_path)

        try:
                #note, shallow is only looking at metadata
                self.assertTrue(filecmp.cmp(csv_output_path,csv_reference_path, shallow=False), "This is a message")
        except:
            print("---")
            print("<<<<<<<<<<<<<<<<<<<<<FAIL>>>>>>>>>>>>>>>>>>>>>>>>>")
            print("*******Model Joint Positions have changed*********")
            print("see test output: " + str(csv_output_path))
            print("see reference output: " + str(csv_reference_path))
            print("---")


    def test_add_single_marker_to_model(self):
        """add a single landmark to an markerless model"""
        marker_name = 'left_eye'
        location_text = '0.069857071913979135 0.55697305173123246 -0.029007770243867158'
        parent_frame = "/bodyset/head"

        osim_template = get_input_path("osim_models", "mediapipe_fullbody_model_no_markers.osim")

        osim_path = Path(repo, "tests","output", "test_add_single_marker_output.osim")
        osim_model = OsimModel(osim_template, osim_path)
        
        osim_model.add_marker(marker_name, location_text, parent_frame)

        model_reference = Path(repo, "tests","reference", "test_add_single_marker_reference.osim")

        try:
            #note, shallow is only looking at metadata
            self.assertTrue(filecmp.cmp(osim_path, model_reference, shallow=False), "This is a message")
        except:
            print("---")
            print("<<<<<<<<<<<<<<<<<<<<<FAIL>>>>>>>>>>>>>>>>>>>>>>>>>")
            print("*******Add Single Marker has Failed*********")
            print("see test output: " + str(osim_path))
            print("see reference output: " + str(model_reference))
            print("---")
            
    def test_add_ModelLandmarkMap(self):
        """given a spreadsheet of landmark positions relative to a segment, add them"""
        repo = Path(__file__).parent.parent
        test_model_template =  get_input_path("osim_models", "mediapipe_fullbody_model.osim")
        
        
        test_model_path =  Path(repo, "tests","output", "test_add_ModelLandmarkMap_output.osim")
        reference_model_path = Path(repo, "tests","reference", "test_add_ModelLandmarkMap_reference.osim")
        
        test_model = OsimModel(test_model_template, test_model_path)

        landmark_map_path = get_input_path("osim_models", "ModelLandmarkMap.xlsx")

        test_model.add_ModelLandmarkMap(landmark_map_path)

        try:
            #note, shallow is only looking at metadata
            self.assertTrue(filecmp.cmp(test_model_path, reference_model_path, shallow=False))
        except:
            print("---")
            print("<<<<<<<<<<<<<<<<<<<<<FAIL>>>>>>>>>>>>>>>>>>>>>>>>>")
            print("*******Add Model Landmark Map has Failed*********")
            print("see test output: " + str(test_model_path))
            print("see reference output: " + str(reference_model_path))
            print("---")

class TestScaleXML(unittest.TestCase):

    # here I start trying to actually use the helper functions I just created.
    
    def test_assign_model(self):
        """assign a model file to a given scaling xml file"""

        in_xml = get_input_path("scale_ik_xml", "ik_mediapipe_model.xml")
        ref_xml, out_xml = get_reference_and_output_paths("test_assign_model", "xml")

        scale_xml = ScaleXML(in_xml, out_xml)



if __name__ == '__main__':
    unittest.main()

# %%
