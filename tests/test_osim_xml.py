# %%

from pathlib import Path
from pyexpat.errors import XML_ERROR_INCOMPLETE_PE
import sys
import unittest
import filecmp



#####################################################################
# boilerplate and helper functions to assist with unittest creation #
repo = Path(__file__).parent.parent
source = Path(repo, "FMC_OpenSim")
sys.path.insert(0, str(source))

from osim_xml import OsimModelTemplate, OsimModel
#####################################################################



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
class TestOsimModelTemplate(unittest.TestCase):

    def test_create_joint_loc_csv(self):
        """this also implicity tests the dataframe creation method"""
        osim_template = get_input_path("osim_models", "mediapipe_fullbody_model.osim")
        reference, output = get_reference_and_output_paths("test_create_joint_loc_csv", "csv")
        osim_model = OsimModelTemplate(osim_template)
        osim_model.create_joint_loc_csv(output)

        self.assertTrue(filecmp.cmp(reference, output, shallow=False), "create_joint_loc_csv() working")
        
    def test_add_single_marker_to_model(self):
        """add a single landmark to an markerless model"""
        
        # Sample Marker
        marker_name = 'left_eye'
        location_text = '0.069857071913979135 0.55697305173123246 -0.029007770243867158'
        parent_frame = "/bodyset/head"

        osim_template = get_input_path("osim_models", "mediapipe_fullbody_model_no_markers.osim")
        reference, output = get_reference_and_output_paths("test_add_single_marker_to_model", ".osim")
        osim_model = OsimModelTemplate(osim_template, output)
        osim_model.add_marker(marker_name, location_text, parent_frame)

        self.assertTrue(filecmp.cmp(reference, output, shallow=False), "add_single_marker() working")
            
    def test_add_ModelLandmarkMap(self):
        """given a spreadsheet of landmark positions relative to a segment, add them"""
        test_model_template =  get_input_path("osim_models", "mediapipe_fullbody_model.osim")
        landmark_map_path = get_input_path("osim_models", "ModelLandmarkMap.xlsx")

        reference, output = get_reference_and_output_paths("test_add_ModelLandmarkMap", ".osim")

        test_model = OsimModelTemplate(test_model_template, output)
        test_model.add_ModelLandmarkMap(landmark_map_path)

        self.assertTrue(filecmp.cmp(reference, output, shallow=False))  


    # def test_init_ScaleXML(self):
    #     """create a new scale xml file based on a template"""
    #     xml_template = get_input_path("scale_ik_xml", "scale_mediapipe_model.xml")
    #     reference, output = get_reference_and_output_paths("test_init_ScaleXML", ".xml")

    #     newScaleXML = ScaleXML(xml_template, output)

    #     self.assertTrue(filecmp.cmp(reference, output, shallow=False))

    # def test_assign_trc(self):
    #     """upate a new scale xml to reference a trc file"""

    #     xml_template = get_input_path("scale_ik_xml", "scale_mediapipe_model.xml")
    #     reference, output = get_reference_and_output_paths("test_assign_trc", ".xml")
    #     trc_input = get_input_path("trc", "dao_yin.trc")

    #     newScaleXML = ScaleXML(xml_template, output)
        
    #     ScaleXML.assign_trc()



    # # def test_add_scaled_model_path
    # currently demotivated on the TDD front while trying to wrap my head around
    # testing these functions using Mock. Going to take a detour and just code some 
    # intermediate functions and will learn from my mistakes later

if __name__ == '__main__':
    unittest.main()

# %%
