import cv2
import tkinter as tk
from tkinter import filedialog
import numpy as np

# Global variables for RoI and augmentation settings
roi_points = []
clip_rect = (100, 100, 400, 400)
rotation_angle = 0

def load_video():
    file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.avi")])
    return file_path

def select_roi(event, x, y, flags, param):
    global roi_points
    if event == cv2.EVENT_LBUTTONDOWN:
        roi_points.append((x, y))
    elif event == cv2.EVENT_RBUTTONDOWN:
        roi_points = []

def clip(frame, x1, y1, x2, y2):
    return frame[y1:y2, x1:x2]

def rotate(frame, angle):
    height, width = frame.shape[:2]
    center = (width // 2, height // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(frame, rotation_matrix, (width, height))

def process_frame(frame):
    global roi_points, clip_rect, rotation_angle
    if roi_points:
        # Mask out everything outside the RoI
        mask = np.zeros_like(frame[:, :, 0])
        points = np.array(roi_points, np.int32)
        cv2.fillPoly(mask, [points], 255)
        frame = cv2.bitwise_and(frame, frame, mask=mask)
    
    # Apply additional augmentation operations on the frame
    frame = clip(frame, *clip_rect)
    frame = rotate(frame, rotation_angle)
    
    return frame

def browse_video():
    video_path = load_video()
    if video_path:
        apply_augmentation(video_path)

def apply_augmentation(video_path):
    cap = cv2.VideoCapture(video_path)
    
    def process_frame_wrapper():
        ret, frame = cap.read()
        if not ret:
            cap.release()
            return
        
        augmented_frame = process_frame(frame)
        
        # Convert the frame to RGB format for displaying in the Tkinter GUI
        augmented_frame = cv2.cvtColor(augmented_frame, cv2.COLOR_BGR2RGB)
        augmented_frame = cv2.resize(augmented_frame, (640, 480))  # Resize for display
        
        # Update the image on the canvas
        photo = tk.PhotoImage(data=cv2.imencode('.png', augmented_frame)[1].tobytes())
        canvas.create_image(0, 0, image=photo, anchor=tk.NW)
        canvas.image = photo
        
        # Schedule the next frame update
        root.after(10, process_frame_wrapper)
    
    process_frame_wrapper()

# Create the Tkinter GUI
root = tk.Tk()
root.title("Video Augmentation Application")

# Create a canvas to display the video frames
canvas = tk.Canvas(root, width=640, height=480)
canvas.pack()

# Add a button to load the video
load_button = tk.Button(root, text="Load Video", command=browse_video)
load_button.pack()

# Add a button to reset the RoI points
reset_button = tk.Button(root, text="Reset RoI", command=lambda: roi_points.clear())
reset_button.pack()

# Add a button to change the clipping rectangle
clip_button = tk.Button(root, text="Set Clip Rect", command=lambda: set_clip_rect())
clip_button.pack()

# Function to set the clipping rectangle
def set_clip_rect():
    global clip_rect
    clip_rect = (100, 100, 400, 400)  # Modify these values to change the clipping rectangle

# Function to set the rotation angle
def set_rotation_angle(angle):
    global rotation_angle
    rotation_angle = angle

# Add buttons to control rotation
rotate_left_button = tk.Button(root, text="Rotate Left", command=lambda: set_rotation_angle(rotation_angle + 10))
rotate_left_button.pack(side=tk.LEFT)

rotate_right_button = tk.Button(root, text="Rotate Right", command=lambda: set_rotation_angle(rotation_angle - 10))
rotate_right_button.pack(side=tk.LEFT)

# Start the Tkinter main loop
root.mainloop()
