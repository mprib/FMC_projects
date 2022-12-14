# %%

from pathlib import Path

from requests import session
import fmc2trc
import osim_xml


repo = Path(__file__).parent.parent

FMC_folder = Path("C:\\", "users", "Mac Prible", "FreeMocap_Data")
session_ID = "sesh_2022-08-30_11_06_41"
data_array = "mediaPipeSkel_3d_smoothed_unrotated.npy"


# print(repo)

# %%
# first order of business is to pull the joint names from the osim file
# and then assign model markers to them

model_template_path = Path(repo,"FMC_OpenSim", "models", "fmc_hand_model", "fmc_hand_model_template_no_muscles.osim")
hand_model = osim_xml.OsimModelTemplate(model_template_path, Path(FMC_folder, session_ID, "OpenSim", "fmc_hand_model.osim"))


################ Only needs to be done once to build the landmark map, which is do
# hand_joint_xls_path = Path(repo,"FMC_OpenSim", "models", "fmc_hand_model", "hand_joints.xlsx")
# hand_model.create_joint_loc_xlsx(hand_joint_xls_path)

# %% Now go update the .osim file to include these markers that have been
# manually identified in the spreadsheet

map_path = Path(FMC_folder, session_ID, "OpenSim", "hand_joints_marker_map.xlsx")
hand_model.add_ModelLandmarkMap(map_path, map_sheet_name="LandmarkMap")


# %% with markers in the model, actually create the .trc file


hand_recording = fmc2trc.FMCSession(session_ID, FMC_folder, data_array ,25, hand_model.osim_path)

hand_recording.create_trajectory_trc(Path(FMC_folder, session_ID, "OpenSim", "mediapipe_hand.trc"), drop_na=True)
hand_recording.create_trajectory_csv(Path(FMC_folder, session_ID, "OpenSim", "mediapipe_hand.csv"))

# %%

# from pathlib import Path
# import lxml.etree as etree

# repo = Path(__file__).parent.parent

# osim_model = Path(repo,"FMC_OpenSim", "models", "fmc_hand_model", "fmc_hand_model_template_no_muscles.osim")

# xml_parser = etree.XMLParser(remove_blank_text=True)
# osim_tree = etree.parse(osim_model, xml_parser)
# osim_root = osim_tree.getroot()

# for body in osim_root.xpath("//WrapObjectSet"):
#     print(body.attrib['name'])
#     body.getparent().remove(body)


# etree.ElementTree(osim_root).write(osim_model, pretty_print=True)
# %%
