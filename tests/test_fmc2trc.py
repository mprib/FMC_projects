

from pathlib import Path
import sys
import unittest
import filecmp


# add the source directory to the top of sys.path so you can import
# the module correctly
repo = Path(__file__).parent.parent
source = Path(repo, "FMC_OpenSim")
sys.path.insert(0, str(source))

from fmc2trc import FMCSession


class TestFMC2trc(unittest.TestCase):

    def setUp(self):
        
        self.FMC_folder = Path("tests", "FMC_Sessions")
        self.GoodSession = "sesh_2022-08-10_10_33_12"
        self.osim_file = Path("tests", "osim_models", "mediapipe_fullbody_model.osim")

        self.testSession = FMCSession(self.GoodSession, self.FMC_folder, osim_file=self.osim_file, camera_rate=25)
        
    def test_trc_creation(self):
        """Provided with a FMC session, create an OpenSim .trc file"""

        test_output = Path("tests", "output", "dao_yin_dropped_working.trc")
        self.testSession.create_trajectory_trc(test_output)
        reference_output = Path("tests", "reference", "dao_yin_dropped_working.trc")

        try:
            #note, shallow is only looking at metadata
            self.assertTrue(filecmp.cmp(test_output,reference_output, shallow=False), "This is a message")
        except:
            print("---")
            print("<<<<<<<<<<<<<<<<<<<<<FAIL>>>>>>>>>>>>>>>>>>>>>>>>>")
            print("*******.trc created by fm2trc has changed*********")
            print("see test output: " + str(test_output))
            print("see reference output: " + str(reference_output))
            print("---")


    def test_csv_creation(self):
        """Provided with a FMC session, create a complete human readable CSV"""

        test_output = Path("tests", "output", "dao_yin.csv")
        self.testSession.create_trajectory_csv(test_output)
        reference_output = Path("tests", "reference", "dao_yin.csv")

        try:
            #note, shallow is only looking at metadata
            self.assertTrue(filecmp.cmp(test_output,reference_output, shallow=False), "This is a message")
        except:
            print("---")
            print("*******.csv created by fm2trc has changed*********")
            print("see test output: " + str(test_output))
            print("see reference output: " + str(reference_output))
            print("---")

        # trc_filename = Path( "tests", "output", "dao_yin_interpolated.trc")
        # testSession.create_trajectory_trc(trc_filename)


if __name__ == '__main__':
    unittest.main()
