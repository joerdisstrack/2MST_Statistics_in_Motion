# NOTE: Runs best locally due to package dependencies of MediaPipe

# import necessary libraries
import cv2
import mediapipe as mp
import seaborn as sns
import numpy as np

# initialize new pose object
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# and setup of drawing utils from MediaPipe
mp_drawing = mp.solutions.drawing_utils

# set input path
input_path = "your_path"

# open file ...
cap = cv2.VideoCapture(input_path)

# ... and obtain

# frame width
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
# frame height
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
# and fps
fps = cap.get(cv2.CAP_PROP_FPS)

# set output path
output_path = "your_path"

# set codec for mp4 files
fourcc = cv2.VideoWriter_fourcc(*'mp4v')

# initialize VideoWrite object that saves result-video
out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

# set husl colour palette by Seaborn to distinguish markers easily for all landmarks
palette = sns.color_palette("husl", 33)

# define helper function that converts RGB (used by Seaborn) to BGR for OpenCV
def sns_to_bgr(color):
    return tuple(int(c * 255) for c in reversed(color))

# define colours per landmark...
landmark_colors = [sns_to_bgr(color) for color in palette]

# ... and map joint names to a colour
landmark_color_map = {
    mp_pose.PoseLandmark.NOSE: landmark_colors[0],
    mp_pose.PoseLandmark.LEFT_EYE: landmark_colors[1],
    mp_pose.PoseLandmark.RIGHT_EYE: landmark_colors[2],
    mp_pose.PoseLandmark.LEFT_EAR: landmark_colors[3],
    mp_pose.PoseLandmark.RIGHT_EAR: landmark_colors[4],
    mp_pose.PoseLandmark.LEFT_SHOULDER: landmark_colors[5],
    mp_pose.PoseLandmark.RIGHT_SHOULDER: landmark_colors[6],
    mp_pose.PoseLandmark.LEFT_ELBOW: landmark_colors[7],
    mp_pose.PoseLandmark.RIGHT_ELBOW: landmark_colors[8],
    mp_pose.PoseLandmark.LEFT_WRIST: landmark_colors[9],
    mp_pose.PoseLandmark.RIGHT_WRIST: landmark_colors[10],
    mp_pose.PoseLandmark.LEFT_HIP: landmark_colors[11],
    mp_pose.PoseLandmark.RIGHT_HIP: landmark_colors[12],
    mp_pose.PoseLandmark.LEFT_KNEE: landmark_colors[13],
    mp_pose.PoseLandmark.RIGHT_KNEE: landmark_colors[14],
    mp_pose.PoseLandmark.LEFT_ANKLE: landmark_colors[15],
    mp_pose.PoseLandmark.RIGHT_ANKLE: landmark_colors[16],
    mp_pose.PoseLandmark.LEFT_HEEL: landmark_colors[17],
    mp_pose.PoseLandmark.RIGHT_HEEL: landmark_colors[18],
    mp_pose.PoseLandmark.LEFT_FOOT_INDEX: landmark_colors[19],
    mp_pose.PoseLandmark.RIGHT_FOOT_INDEX: landmark_colors[20]
}

# set background to black - easy to remove
blank_frame = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)

# and begin processing input video frame by frame
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # first, convert frame to RGB for MediaPipe
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # then, extract pose landmarks
    results = pose.process(frame_rgb)

    # set on black background
    skeleton_frame = blank_frame.copy()

    # if coordinates were obtained:
    if results.pose_landmarks:
        # draw skeleton using landmark-coordinates
        for idx, landmark in enumerate(results.pose_landmarks.landmark):
            # set x- and y-coordinates and place in width/heights requirements
            x = int(landmark.x * frame_width)
            y = int(landmark.y * frame_height)

            # set colour
            landmark_color = landmark_color_map.get(mp_pose.PoseLandmark(idx), (255, 255, 255))

            # place a round marker on top of joints
            cv2.circle(skeleton_frame, (x, y), 5, landmark_color, -1)

        # and use predefined colour palette to draw edges between landmarks for all connection pairs
        for connection in mp_pose.POSE_CONNECTIONS:

            # select first of pair
            start_idx = connection[0]

            # and select second of pair
            end_idx = connection[1]

            # and define start and end points of edges based on coordinates
            start_point = results.pose_landmarks.landmark[start_idx]
            end_point = results.pose_landmarks.landmark[end_idx]

            # convert to pixels
            start_coords = (int(start_point.x * frame_width), int(start_point.y * frame_height))
            end_coords = (int(end_point.x * frame_width), int(end_point.y * frame_height))

            # use colour of start point to set colour of edge
            color = landmark_color_map.get(mp_pose.PoseLandmark(start_idx), (255, 255, 255))

            # and finally draw edge
            cv2.line(skeleton_frame, start_coords, end_coords, color, 2)

    # write to output-file
    out.write(skeleton_frame)

    # show the final results to check if correct
    cv2.imshow('Skeleton Only', skeleton_frame)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

# release video capture and writer objects
cap.release()
out.release()

# close OpenCV window
cv2.destroyAllWindows()
