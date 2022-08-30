

from pathlib import Path
import sys
import unittest
import filecmp
import tracemalloc

from pyrsistent import get_in


tracemalloc.start()

#####################################################################
# boilerplate and helper functions to assist with unittest creation #
repo = Path(__file__).parent.parent
source = Path(repo, "FMC_OpenSim")
sys.path.insert(0, str(source))

from fmc2trc import FMCSession
#####################################################################

def get_input_path(*args):
    return Path(repo,"tests",  "input", *args)


def get_reference_and_output_paths(test_name, filetype):

    test_name = test_name.replace(" ", "_")

    if filetype.startswith("."):
        pass
    else:
        filetype = "." + filetype

    ref_path = Path(repo, "tests", "reference", test_name+"_reference" + filetype)
    out_path = Path(repo, "tests", "output", test_name+"_output" + filetype)

    return ref_path, out_path

class TestFMC2trc(unittest.TestCase):

    def setUp(self):
        
        self.FMC_folder = get_input_path("FMC_Sessions")
        self.GoodSession = "sesh_2022-08-10_10_33_12"
        self.data_array = 'mediaPipeSkel_3d_smoothed.npy'
        self.osim_file = get_input_path("osim_models", "mediapipe_fullbody_model.osim")

        self.testSession = FMCSession(self.GoodSession, self.FMC_folder, self.data_array, osim_file=self.osim_file, camera_rate=25)
        
    def test_trc_creation(self):
        """given a previously set up FMC session, create an OpenSim .trc file"""

        reference, output = get_reference_and_output_paths("test_trc_creation", ".trc")   

        self.testSession.create_trajectory_trc(output)
        self.assertTrue(filecmp.cmp(reference, output, shallow=False))
        
    def test_csv_creation(self):
        """given a previously set up FMC session, create a complete human readable CSV"""

        reference, output = get_reference_and_output_paths("test_csv_creation", ".csv")        

        self.testSession.create_trajectory_csv(output)
        self.assertTrue(filecmp.cmp(reference, output, shallow=False))

if __name__ == '__main__':
    unittest.main()
