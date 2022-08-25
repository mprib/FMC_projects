from pathlib import Path
import sys
import unittest
import filecmp


# add the source directory to the top of sys.path so you can import
# the module correctly
repo = Path(__file__).parent.parent
source = Path(repo, "FMC_OpenSim")
sys.path.insert(0, str(source))

from osim_xml import OsimModel

repo = Path(__file__).parent.parent
        

class TestOsimModel(unittest.TestCase):

    def test_get_joint_locations(self):
        """this also implicity tests the dataframe creation methodi"""
        osim_path = Path(repo, "tests","osim_models", "mediapipe_fullbody_model.osim")
        osim_model = OsimModel(osim_path)
        csv_output_path = Path(repo, "tests", "output", "model_marker_locations.csv")
        csv_reference_path =  Path(repo, "tests","reference", "model_marker_locations.csv")
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
        """given a spreadsheet of landmarks, add them to an osim file"""
        marker_name = 'nose'
        location = '(0.0890481 0.532978 0.000609926)'
        parent_frame = "/bodyset/head"

        osim_path = Path(repo, "tests","osim_models", "mediapipe_fullbody_model_no_markers.osim")
        osim_model = OsimModel(osim_path)
        
        osim_model.add_marker(marker_name, location, parent_frame)

        l
        
        
        
        pass

if __name__ == '__main__':
    unittest.main()
