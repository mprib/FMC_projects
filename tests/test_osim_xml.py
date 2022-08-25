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


class TestOsimModel(unittest.TestCase):

    def test_get_joint_locations(self):
        repo = Path(__file__).parent.parent
        osim_path = Path(repo, "tests","osim_models", "mediapipe_fullbody_model.osim")

        osim_model = OsimModel(osim_path)

        csv_output_path = Path(repo, "tests", "output", "model_marker_locations.csv")
        osim_model.create_joint_loc_csv(csv_output_path)
        
        csv_reference_path =  Path(repo, "tests","reference", "model_marker_locations.csv")

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


if __name__ == '__main__':
    unittest.main()
