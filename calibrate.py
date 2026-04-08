import cv2
import numpy as np
import os
import glob
from datetime import datetime

# --- Configuration & Setup ---
DICTIONARY = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
BOARD_PIXELS = 600
MARKER_PX = 150
SEPARATION_PX = 50
LINE_LENGTH_PX = 500

def step1_display_and_get_input():
    """Displays the ArUco board and captures physical length input from the user."""
    display_board = cv2.aruco.GridBoard((3, 3), MARKER_PX, SEPARATION_PX, DICTIONARY)
    board_img = display_board.generateImage((BOARD_PIXELS, BOARD_PIXELS))

    canvas = np.ones((800, 800, 3), dtype=np.uint8) * 255
    x_offset = (800 - BOARD_PIXELS) // 2
    canvas[50:650, x_offset:x_offset+BOARD_PIXELS] = cv2.cvtColor(board_img, cv2.COLOR_GRAY2BGR)

    line_start = (150, 700)
    line_end = (150 + LINE_LENGTH_PX, 700)
    cv2.line(canvas, line_start, line_end, (0, 0, 255), 4)
    
    cv2.putText(canvas, f"{LINE_LENGTH_PX} pixels length", (150, 690), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    user_input = ""
    print("\n[STEP 1] Look at the OpenCV window. Enter the physical length of the red line.")
    
    while True:
        frame = canvas.copy()
        prompt = f"Enter physical length in mm: {user_input}_"
        cv2.putText(frame, prompt, (150, 750), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
        cv2.putText(frame, "(Press ENTER when done)", (150, 780), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)

        cv2.imshow("Calibration Setup", frame)
        key = cv2.waitKey(0)

        if key in [13, 10]:
            if user_input.replace('.', '', 1).isdigit():
                break
            else:
                print("Please enter a valid number.")
                user_input = ""
        elif key in [8, 127]:
            user_input = user_input[:-1]
        elif 48 <= key <= 57 or key == 46:
            user_input += chr(key)

    # --- THE FIX IS HERE ---
    # Instead of destroying the window, we paint a clean version of it 
    # to stay on your screen while you use the webcam.
    clean_frame = canvas.copy()
    cv2.putText(clean_frame, f"Length locked at {user_input} mm. Switch to Webcam!", 
                (100, 750), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 150, 0), 2)
    cv2.imshow("Calibration Setup", clean_frame)
    cv2.waitKey(1) # Force the UI to refresh before moving to Step 2
    
    return float(user_input)

def step2_capture_images(save_dir):
    """Opens webcam and allows user to capture images of the board."""
    os.makedirs(save_dir, exist_ok=True)
    
    cam_path = '/dev/video2'
    cap = cv2.VideoCapture(cam_path, cv2.CAP_V4L2)
    if not cap.isOpened():
        print(f"Error: Could not open camera at {cam_path}.")
        exit()

    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    cap.set(cv2.CAP_PROP_FPS, 30)

    print(f"\n[STEP 2] Webcam active. Press SPACE to capture images.")
    print("Take at least 10-15 photos from different angles/distances.")
    print("Press 'q' when you are finished to compute intrinsics.")

    count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        preview = cv2.resize(frame[:, 420:1500], (500, 500), interpolation=cv2.INTER_AREA)
        cv2.imshow("Webcam - SPACE to Snap, Q to Quit", preview)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord(' '):
            count += 1
            filename = f"{save_dir}/calib_{count:03d}.jpg"
            cv2.imwrite(filename, frame)
            print(f"[{count}] Saved: {filename}")

    cap.release()
    # --- THE FIX PART 2 ---
    # Now that we are done capturing, we close BOTH windows at the same time.
    cv2.destroyAllWindows()
    return count

def step3_compute_intrinsics(save_dir, physical_length_mm):
    """Computes camera matrix and distortion coefficients."""
    print("\n[STEP 3] Computing camera intrinsics...")
    
    px_to_mm = physical_length_mm / LINE_LENGTH_PX
    marker_len_mm = MARKER_PX * px_to_mm
    marker_sep_mm = SEPARATION_PX * px_to_mm
    
    print(f"Calculated Marker size: {marker_len_mm:.2f}mm, Separation: {marker_sep_mm:.2f}mm")

    physical_board = cv2.aruco.GridBoard((3, 3), marker_len_mm, marker_sep_mm, DICTIONARY)
    detector = cv2.aruco.ArucoDetector(DICTIONARY, cv2.aruco.DetectorParameters())

    image_files = glob.glob(f"{save_dir}/*.jpg")
    if len(image_files) < 5:
        print("Warning: You usually need at least 5-10 images for good calibration!")

    all_obj_points = []
    all_img_points = []
    image_size = None

    for file in image_files:
        img = cv2.imread(file)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if image_size is None:
            image_size = gray.shape[::-1]

        corners, ids, rejected = detector.detectMarkers(gray)

        if ids is not None and len(ids) > 0:
            obj_pts, img_pts = physical_board.matchImagePoints(corners, ids)
            if obj_pts is not None and len(obj_pts) > 3:
                all_obj_points.append(obj_pts)
                all_img_points.append(img_pts)

    if not all_obj_points:
        print("Failed: Could not find enough ArUco markers in the captured images.")
        return

    ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
        all_obj_points, all_img_points, image_size, None, None
    )

    print("\n--- Calibration Complete ---")
    print(f"Used {len(all_obj_points)} valid images out of {len(image_files)} captured.")
    print(f"Reprojection Error (lower is better): {ret:.4f}")
    print("\nCamera Intrinsics Matrix (K):")
    print(np.round(camera_matrix, 2))
    print("\nDistortion Coefficients:")
    print(np.round(dist_coeffs, 4))

if __name__ == "__main__":
    physical_mm = step1_display_and_get_input()
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    save_directory = os.path.join(script_dir, "snapshots", f"calibration_{timestamp}")
    
    images_taken = step2_capture_images(save_directory)
    if images_taken > 0:
        step3_compute_intrinsics(save_directory, physical_mm)
    else:
        print("No images were taken. Exiting.")