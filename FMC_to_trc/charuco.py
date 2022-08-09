import cv2

aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_250) #note `cv2.aruco` can be installed via `pip install opencv-contrib-python`

board = cv2.aruco.CharucoBoard_create(4, 3, 1, .8, aruco_dict)

charuco_board_image = board.draw((4000,3000)) 

cv2.imwrite('charuco_board_image.png',charuco_board_image)