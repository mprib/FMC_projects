# The purpose of this code module is to take the numpy output of freemocap and convert
# it to a human readable format that will become the hub of translation to other formats

# I am beginning with the code that I developed in a jupyter notebook 


# This code copied from https://github.com/freemocap/freemocap/wiki
from turtle import down
import numpy as np
from pathlib import Path 
import pandas as pd
import os
import csv


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

#TODO: convert this module into a FmcSession class object with methods after the export pipeline is working
#  make it work in a rough way, and then clean it up. You can start the "right" way when you have more experience with it.

# class FmcSession():
#     """Provide a session object to manage FMC output processing"""


#     def __init__(self, sessionID, output_folder, output_filename,
#             camera_rate):
#             self.sessionID = sessionID
#             self.output_folder = output_folder
#             self.output_filename = output_filename

# changing a file to check on something

def get_numpy_trajectories(sessionID):
    """returns the array of trajectories associated with a given motion capture session"""
    FMC_Folder = Path("C:/Users/Mac Prible/FreeMocap_Data") 
    dataArrayPath = FMC_Folder / sessionID / 'DataArrays'
    skeletonPath = dataArrayPath / 'mediaPipeSkel_3d_smoothed.npy'
    return np.load(skeletonPath) #load 3d open pose data


def get_trajectory_df(SessionID, TargetFolder="", TargetFilename="", 
        Axes= [0,2,1] , FlipAxis=[1,1,-1]):
    """returns a dataframe of trajectories for a session

    if a target folder and filename are provided, will also create 
    a csv file

    """

    scale_factor = 0.003

    joint_trajectories = get_numpy_trajectories(SessionID)
    
    # Order of the Axes
    x_axis = Axes[0]
    y_axis = Axes[1]
    z_axis = Axes[2]

    # Adjust axes to have alignment with the vertical
    flip_x = FlipAxis[0]
    flip_y = FlipAxis[1]
    flip_z = FlipAxis[2]

    # not interested in face mesh or hands here, 
    # so only taking first 33 elements
    # these represent the gross pose + hands
    sk_x = (joint_trajectories[:, 0:33, x_axis] * flip_x * scale_factor)   # skeleton x data
    sk_y = (joint_trajectories[:, 0:33, y_axis] * flip_y * scale_factor)   # skeleton y data
    sk_z = (joint_trajectories[:, 0:33, z_axis] * flip_z * scale_factor)   # skeleton z data
    
    marker_names = mediapipe_trajectories[0:33]
    
    # convert to df and concatenate
    x_df = pd.DataFrame(sk_x, columns = [name + "_x" for name in marker_names])
    y_df = pd.DataFrame(sk_y, columns = [name + "_y" for name in marker_names])
    z_df = pd.DataFrame(sk_z, columns = [name + "_z" for name in marker_names])
    merged_trajectories = pd.concat([x_df, y_df, z_df],axis = 1, join = "inner")    

    # get the correct order for all dataframe columns
    column_order = []
    for marker in marker_names:
        column_order.append(marker + "_x")
        column_order.append(marker + "_y")
        column_order.append(marker + "_z")

    print(column_order)

    # reorder the dataframe, note frame number in 0 position remains
    merged_trajectories = merged_trajectories.reindex(columns=column_order)
    
    # for column in reversed(column_order):
    #     merged_trajectories.insert(0, column, merged_trajectories.pop(column))


    return merged_trajectories

def create_trajectory_csv(SessionID, TargetFolder="", TargetFilename="", 
        Axes= [0,2,1] , FlipAxis=[1,1,-1]):

    TargetPath = os.path.join(TargetFolder, TargetFilename + ".csv")    
    df_traj = get_trajectory_df(SessionID, TargetFolder="", TargetFilename="", Axes= [0,2,1] , FlipAxis=[1,1,-1])
    df_traj.to_csv(TargetPath)


#TODO: need to fix scaling factors (probably an issue with the charuco board), and fix open sim orientation

#TODO: are some of the points jumping around? the IK looks like shit.

# Convert a human readable csv to a trc
def create_trajectory_trc(SessionID, TargetFolder, TargetFilename, 
        Axes= [0,1,2] , FlipAxis=[1,-1,-1]):
    
    num_markers = 33
    data_rate= 25
    camera_rate= 25
    units = 'm'
    orig_data_rate = 25
    orig_data_start_frame = 0

    traj_df = get_trajectory_df(SessionID, TargetFolder, TargetFilename, Axes, FlipAxis)
    # traj_df = traj_df.fillna("")
    traj_df = traj_df.dropna()
    

    orig_num_frames = len(traj_df) - 1
    num_frames = orig_num_frames

    TargetPath = os.path.join(TargetFolder, TargetFilename + ".trc")

    with open(TargetPath, 'wt', newline='', encoding='utf-8') as out_file:
        tsv_writer = csv.writer(out_file, delimiter='\t')
        tsv_writer.writerow(["PathFileType","4", "(X/Y/Z)",	"Tpose_0-50.trc"])
        tsv_writer.writerow(["DataRate","CameraRate","NumFrames","NumMarkers", "Units","OrigDataRate","OrigDataStartFrame","OrigNumFrames"])
        tsv_writer.writerow([data_rate, camera_rate,num_frames, num_markers, units, orig_data_rate, orig_data_start_frame, orig_num_frames])

        # create names of trajectories, skipping two columns (top of table)
        header_names = ['Frame#', 'Time']
        for trajectory in mediapipe_trajectories[0:33]:
            header_names.append(trajectory)
            header_names.append("")
            header_names.append("")    

        tsv_writer.writerow(header_names)

        # create labels for x,y,z axes (second row of table)
        header_names = ["",""]
        for i in range(1,34):
            header_names.append("X"+str(i))
            header_names.append("Y"+str(i))
            header_names.append("Z"+str(i))

        tsv_writer.writerow(header_names)

        # Create a list with the appropriate column order in it
        column_names = traj_df.columns
        column_names = column_names.insert(0, "Frame")
        column_names = column_names.insert(1, "time")

        # the .trc fileformat expects a blank fourth line
        tsv_writer.writerow("")

        # add in frame and Time stamp to the data frame

        traj_df["Frame"] = [str(i) for i in range(0, len(traj_df))]
        traj_df["time"] = traj_df["Frame"].astype(float) / float(camera_rate)
        
        # pd.to_string(traj_df["Frame"], downcast='string')

        traj_df = traj_df.reindex(columns=column_names)

        for row in range(0, len(traj_df)):
            tsv_writer.writerow(traj_df.iloc[row].tolist())


        print(traj_df)




GoodSession = "sesh_2022-08-10_10_33_12"
target_folder = "C:\\Users\\Mac Prible\\Box\\Research\\FMC_projects\\FMC_to_trc"
target_filename = "dao_yin_dropped"

# create_trajectory_csv(GoodSession,target_folder, target_filename)

create_trajectory_trc(GoodSession,target_folder, target_filename)

test_df = get_trajectory_df(GoodSession)
print(test_df)

