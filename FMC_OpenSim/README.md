# FreeMoCap to OpenSim

## Overview

The purpose of this code module is to automate the process of taking trajectory arrays from FreeMocap (FMC) output and applying the Inverse Kinematics (IK) of OpenSim. The development process will begin with a sample of trajectories collected earlier this week that I was able to generate a rough `.blend` file from.

## Current Roadmap (20220822)

A proof of concept currently exists for taking the output from FMC and generating a file from OpenSim. I am hoping to expand this by mapping to a more fine-grain model of the upper extremity. The plan is to begin with the hand, incorporating shoulder and neck into the IK model. As this will involve many periods of iteration and likely reformatting of code, it is important that I begin to build some tools that will help me to automate the iteration and to ensure that I do not break anything while undergoing the inevitable refactoring.

1. Create a test case that will perform the following unit tests:
   1. produce a trc file from a freemocap session and given model
   2. produce a list of markers used in a given model
   3. scale a model to a trc file
   4. run inverse kinematics on a trc file given a model
   5. modify an osim model to create a marker at the distal end of a segment
   6. modify a scaling file to change the input model
   7. modify a scaling file to change the output model
   8. modify a scaling file to define new scaling factors for a segment