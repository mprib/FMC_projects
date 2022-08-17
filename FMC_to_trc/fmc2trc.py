# The purpose of this code module is to take the numpy output of freemocap and convert
# it to a human readable format that will become the hub of translation to other formats

# I am beginning with the code that I developed in a jupyter notebook 


# This code copied from https://github.com/freemocap/freemocap/wiki
import numpy as np
from pathlib import Path 
import pandas as pd
 
mediapipe_trajectories =  [
    "nose",
    "left_eye_inner",
    "left_eye",
    "left_eye_outer",
    "right_eye_inner",
    "right_eye",
    "right_eye_outer",
    "left_ear",
    "right_ear",
    "mouth_left",
    "mouth_right",
    "left_shoulder",
    "right_shoulder",
    "left_elbow",
    "right_elbow",
    "left_wrist",
    "right_wrist",
    "left_pinky",
    "right_pinky",
    "left_index",
    "right_index",
    "left_thumb",
    "right_thumb",
    "left_hip",
    "right_hip",
    "left_knee",
    "right_knee",
    "left_ankle",
    "right_ankle",
    "left_heel",
    "right_heel",
    "left_foot_index",
    "right_foot_index",
    "right_hand_wrist",
    "right_hand_thumb_cmc",
    "right_hand_thumb_mcp",
    "right_hand_thumb_ip",
    "right_hand_thumb_tip",
    "right_hand_index_finger_mcp",
    "right_hand_index_finger_pip",
    "right_hand_index_finger_dip",
    "right_hand_index_finger_tip",
    "right_hand_middle_finger_mcp",
    "right_hand_middle_finger_pip",
    "right_hand_middle_finger_dip",
    "right_hand_middle_finger_tip",
    "right_hand_ring_finger_mcp",
    "right_hand_ring_finger_pip",
    "right_hand_ring_finger_dip",
    "right_hand_ring_finger_tip",
    "right_hand_pinky_finger_mcp",
    "right_hand_pinky_finger_pip",
    "right_hand_pinky_finger_dip",
    "right_hand_pinky_finger_tip",
    "left_hand_wrist",
    "left_hand_thumb_cmc",
    "left_hand_thumb_mcp",
    "left_hand_thumb_ip",
    "left_hand_thumb_tip",
    "left_hand_index_finger_mcp",
    "left_hand_index_finger_pip",
    "left_hand_index_finger_dip",
    "left_hand_index_finger_tip",
    "left_hand_middle_finger_mcp",
    "left_hand_middle_finger_pip",
    "left_hand_middle_finger_dip",
    "left_hand_middle_finger_tip",
    "left_hand_ring_finger_mcp",
    "left_hand_ring_finger_pip",
    "left_hand_ring_finger_dip",
    "left_hand_ring_finger_tip",
    "left_hand_pinky_finger_mcp",
    "left_hand_pinky_finger_pip",
    "left_hand_pinky_finger_dip",
    "left_hand_pinky_finger_tip",
]


#openPoseData_nCams_nFrames_nImgPts_XYC = np.load(dataArrayPath / 'openPoseData_2d.npy') #2d data too, if you're into that

def get_trajectories(sessionID):
    """returns the array of trajectories associated with a given motion capture session"""
    FMC_Folder = Path("C:/Users/Mac Prible/FreeMocap_Data") #replace this with path to the unzipped session data folder, e.g. Path(r'C:/Users/Me/session_data_folder')
    dataArrayPath = FMC_Folder / sessionID / 'DataArrays'
    skeletonPath = dataArrayPath / 'mediaPipeSkel_3d.npy'
    return np.load(skeletonPath) #load 3d open pose data

# Build list of lists that can be used to iterate
def create_trajectory_csv(SessionID, TargetLocation, Axes= [0,2,1] , FlipAxis=[1,1,-1]):
    """builds a human readable csv of a session's trajectories at a given location"""

    joint_trajectories = get_trajectories(SessionID)
    
    # Order of the Axes
    x_axis = Axes[0]
    y_axis = Axes[1]
    z_axis = Axes[2]

    # Adjust axes to have alignment with the vertical
    flip_x = FlipAxis[0]
    flip_y = FlipAxis[1]
    flip_z = FlipAxis[2]

    # not interested in face mesh here, so only taking first 75 elements
    # these represent the gross pose + hands
    sk_x = (joint_trajectories[:, 0:75, x_axis] * flip_x)   # skeleton x data
    sk_y = (joint_trajectories[:, 0:75, y_axis] * flip_y)   # skeleton y data
    sk_z = (joint_trajectories[:, 0:75, z_axis] * flip_z)   # skeleton z data
    

    # convert to df and concatenate
    x_df = pd.DataFrame(sk_x, columns = [name + "_x" for name in mediapipe_trajectories])
    y_df = pd.DataFrame(sk_y, columns = [name + "_y" for name in mediapipe_trajectories])
    z_df = pd.DataFrame(sk_z, columns = [name + "_z" for name in mediapipe_trajectories])
    merged_trajectories = pd.concat([x_df, y_df, z_df],axis = 1, join = "inner")    

    merged_trajectories.to_csv(TargetLocation)

# Convert a human readable csv to a trc
def trajectory_csv2trc(SessionID, TargetLocation):

    create_trajectory_csv(SessionID, TargetLocation)

    with open(TargetLocation+".trc")







GoodSession = "sesh_2022-08-10_10_33_12"
target_csv = "C:\\Users\\Mac Prible\\Box\\Research\\FMC_projects\\FMC_to_trc\\dao_yin.csv"

create_trajectory_csv(GoodSession,target_csv)