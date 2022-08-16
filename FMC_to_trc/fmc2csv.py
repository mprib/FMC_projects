# The purpose of this code module is to take the numpy output of freemocap and convert
# it to a human readable format that will become the hub of translation to other formats

# I am beginning with the code that I developed in a jupyter notebook 


# This code copied from https://github.com/freemocap/freemocap/wiki
import numpy as np
from pathlib import Path 
import pandas as pd

#openPoseData_nCams_nFrames_nImgPts_XYC = np.load(dataArrayPath / 'openPoseData_2d.npy') #2d data too, if you're into that

def get_trajectories(sessionID):

    FMC_Folder = Path("C:/Users/Mac Prible/FreeMocap_Data") #replace this with path to the unzipped session data folder, e.g. Path(r'C:/Users/Me/session_data_folder')
    dataArrayPath = FMC_Folder / sessionID / 'DataArrays'
    skeletonPath = dataArrayPath / 'mediaPipeSkel_3d.npy'
    return np.load(skeletonPath) #load 3d open pose data



GoodSession = "sesh_2022-08-10_10_33_12"


# Build list of lists that can be used to iterate
def trajectories2df(SessionID, frameNum, Axes= [0,2,1] , FlipAxis=[1,1,-1]):

    joint_trajectories = get_trajectories(SessionID)
    # These are the order of the axes as stored in the 
    x_axis = Axes[0]
    y_axis = Axes[1]
    z_axis = Axes[2]

    # flip axis in or
    flip_x = FlipAxis[0]
    flip_y = FlipAxis[1]
    flip_z = FlipAxis[2]

    sk_x = (joint_trajectories[frameNum, :, x_axis] * flip_x).tolist()   # skeleton x data
    sk_y = (joint_trajectories[frameNum, :, y_axis] * flip_y).tolist()   # skeleton y data
    sk_z = (joint_trajectories[frameNum, :, z_axis] * flip_z).tolist()   # skeleton z data
    sk_index = [i for i in range(0, joint_trajectories.shape[1])]              # get a list of the index numbers of each observation




GoodSession = "sesh_2022-08-10_10_33_12"
PlotInteractiveFrame(GoodSession, 200)