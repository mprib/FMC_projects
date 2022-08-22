# The purpose of this code module is to take the numpy output of freemocap and convert
# it to a human readable format that will become the hub of translation to other formats

# I am beginning with the code that I developed in a jupyter notebook 


# This code copied from https://github.com/freemocap/freemocap/wiki
import os
import csv
from pathlib import Path 
import numpy as np
import pandas as pd
import json


class FMCSession():
    """Provide a session object to manage FMC output processing"""

    def __init__(self, sessionID, FMC_folder, camera_rate, osim_file, pose_tracked="mediapipe_body_hands"):
            self.sessionID = sessionID
            self.camera_rate = camera_rate
            self.FMC_folder =  FMC_folder
            self.osim_file = osim_file
            self.pose_tracked = pose_tracked

            # tracked landmarks will be used to label trajectory array and 
            # convert to human readable csv
            self.tracked_landmarks = self.get_landmark_index(pose_tracked)
            self.tracked_landmark_count = len(self.tracked_landmarks)
            self.trajectories = self.get_trajectory_dataframe()
            
            # modelled trajectories will be used to create the trc and ignore
            # gap filling of non-modelled landmarks
            #TODO this should get refactored to pull in the modelled 
            # trajectories directly from the osim file
            #pose_modeled = "mediapipe_body"
            pose_modeled = "mediapipe_body_hands"
            self.model_landmarks = self.get_landmark_index(pose_modeled)

    def get_landmark_index(self, pose_key):
        """Read in a dictionary of the landmarks being tracked"""
        
        with open("reference\landmarks.json") as f_obj:
            landmarks = json.load(f_obj)

        return landmarks[pose_key]


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

        all_trajectories = self.get_trajectory_array()

        # not interested in face mesh or hands here, 
        # so only taking first 33 elements
        # these represent the gross pose + simple hands
        lm_x = (all_trajectories[:, 0:self.tracked_landmark_count, x_axis] * flip_x * scale_factor)   # skeleton x data
        lm_y = (all_trajectories[:, 0:self.tracked_landmark_count, y_axis] * flip_y * scale_factor)   # skeleton y data
        lm_z = (all_trajectories[:, 0:self.tracked_landmark_count, z_axis] * flip_z * scale_factor)   # skeleton z data
        

        # convert landmark trajectory arrays to df and merge together
        x_df = pd.DataFrame(lm_x, columns = [name + "_x" for name in self.tracked_landmarks])
        y_df = pd.DataFrame(lm_y, columns = [name + "_y" for name in self.tracked_landmarks])
        z_df = pd.DataFrame(lm_z, columns = [name + "_z" for name in self.tracked_landmarks])
        merged_trajectories = pd.concat([x_df, y_df, z_df],axis = 1, join = "inner")    


        # add in Frame Number and Time stamp 
        merged_trajectories["Frame"] = [str(i) for i in range(0, len(merged_trajectories))]
        merged_trajectories["Time"] = merged_trajectories["Frame"].astype(float) / float(self.camera_rate)        

        # get the correct order for all dataframe columns
        column_order = []
        for marker in self.tracked_landmarks:
            column_order.append(marker + "_x")
            column_order.append(marker + "_y")
            column_order.append(marker + "_z")

        # Add Frame and Time
        column_order.insert(0, "Frame")
        column_order.insert(1, "Time")

        # reorder the dataframe, note frame number in 0 position remains
        merged_trajectories = merged_trajectories.reindex(columns=column_order)

        return merged_trajectories

    def create_trajectory_csv(self, csv_filename):          
        self.trajectories.to_csv(csv_filename, index=False)


    # Convert a human readable csv to a trc
    def create_trajectory_trc(self, trc_filename):
        
        num_markers = 33
        data_rate= self.camera_rate # not sure how this is different from camera rate
        camera_rate= self.camera_rate
        units = 'm'
        orig_data_rate = 25
        orig_data_start_frame = 0

        trajectories_for_trc = self.trajectories


        # make a list of the trajectories to keep
        keep_trajectories = []
        for lm in self.model_landmarks:
            keep_trajectories.append(lm+"_x")
            keep_trajectories.append(lm+"_y")
            keep_trajectories.append(lm+"_z")

        print(keep_trajectories)

        # going to recreate these later after potentially dropping frames
        trajectories_for_trc = trajectories_for_trc[keep_trajectories]
        

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
            for trajectory in self.model_landmarks:
                header_names.append(trajectory)
                header_names.append("")
                header_names.append("")    

            tsv_writer.writerow(header_names)

            # create labels for x,y,z axes (below landmark names)
            header_names = ["",""]
            for i in range(1,len(self.model_landmarks)+1):
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

    def interpolate_trajectory_gaps(self):
        """
        Gap fill with a simple method just to play out IK for longer
        Future iterations of this may involve multiple methods, or perhaps
        a pose estimation function based on previous ML to patch data
        """
        self.trajectories.interpolate(method='polynomial', order=3, inplace=True)


GoodSession = "sesh_2022-08-10_10_33_12"
FMC_folder = Path("C:/Users/Mac Prible/FreeMocap_Data")
osim_file = "FMC_OpenSim\models\mediapipe_fullbody\mediapipe_fullbody_model.osim"

testSession = FMCSession(GoodSession, FMC_folder, osim_file=osim_file, camera_rate=25)

trc_filename = "FMC_OpenSim/trc/dao_yin_dropped_working.trc" 
testSession.create_trajectory_trc(trc_filename)


testSession.create_trajectory_csv("FMC_OpenSim/trc/dao_yin.csv")
testSession.interpolate_trajectory_gaps()

trc_filename = "FMC_OpenSim/trc/dao_yin_interpolated.trc" 
testSession.create_trajectory_trc(trc_filename)

# print(trajectories)