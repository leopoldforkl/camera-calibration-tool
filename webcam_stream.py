import cv2

# Hardcode the exact device path to avoid index confusion
cam_path = '/dev/video2'

# Open the specific camera using the V4L2 backend
cap = cv2.VideoCapture(cam_path, cv2.CAP_V4L2)

if not cap.isOpened():
    print(f"Error: Could not open camera at {cam_path}.")
    exit()

# Set buffer size to 1 to prevent frame lag and tearing
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

# --- Hardware Optimization Settings ---
#Force MJPG codec first to unlock 30fps at 1080p
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

# Set resolution to 1920x1080
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

# Set framerate to 30 FPS
cap.set(cv2.CAP_PROP_FPS, 30)

# Verify what the camera actually accepted
actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
actual_fps = cap.get(cv2.CAP_PROP_FPS)
print(f"Hardware accepted streaming at: {int(actual_width)}x{int(actual_height)} @ {actual_fps} FPS")

# --- Video Loop ---
while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Can't receive frame. Exiting ...")
        break


    # --- 2. Crop 16:9 to 1:1 Square ---
    # The frame is 1920x1080. We slice a 1080x1080 square right out of the middle.
    # Height is all rows (:). Width is columns from 420 to 1500.
    square_frame = frame[:, 420:1500]

    # --- 3. Resize to 300x300 ---
    # INTER_AREA is the secret sauce here. It averages the pixels as it shrinks them,
    # which naturally smooths out Gaussian noise.
    small_frame = cv2.resize(square_frame, (300, 300), interpolation=cv2.INTER_AREA)

    # Display the frame in a window
    cv2.imshow('300x300 Smooth Stream', small_frame)

    # Listen for the 'q' key to exit cleanly
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Clean up resources
cap.release()
cv2.destroyAllWindows()