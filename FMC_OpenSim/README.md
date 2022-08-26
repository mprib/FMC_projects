# FreeMoCap to OpenSim

## Overview

The purpose of this code module is to automate the process of taking trajectory arrays from FreeMocap (FMC) output and applying the Inverse Kinematics (IK) of OpenSim. The development process will begin with a sample of trajectories collected earlier this week that I was able to generate a rough `.blend` file from.

## Current Roadmap (20220822)

A proof of concept currently exists for taking the output from FMC and generating a file from OpenSim. I am hoping to expand this by mapping to a more fine-grain model of the upper extremity. The plan is to begin with the hand, incorporating shoulder and neck into the IK model. As this will involve many periods of iteration and likely reformatting of code, it is important that I begin to build some tools that will help me to automate the iteration and to ensure that I do not break anything while undergoing the inevitable refactoring.

1. Create a test case that will perform the following unit tests:
   1. ~~produce a trc file from a freemocap session and given model~~
   2. ~~produce a list of markers used in a given model~~
   3. ~~produce a file summarizing each joint's placement relative to it's socket~~
      ~~1. note that this functional is programmed into xml_opensim.py but no test case as such yet~~
   4. *update an osim model file based on in input of markers and the associated joints*
      1. running into issues with modifying the xml file. I appear to be corruping the file
         1. copy the old file over in it's working form. 
         2. commit all changes
         3. rerun your modification script
         4. inspect differences in git
   5. scale a model to a trc file
   6. modify an osim model to create a marker at the distal end of a segment
   7. run inverse kinematics on a trc file given a model
   8. modify a scaling file to change the input model
   9.  modify a scaling file to change the output model
   10. modify a scaling file to define new scaling factors for a segment