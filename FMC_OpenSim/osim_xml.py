
# %%
from pathlib import Path
import lxml.etree as etree
import pandas as pd



class OsimModel():

    def __init__(self, osim_path):
        self.osim_tree = etree.parse(osim_path)
        self.osim_root = self.osim_tree.getroot()        


    def get_joint_locations(self):

        joint_locations = []

        for joint in self.osim_root.xpath('Model/JointSet/objects')[0]:
            joint_name = joint.attrib['name']

            for frame in joint.xpath("frames/PhysicalOffsetFrame"):
                physical_offset_frame = frame.attrib['name']
                translation = frame.xpath("translation")[0].text
                socket_parent = frame.xpath("socket_parent")[0].text

                if translation != "0 0 0":
                    # addition of the ' in translation is to avoid errors if opened in excel
                    joint_locations.append([joint_name, physical_offset_frame, "'" + translation, socket_parent])
        
        
        columns = [["JointName", "PhysicalOffsetFrame", "Translation", "Socket_Parent"]]

        return pd.DataFrame(joint_locations, columns=columns)


    def create_joint_loc_csv(self, csv_path):
        joint_loc_df = self.get_joint_locations()
        joint_loc_df.to_csv(csv_path)

# with open('../tests/reference/model_joints.csv', 'w', newline='') as f:
#     writer = csv.writer(f)
#     writer.writerows(joint_csv)   
# %%
