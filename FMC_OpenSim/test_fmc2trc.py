import unittest
from fmc2trc import FMCSession


class TestFMC2trc(unittest.TestCase):


    def test_trc_creation(self):
        """
        Provided with the dao yin session and full body model files,
        create a specific .mot file        
        """
        FMC_folder = Path("C:/Users/Mac Prible/FreeMocap_Data")
        GoodSession = "sesh_2022-08-10_10_33_12"

        osim_file = "FMC_OpenSim\models\mediapipe_fullbody\mediapipe_fullbody_model.osim"

        testSession = FMCSession(GoodSession, FMC_folder, osim_file=osim_file, camera_rate=25)

        trc_filename = "FMC_OpenSim/trc/dao_yin_dropped_working.trc" 
        testSession.create_trajectory_trc(trc_filename)


        testSession.create_trajectory_csv("FMC_OpenSim/trc/dao_yin.csv")
        testSession.interpolate_trajectory_gaps()

        trc_filename = "FMC_OpenSim/trc/dao_yin_interpolated.trc" 
        testSession.create_trajectory_trc(trc_filename)


    def test_model_scaling(self):




    def test_model_inverse_kinematics(self):

    

subprocess.run('dir', shell=True)