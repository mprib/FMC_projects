
from pathlib import Path
import fmc2trc

FMC_output_folder = Path("C:", "users", "Mac Prible", "FreeMocap_Data", "sesh_2022-08-30_11_06_41")
trajectory_npy = "mediaPipeSkel_3d_smoothed_unrotated.npy"



hand_recording = fmc2trc.FMCSession(FMC_output_folder, trajectory_npy,25, , 

