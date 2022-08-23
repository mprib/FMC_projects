import subprocess
from pathlib import Path

opensim_cmd = str(Path("C:/OpenSim 4.4/bin/opensim-cmd.exe"))
model_osim =str(Path("FMC_OpenSim\models\mediapipe_fullbody\mediapipe_fullbody_model.osim")) 
scale_xml = str(Path("FMC_OpenSim\models\mediapipe_fullbody\mediapipe_scaling.xml"))


commands = [opensim_cmd, 'run-tool', model_osim]
p1 = subprocess.run(commands, shell=True, stdout=subprocess.PIPE, text=True)
print(p1.stdout)


#TODO: fix the xml file to refer to the appropriate starting model
commands = [opensim_cmd, 'run-tool', scale_xml]
p1 = subprocess.run(commands, shell=True, stdout=subprocess.PIPE, text=True)
print(p1.stdout)
