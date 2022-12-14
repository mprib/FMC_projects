# FreeMoCap to OpenSim

## Overview

The purpose of this code module is to automate the process of taking trajectory arrays from FreeMocap (FMC) output and applying the Inverse Kinematics (IK) of OpenSim.

## Current Roadmap

A proof of concept currently exists for a full body model, but it seemed that the skeletal model being used was insufficiently articulated to provide a high-value reconstruction. I plan to take a step back and focu on a refined hand model, building back to the shoulder, and so on.

Given changing underlying models and the high number of trajectories to manage for the hand, the current focus is on automating integration of the FMC trajectories with the OpenSim model, scaling, and inverse kinematic configutation files (all of which are in `.xml` format).

### Useful Reference

Discussion of the scaling xml file structure: <https://simtk-confluence.stanford.edu:8443/display/OpenSim/Scale+Setup+File>

### Punch List

#### Stage 1: Processing of Full Body "Dao Yin" steps

1. ~~produce a trc file from a freemocap session and given model~~
2. ~~produce a list of markers used in a given model~~
3. ~~produce a file summarizing each joint's placement relative to it's socket~~
   ~~1. note that this functional is programmed into xml_opensim.py but no test case as such yet~~
4. ~~update an osim model file based on in input of markers and the associated joints~~
5. ~~modify osim creation to have a template (for creation) and a target (for long term saving)~~
6. ~~unittest of add_marker method~~
7. ~~Create method to add markers in bulk from config spreadsheet~~
8. ~~automate updates of model scaling.xml~~
   1. ~~set template model name~~
   2. ~~set trc file~~
   3. ~~set output model name~~
   4. ~~set time range in trc~~
9. ~~modify an osim model to create a marker at the distal end of a segment~~
10. ~~run inverse kinematics on a trc file given a model~~
11. ~~modify a scaling file to change the input model~~
12. ~~modify a scaling file to change the output model~~
#### Stage 2: Apply Workflow to Hand Tracking

1. ~~Capture hand tracking skeleton.npy data~~
   1. *note: had to use full sized charuco* 
2. Convert hand tracking.npy to .trc
3. update hand model template to include markers at each joint
4. Create hand model scaling template
5. Run IK on hand tracked data
## Future Directions

Gap filling of trajectories will be an important component of a useful system, particularly for configurations without substantial camera redundancy. Machine learning tools may offer a way to back fill trajectories "good enough" for IK to finish the job.
