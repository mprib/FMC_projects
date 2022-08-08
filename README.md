# Creating a pipeline from FMC to OpenSim


## Pose2Sim

Tutorial is found [here](https://github.com/perfanalytics/pose2sim)

I believe that we can skip many of the steps that lead up to the creation of the 3D joint parameters. 

It looks like the filtering is specificed by a configuration file "Config.toml"

This config file also does many of the same triangulation activities that I suspect are duplicated by FMC. So I don't need to worry about those. Focus on the 3d filtering --> OpenSim setup

I am getting hung up on the Filter3D step, so I'm going to close out and try to rerun. Also going to try to install pose2sim from the files rather than just pip.

I believe that Triangulation takes the json files and creates a .trc file from it. Filter then just transforms this file based on the filter configuration setup in Config.toml.

Success! The .trc file is now stored [here](pose2sim/Pose2Sim/Demo/pose-3d/Demo_filt_0-100.trc)

---

now the question...How to get this .trc file (which could be straighforwardly created from a sensible FMC output) into an OpenSim pipeline?

--_


## OpenSim Model

https://simtk-confluence.stanford.edu:8443/display/OpenSim/OpenSim+Models#

A sample model can be found [here](~/../pose2sim/pose2sim-main/Pose2Sim/Demo/opensim/Model_Pose2Sim_Body25b.osim)

---

I am running into some issues getting the output of this to run successfully, so I'm going to go ahead and just back off to the simpler thing: go through Tutorial #3 for open sim, which I think is the relevant introductory information:

https://simtk-confluence.stanford.edu:8443/display/OpenSim/Tutorial+3+-+Scaling%2C+Inverse+Kinematics%2C+and+Inverse+Dynamics

This is something that I was able to get to run successfully. Notably, after returning to the same open session a day later, I had to close and restart OpenSim to get it to run the animation.

---

Return to the process and do it again to confirm your understanding of it:

1. Open Model (.osim)
2. Scale the model (Tools--> Scale Model)
   1. **Load** a static .trc file in the static calibration pose
   2. This will create a new model which is a scaled version of the original model you opened.
3. Render Inverse Kinematics (Tools-->Inverse Kinematics)
   1. **Load** .xml file that specifies the IK
4. This will create a motion file that can then get played

So there are a few files that are necessary in order to perform this process:

1. Model definition (.osim)
2. Static calibration file for scaling (.trc)
3. Inverse Kinematics configuration file (.xml)
4. Motion trajectories (.trc)

# Calling OpenSim from Python

It looks like Opensim is not directly installable via pip and the methods to install the python wrappers to it may not integrate well with freemocap because of dependency clashes. To simplify the situation, the primary opensim-cmd can be called from the command line using `& "C:\OpenSim 4.4\bin\opensim-cmd.exe"`. Append the `run-tool` argument with an `.xml` setup file to evoke the desired computations (model scaling and inverse kinematics).

This workflow should enable tranformation of a .trc file to...wait...

What does the inverse kinematic file output? It's a .mot file, correct? 