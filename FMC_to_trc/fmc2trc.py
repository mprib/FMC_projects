# The purpose of this code module is to take the numpy output of freemocap and convert
# it to a human readable format that will become the hub of translation to other formats

# I am beginning with the code that I developed in a jupyter notebook 


# This code copied from https://github.com/freemocap/freemocap/wiki
import os
import csv
from pathlib import Path 
import numpy as np
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

class FMCSession():
    """Provide a session object to manage FMC output processing"""

    def __init__(self, sessionID, FMC_folder, camera_rate):
            self.sessionID = sessionID
            self.camera_rate = camera_rate
            self.FMC_folder =  FMC_folder

            self.trajectories = self.get_trajectory_dataframe()

  
    def get_trajectory_array(self):
        """returns the array of 3D trajectories associated with a session"""

        dataArrayPath = self.FMC_folder / self.sessionID / 'DataArrays'
        skeletonPath = dataArrayPath / 'mediaPipeSkel_3d_smoothed.npy'
        return np.load(skeletonPath) #load 3d open pose data


    def get_trajectory_dataframe(self):
        """returns a dataframe of trajectories for a session"""

        #TODO: resolve this via a good charuco board, not this hack
        scale_factor = 0.003

        # These will manipulate the orientation of the markers 
        # to make them line up better by default with OpenSim
        # axes_order= [0,2,1]
        # axes_flip=[1,1,-1]
    
        # flip y and z (1 and 2); y becomes negative
        axes_order= [0,1,2]
        axes_flip=[1,-1,-1]
        

        # Order of the Axes
        x_axis = axes_order[0]
        y_axis = axes_order[1]
        z_axis = axes_order[2]

        # Adjust axes to have alignment with the vertical
        flip_x = axes_flip[0]
        flip_y = axes_flip[1]
        flip_z = axes_flip[2]

        joint_trajectories = self.get_trajectory_array()

        # not interested in face mesh or hands here, 
        # so only taking first 33 elements
        # these represent the gross pose + simple hands
        sk_x = (joint_trajectories[:, 0:33, x_axis] * flip_x * scale_factor)   # skeleton x data
        sk_y = (joint_trajectories[:, 0:33, y_axis] * flip_y * scale_factor)   # skeleton y data
        sk_z = (joint_trajectories[:, 0:33, z_axis] * flip_z * scale_factor)   # skeleton z data
        

        marker_names = mediapipe_trajectories[0:33]
        
        # convert to df and concatenate
        x_df = pd.DataFrame(sk_x, columns = [name + "_x" for name in marker_names])
        y_df = pd.DataFrame(sk_y, columns = [name + "_y" for name in marker_names])
        z_df = pd.DataFrame(sk_z, columns = [name + "_z" for name in marker_names])
        merged_trajectories = pd.concat([x_df, y_df, z_df],axis = 1, join = "inner")    


        # add in frame and Time stamp to the data frame
        merged_trajectories["Frame"] = [str(i) for i in range(0, len(merged_trajectories))]
        merged_trajectories["Time"] = merged_trajectories["Frame"].astype(float) / float(self.camera_rate)
        

        # get the correct order for all dataframe columns
        column_order = []
        for marker in marker_names:
            column_order.append(marker + "_x")
            column_order.append(marker + "_y")
            column_order.append(marker + "_z")

        # Add Frame and Time
        column_order.insert(0, "Frame")
        column_order.insert(1, "Time")

        # reorder the dataframe, note frame number in 0 position remains
        merged_trajectories = merged_trajectories.reindex(columns=column_order)
        
        # for column in reversed(column_order):
        #     merged_trajectories.insert(0, column, merged_trajectories.pop(column))


        return merged_trajectories

    def create_trajectory_csv(self, csv_filename):

        # TargetPath = os.path.join(TargetFolder, TargetFilename + ".csv")    
        df_traj = self.get_trajectory_dataframe()
        df_traj.to_csv(csv_filename, index=False)


    # Convert a human readable csv to a trc
    def create_trajectory_trc(self, trc_filename):
        
        num_markers = 33
        data_rate= self.camera_rate # not sure how this is different from camera rate
        camera_rate= self.camera_rate
        units = 'm'
        orig_data_rate = 25
        orig_data_start_frame = 0

        trajectories_for_trc = self.trajectories

        # going to recreate these later after potentially dropping frames
        original_column_order = trajectories_for_trc.columns
        trajectories_for_trc = trajectories_for_trc.drop(columns=["Frame", "Time"]) 
        # traj_df = traj_df.fillna("")
        trajectories_for_trc = trajectories_for_trc.dropna()
        
        orig_num_frames = len(trajectories_for_trc) - 1
        num_frames = orig_num_frames

        trc_path = os.path.join(trc_filename)

        # this will create the formatted .trc file
        with open(trc_path, 'wt', newline='', encoding='utf-8') as out_file:
            tsv_writer = csv.writer(out_file, delimiter='\t')
            tsv_writer.writerow(["PathFileType",
                                "4", 
                                "(X/Y/Z)",	
                                trc_filename])
            tsv_writer.writerow(["DataRate",
                                "CameraRate",
                                "NumFrames",
                                "NumMarkers", 
                                "Units",
                                "OrigDataRate",
                                "OrigDataStartFrame",
                                "OrigNumFrames"])
            tsv_writer.writerow([data_rate, 
                                camera_rate,
                                num_frames, 
                                num_markers, 
                                units, 
                                orig_data_rate, 
                                orig_data_start_frame, 
                                orig_num_frames])

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

            # the .trc fileformat expects a blank fourth line
            tsv_writer.writerow("")

            # add in frame and Time stamp to the data frame 
            # this redundent step is due to potentially dropping frames earlier
            # trajectories_for_trc["Frame"] = [str(i) for i in range(0, len(trajectories_for_trc))]
            # trajectories_for_trc["Time"] = trajectories_for_trc["Frame"].astype(float) / float(self.camera_rate)
            trajectories_for_trc.insert(0, "Frame", [str(i) for i in range(0, len(trajectories_for_trc))])
            trajectories_for_trc.insert(1, "Time", trajectories_for_trc["Frame"].astype(float) / float(self.camera_rate))

        
            # trajectories_for_trc = trajectories_for_trc.reindex(columns=column_names)

            for row in range(0, len(trajectories_for_trc)):
                tsv_writer.writerow(trajectories_for_trc.iloc[row].tolist())

            #print(column_names)





#TODO: interpolate missing data
#def interpolate_trajectories(self):

GoodSession = "sesh_2022-08-10_10_33_12"
FMC_folder = Path("C:/Users/Mac Prible/FreeMocap_Data")
trc_filename = "FMC_to_trc/dao_yin_dropped.trc"
csv_filename = "FMC_to_trc/dao_yin_dropped.csv"

testSession = FMCSession(GoodSession, FMC_folder, 25)

trajectories = testSession.get_trajectory_dataframe()

testSession.create_trajectory_csv(csv_filename)
testSession.create_trajectory_trc(trc_filename)

print(trajectories)