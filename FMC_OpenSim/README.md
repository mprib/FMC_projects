# FreeMoCap to OpenSim

## Overview

The purpose of this code module is to automate the process of taking trajectory arrays from FreeMocap (FMC) output and applying the Inverse Kinematics (IK) of OpenSim. The development process will begin with a sample of trajectories collected earlier this week that I was able to generate a rough `.blend` file from.

## Current Roadmap (20220822)

A proof of concept currently exists for taking the output from FMC and generating a file from OpenSim. I am hoping to expand this by mapping to a more fine-grain model of the upper extremity. The plan is to begin with the hand, incorporating shoulder and neck into the IK model. As this will involve many periods of iteration and likely reformatting of code, it is important that I begin to build some tools that will help me to automate the iteration and to ensure that I do not break anything while undergoing the inevitable refactoring.

1. Create a test case that will pull in a given session, model, scaling and IK files, then run scaling and IK on it in OpenSim
   1. create a method in FMCSession for calling OpenSim from the command line and providing the keyword arguments based on the file name.
