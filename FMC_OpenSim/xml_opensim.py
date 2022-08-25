
# %%
from pathlib import Path
# import xml.etree.ElementTree as ET
import lxml.etree as etree
import csv

# %%
# Going to try to use ELement Tree to get some of this stuff
repo = Path(__file__).parent.parent
osim_path = Path(repo, "tests","osim_models", "mediapipe_fullbody_model.osim")

osim_tree = etree.parse(osim_path)

osim_root = osim_tree.getroot()

joint_csv = [["JointName", "PhysicalOffsetFrame", "Translation", "Socket_Parent"]]

# %%

for joint in osim_root.findall("Model/JointSet/objects/"):
    joint_name = joint.attrib['name']
    for frame in joint.findall("frames/PhysicalOffsetFrame"):
        physical_offset_frame = frame.attrib['name']

        print(frame.findall("socket_parent")[0].text)
        print(frame.findall("translation")[0].text)

        # for parent in frame.findall("socket_parent"):
        #     socket_parent = parent.text
        # for translation in frame.findall("translation"):
        #     trans = translation.text
        #     # print(translation)
        #     # print(translation == '0 0 0')
       
            # joint_csv.append([joint_name, physical_offset_frame, "'" + trans, socket_parent])

with open('model_joints.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(joint_csv)
# %%

joint_csv = [["JointName", "PhysicalOffsetFrame", "Translation", "Socket_Parent"]]

for child in osim_root[0]:
    if child.tag == "JointSet":
        for child2 in child[0]:
            #print("JointName: " + child2.attrib['name'])
            joint_name = child2.attrib['name']
            for child3 in child2:
                if child3.tag == "frames":
                    for child4 in child3:
                        #print("    PhysicalOffsetFrame: " + child4.attrib['name'])
                        offset_frame = child4.attrib['name']
                        for child5 in child4:
                            if child5.tag == "translation":
                                #print("        translation: " + child5.text)
                                translation = child5.text

                            if child5.tag == "socket_parent":
                                #print("        socket_parent: " + child5.text)
                                socket_parent = child5.text
                        if translation != "0 0 0":
                            joint_csv.append([joint_name, offset_frame, "'" + translation, socket_parent])

with open('model_joints.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(joint_csv)   

# %%
joint_csv = [["JointName", "PhysicalOffsetFrame", "Translation", "Socket_Parent"]]


for joint in osim_root.xpath('Model/JointSet/objects')[0]:
    joint_name = joint.attrib['name']

    for frame in joint.xpath("frames/PhysicalOffsetFrame"):
        physical_offset_frame = name = frame.attrib['name']
        translation = frame.xpath("translation")[0].text
        socket_parent = frame.xpath("socket_parent")[0].text

        if translation != "0 0 0":
            joint_csv.append([joint_name, physical_offset_frame, "'" + translation, socket_parent])

for line in joint_csv:
    print(line)


with open('model_joints.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(joint_csv)   
# %%
