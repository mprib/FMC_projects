#!/bin/bash

WORKING_DIR="C:\Users\Mac Prible\Box\Research\FMC_projects\OpenSimModels\testOpenSimCmd"

read -p "Press [ENTER] to continue"

SCALE_XML=$WORKING_DIR"\IK_Setup_Pose2Sim_Body25b.xml"
echo "'""$SCALE_XML""'"

"'C:\OpenSim 4.4\bin\opensim-cmd.exe' run-tool '""$SCALE_XML""'"

echo "'C:\OpenSim 4.4\bin\opensim-cmd.exe' run-tool '""$SCALE_XML""'"

read -p "Press [ENTER] to continue"
# print the contents of the variable on screen