

mediapipe_trajectories =  [
    "nose",
    "left_eye_inner",
    "left_eye",
    "left_eye_outer",
    "right_eye_inner",
    "right_eye",
    "right_eye_outer",
    "left_ear",
    "right_ear",
    "mouth_left",
    "mouth_right",
    "left_shoulder",
    "right_shoulder",
    "left_elbow",
    "right_elbow",
    "left_wrist",
    "right_wrist",
    "left_pinky",
    "right_pinky",
    "left_index",
    "right_index",
    "left_thumb",
    "right_thumb",
    "left_hip",
    "right_hip",
    "left_knee",
    "right_knee",
    "left_ankle",
    "right_ankle",
    "left_heel",
    "right_heel",
    "left_foot_index",
    "right_foot_index",
    "right_hand_wrist",
    "right_hand_thumb_cmc",
    "right_hand_thumb_mcp",
    "right_hand_thumb_ip",
    "right_hand_thumb_tip",
    "right_hand_index_finger_mcp",
    "right_hand_index_finger_pip",
    "right_hand_index_finger_dip",
    "right_hand_index_finger_tip",
    "right_hand_middle_finger_mcp",
    "right_hand_middle_finger_pip",
    "right_hand_middle_finger_dip",
    "right_hand_middle_finger_tip",
    "right_hand_ring_finger_mcp",
    "right_hand_ring_finger_pip",
    "right_hand_ring_finger_dip",
    "right_hand_ring_finger_tip",
    "right_hand_pinky_finger_mcp",
    "right_hand_pinky_finger_pip",
    "right_hand_pinky_finger_dip",
    "right_hand_pinky_finger_tip",
    "left_hand_wrist",
    "left_hand_thumb_cmc",
    "left_hand_thumb_mcp",
    "left_hand_thumb_ip",
    "left_hand_thumb_tip",
    "left_hand_index_finger_mcp",
    "left_hand_index_finger_pip",
    "left_hand_index_finger_dip",
    "left_hand_index_finger_tip",
    "left_hand_middle_finger_mcp",
    "left_hand_middle_finger_pip",
    "left_hand_middle_finger_dip",
    "left_hand_middle_finger_tip",
    "left_hand_ring_finger_mcp",
    "left_hand_ring_finger_pip",
    "left_hand_ring_finger_dip",
    "left_hand_ring_finger_tip",
    "left_hand_pinky_finger_mcp",
    "left_hand_pinky_finger_pip",
    "left_hand_pinky_finger_dip",
    "left_hand_pinky_finger_tip",
]

import json

landmarks = {}

filename = "mediapipe_landmarks.json"

for i in range(0,len(mediapipe_trajectories)):
    landmarks[i]=mediapipe_trajectories[i]

with open(filename, 'w') as json_file:
        json.dump(landmarks,json_file)



print(landmarks)