### NOTE: The following code runs best locally.

# import necessary libraries
import cv2
import mediapipe as mp
import pandas as pd

# initialize MediaPose objects
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# set landmark names based on MediaPose documentation
landmark_names = [
    "nose", "left_eye_inner", "left_eye", "left_eye_outer",
    "right_eye_inner", "right_eye", "right_eye_outer",
    "left_ear", "right_ear",
    "mouth_left", "mouth_right",
    "left_shoulder", "right_shoulder",
    "left_elbow", "right_elbow",
    "left_wrist", "right_wrist",
    "left_pinky", "right_pinky",
    "left_index", "right_index",
    "left_thumb", "right_thumb",
    "left_hip", "right_hip",
    "left_knee", "right_knee",
    "left_ankle", "right_ankle",
    "left_heel", "right_heel",
    "left_foot_index", "right_foot_index"
]

# open mp4 video file
# change to your path:
video_path = "your_input_path.mp4"
cap = cv2.VideoCapture(video_path)

# initialize empty lists for landmark-coordinates and timestamps
landmarks_data = []
timestamps = []

# use openCV to obtain frames per second (fps)
fps = cap.get(cv2.CAP_PROP_FPS)

# error management to prevent crashes
if fps == 0:
    raise ValueError("Could not retrieve FPS. Please ensure the video file is valid.")

# now process each frame
frame_number = 0
success, frame = cap.read()

# and while processing was successful
while success:
    # convert colouring from BGR to RGB for each frame
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # process image recognized for frame and find the pose
    results = pose.process(image_rgb)

    # if results are not empty extract coordinates:
    if results.pose_landmarks:
        # and store in empty list per frame
        frame_landmarks = []

        # obtain specifically x, y, z-coordinates per frame for each landmark
        for i, landmark in enumerate(results.pose_landmarks.landmark):
            x = landmark.x
            y = landmark.y
            z = landmark.z

            # append coordinate-dimensions to frame's list
            frame_landmarks.extend([x, y, z])

        # and append data of single frame to landmarks list
        landmarks_data.append(frame_landmarks)

    # use fps to compute timestamp per frame
    timestamp = frame_number / fps
    timestamps.append(timestamp)

    # increment frame counter and check for success
    frame_number += 1
    success, frame = cap.read()

# document status after all frames have been processed
cap.release()
print("Pose landmarks and timestamps have been extracted.")

# prepare setup of dataframe by initializing columns-list
landmark_columns = []

# fill columns-list by extracting names from landmarks and adding dimension
for name in landmark_names:
    landmark_columns.extend([f'{name}_x', f'{name}_y', f'{name}_z'])

# populate dataframe
df = pd.DataFrame(landmarks_data, columns=landmark_columns)

# add timestamp and fps to dataframe
df['timestamp_seconds'] = timestamps
df['fps'] = fps

# standardize the y-coordinates for step tracking into range 0, 1
landmarks_y = [
    'nose_y', 'left_eye_inner_y', 'left_eye_y', 'left_eye_outer_y',
    'right_eye_inner_y', 'right_eye_y', 'right_eye_outer_y', 'left_ear_y',
    'right_ear_y', 'mouth_left_y', 'mouth_right_y', 'left_shoulder_y',
    'right_shoulder_y', 'left_elbow_y', 'right_elbow_y', 'left_wrist_y',
    'right_wrist_y', 'left_pinky_y', 'right_pinky_y', 'left_index_y',
    'right_index_y', 'left_thumb_y', 'right_thumb_y', 'left_hip_y',
    'right_hip_y', 'left_knee_y', 'right_knee_y', 'left_ankle_y',
    'right_ankle_y', 'left_heel_y', 'right_heel_y', 'left_foot_index_y',
    'right_foot_index_y'
]

# ... by inverting them
for landmark in landmarks_y:
    df[landmark] = 1 - df[landmark]

# save to csv
final_csv_path = "your_output_path.csv"
df.to_csv(final_csv_path, index=False)

# and update status
print("Data with timestamps and standardized values have been saved to working_example_1.csv")
