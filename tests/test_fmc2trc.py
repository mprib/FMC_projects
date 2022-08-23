
from pathlib import Path
import unittest

from FMC_OpenSim import fmc2trc


class TestFMC2trc(unittest.TestCase):


    def test_trc_creation(self):
        """
        Provided with the dao yin session and full body model,
        create a trc file for OpenSim
        """
        FMC_folder = Path("FMC_OpenSim", "tests", "FMC_Sessions")
        
        GoodSession = "sesh_2022-08-10_10_33_12"

        osim_file = Path("FMC_OpenSim","models", "mediapipe_fullbody", "mediapipe_fullbody_model.osim")

        testSession = fmc2trc.FMCSession(GoodSession, FMC_folder, osim_file=osim_file, camera_rate=25)

        trc_filename = Path("FMC_OpenSim","tests", "output", "dao_yin_dropped_working.trc")
        testSession.create_trajectory_trc(trc_filename)


        testSession.create_trajectory_csv(Path("FMC_OpenSim", "tests", "output", "dao_yin.csv"))
        testSession.interpolate_trajectory_gaps()

        trc_filename = Path("FMC_OpenSim", "tests", "output", "dao_yin_interpolated.trc")
        testSession.create_trajectory_trc(trc_filename)

        
    # def test_model_scaling(self):

    # def test_model_inverse_kinematics(self):
   

unittest.main()