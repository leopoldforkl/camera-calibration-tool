import cv2
import os
from datetime import datetime

# 1. Setup the snapshots directory
# exist_ok=True ensures the script doesn't crash if the folder already exists
save_folder = "snapshots"
os.makedirs(save_folder, exist_ok=True)

# 2. Hardware Setup
cam_path = '/dev/video2'
cap = cv2.VideoCapture(cam_path, cv2.CAP_V4L2)

if not cap.isOpened():
    print(f"Error: Could not open camera at {cam_path}.")
    exit()

# Set buffer size to 1 to prevent frame lag
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

# Force MJPG codec, 1080p, 30fps
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
cap.set(cv2.CAP_PROP_FPS, 30)

print("Stream running. Press 'SPACE' to save a full-res snapshot, 'q' to quit.")

# --- Video Loop ---
while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Can't receive frame. Exiting ...")
        break

    # --- Display Processing ---
    # Crop and resize for the live preview window only
    square_frame = frame[:, 420:1500]
    small_frame = cv2.resize(square_frame, (300, 300), interpolation=cv2.INTER_AREA)

    # Show the small preview
    cv2.imshow('300x300 Smooth Stream', small_frame)

    # --- Keyboard Controls ---
    # waitKey(1) listens for a key press for 1 millisecond
    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        # Quit the program
        break
    elif key == ord(' '): # The spacebar
        # Generate a unique filename using the current date and time
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{save_folder}/snapshot_{timestamp}.jpg"
        
        # Save the UNALTERED original 'frame' (1920x1080)
        cv2.imwrite(filename, frame)
        
        # Print confirmation to the terminal
        print(f"Snapshot successfully saved: {filename}")

# Clean up resources
cap.release()
cv2.destroyAllWindows()