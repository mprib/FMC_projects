# Creating a pipeline from FMC to OpenSim

## OpenSim Model

https://simtk-confluence.stanford.edu:8443/display/OpenSim/OpenSim+Models#

A sample model can be found [here](~/../pose2sim/pose2sim-main/Pose2Sim/Demo/opensim/Model_Pose2Sim_Body25b.osim)

## Pose2Sim

Tutorial is found [here](https://github.com/perfanalytics/pose2sim)

I believe that we can skip many of the steps that lead up to the creation of the 3D joint parameters. 

It looks like the filtering is specificed by a configuration file "Config.toml"

This config file also does many of the same triangulation activities that I suspect are duplicated by FMC. So I don't need to worry about those. Focus on the 3d filtering --> OpenSim setup
