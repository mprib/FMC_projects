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

--


## OpenSim Model

https://simtk-confluence.stanford.edu:8443/display/OpenSim/OpenSim+Models#

A sample model can be found [here](~/../pose2sim/pose2sim-main/Pose2Sim/Demo/opensim/Model_Pose2Sim_Body25b.osim)

---

I am running into some issues getting the output of this to run successfully, so I'm going to go ahead and just back off to the simpler thing: go through Tutorial #3 for open sim, which I think is the relevant introductory information:

https://simtk-confluence.stanford.edu:8443/display/OpenSim/Tutorial+3+-+Scaling%2C+Inverse+Kinematics%2C+and+Inverse+Dynamics

