

from pathlib import Path
import sys
import unittest


# add the source directory to the top of sys.path so you can import
# the module correctly
repo = Path(__file__).parent.parent
source = Path(repo, "FMC_OpenSim")
sys.path.insert(0, str(source))

from fmc2trc import FMCSession


class TestFMC2trc(unittest.TestCase):


    def test_trc_creation(self):
        """
        Provided with the dao yin session and full body model,
        create a trc file for OpenSim
        """
        FMC_folder = Path("tests", "FMC_Sessions")
        
        GoodSession = "sesh_2022-08-10_10_33_12"

        osim_file = Path("models", "mediapipe_fullbody", "mediapipe_fullbody_model.osim")

        testSession = FMCSession(GoodSession, FMC_folder, osim_file=osim_file, camera_rate=25)

        trc_filename = Path("tests", "output", "dao_yin_dropped_working.trc")
        print(trc_filename)
        testSession.create_trajectory_trc(trc_filename)


        testSession.create_trajectory_csv(Path( "tests", "output", "dao_yin.csv"))
        testSession.interpolate_trajectory_gaps()

        trc_filename = Path( "tests", "output", "dao_yin_interpolated.trc")
        testSession.create_trajectory_trc(trc_filename)

        
    # def test_model_scaling(self):

    # def test_model_inverse_kinematics(self):



if __name__ == '__main__':
    unittest.main()
