import subprocess
exe_file = "C:/Program Files/Blender Foundation/Blender 3.2/blender.exe"
py_file = "C:/Users/Mac Prible/anaconda3/envs/freemocap-env/Lib/site-packages/freemocap/freemocap_blender_megascript.py"

blend_output = subprocess.run([exe_file, '--background', '--python', py_file], shell=True, stdout=subprocess.PIPE, text=True)

print(blend_output.stdout)