
# %%
from pathlib import Path
import xml.etree.ElementTree as ET
import xml.dom.minidom as md
import sys
import csv



# %%

repo = Path(__file__).parent.parent
osim_model = open(Path(repo, "tests","osim_models", "mediapipe_fullbody_model.osim"))

xmldom = md.parse(osim_model)
markers = xmldom.getElementsByTagName("Marker")

model_markers = []

for m in markers:
    model_markers.append(m.getAttribute("name"))

print(model_markers)

# %%
# Get a printout of all the markers and their location
# it seems that location is an elemement of only the markers
locations = xmldom.getElementsByTagName("location")
for l in locations:
    print(l.parentNode.getAttribute("name"))
    print(l.childNodes[0].data)


# %%

for m in markers:
    
    print(m.getAttribute("name"))
    print(m.getAttribute("location"))

# %%
# this doesn't seem to be giving me quite what I want
joint_nodes = xmldom.getElementsByTagName("PinJoint")

for j in joint_nodes:
    print(j.getAttribute("name"))

# %%
JointSet = xmldom.getElementsByTagName("JointSet")
objects = JointSet[0].getElementsByTagName("objects")
joint_nodes = objects[0].childNodes

with open("temp.csv", 'w') as out_csv:
    out_csv.write("Joint, Parent Socket, Child Socket \n")

    for j in joint_nodes:
        # print(node.nodeType)
        if j.nodeType == j.ELEMENT_NODE:
            joint_name = j.getAttribute("name")
            joint_socket_parent = j.getElementsByTagName("socket_parent_frame")[0].firstChild.nodeValue 
            joint_socket_child = j.getElementsByTagName("socket_child_frame")[0].firstChild.nodeValue
            out_csv.write("{}, {}, {} \n".format(joint_name, joint_socket_parent, joint_socket_child))

# %%
# Build a dictionary of the joint configurations

JointSet = xmldom.getElementsByTagName("JointSet")
objects = JointSet[0].getElementsByTagName("objects")
joint_nodes = objects[0].childNodes

joints = {}

for j in joint_nodes:
    # print(node.nodeType)
    if j.nodeType == j.ELEMENT_NODE:
        joint_name = j.getAttribute("name")
        joint_socket_parent = j.getElementsByTagName("socket_parent_frame")[0].firstChild.nodeValue 
        joint_socket_child = j.getElementsByTagName("socket_child_frame")[0].firstChild.nodeValue

        joints[joint_name] = {}
        joints[joint_name]["Parent_Socket"] = joint_socket_parent
        joints[joint_name]["Child_Socket"] = joint_socket_child

# %%
# build a function to return the joint axis given a socket frame

offset_frame_locations = {}
frames = JointSet = xmldom.getElementsByTagName("PhysicalOffsetFrame")

for f in frames:
    name = f.getAttribute("name")
    print(name)
    print(f.getElementsByTagName("socket_parent")[0].firstChild.nodeValue)
    print(f.getElementsByTagName("translation")[0].firstChild.nodeValue)

# %%
# export csv to a table for better inspection and handling later

with open("joints.csv", 'w') as f:
    f.write("Joint, Parent_Socket, Child_Socket \n")
    for key in joints.keys():
        f.write("{}, {}, {} \n".format(key, 
                                    joints[key]["Parent_Socket"], 
                                    joints[key]["Child_Socket"]))

# %%
# Basically going to go bak and try to start over with this
# I don't think my solution above was going to give me what I wanted

JointSet = xmldom.getElementsByTagName("JointSet")
objects = JointSet[0].getElementsByTagName("objects")
joint_nodes = objects[0].childNodes

for node in joint_nodes:
    if node.nodeType == node.ELEMENT_NODE:
        joint_name = node.getAttribute("name")
        print(joint_name)
        
        for element in node:
         print(node)

# %%
# Going to try to use ELement Tree to get some of this stuff
repo = Path(__file__).parent.parent
osim_path = Path(repo, "tests","osim_models", "mediapipe_fullbody_model.osim")

osim_tree = ET.parse(osim_path)

osim_root = osim_tree.getroot()

joint_csv = [["JointName", "PhysicalOffsetFrame", "Translation", "Socket_Parent"]]

for child in osim_root[0]:
    if child.tag == "JointSet":
        for child2 in child[0]:
            print("JointName: " + child2.attrib['name'])
            joint_name = child2.attrib['name']
            for child3 in child2:
                if child3.tag == "frames":
                    for child4 in child3:
                        print("    PhysicalOffsetFrame: " + child4.attrib['name'])
                        offset_frame = child4.attrib['name']
                        for child5 in child4:
                            if child5.tag == "translation":
                                print("        translation: " + child5.text)
                                translation = child5.text

                            if child5.tag == "socket_parent":
                                print("        socket_parent: " + child5.text)
                                socket_parent = child5.text
                        joint_csv.append([joint_name, offset_frame, translation, socket_parent])




# %%
