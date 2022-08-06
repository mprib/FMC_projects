# Mac, this is a file that you created

from Pose2Sim import Pose2Sim
import os

print(os.path.join("Pose2Sim", "Demo","User", "Config.toml"))
print(os.path.abspath(os.path.join("Pose2Sim", "Demo","User", "Config.toml")))


Pose2Sim.triangulate3D(os.path.abspath(os.path.join("pose2sim", "Pose2Sim", "Demo","User", "Config.toml")))
Pose2Sim.filter3D(os.path.abspath(os.path.join("pose2sim", "Pose2Sim", "Demo","User", "Config.toml")))
