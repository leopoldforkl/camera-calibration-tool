# Interactive ChArUco Webcam Calibrator

A robust, screen-based camera calibration tool designed for 6D pose estimation setups. 

Standard OpenCV chessboard calibration often fails due to screen glare, extreme angles, or the camera physically blocking the screen (occlusion). This tool solves those issues by generating a **ChArUco board** (Chessboard + ArUco markers) directly on your monitor. 

Because each square contains a unique barcode, the algorithm can interpolate the grid even if only a fraction of the screen is visible.

## Features
* **Zero-Math Scaling:** Uses an interactive slider to match the digital grid to a physical ruler, eliminating pixel-density conversion math.
* **Occlusion Robust:** Can calibrate successfully even if the webcam window or glare covers large portions of the pattern.
* **Sub-Pixel Accuracy:** Automatically refines corner detection for highly accurate intrinsic matrices.

## Setup (Ubuntu / Conda)

1. Clone or download this repository.
2. Create and activate a Conda environment:
   ```bash
   conda create -n pose_env python=3.10 -y
   conda activate pose_env
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Verify Your Camera is running:
```bash
python webcam_stream.py
```

Run the calibration script:
```bash
python calibrate.py
```

### Phase 1: Physical Scaling
1. Turn off your room lights and maximize your screen brightness to reduce glare.
2. The script will open a full-screen ChArUco pattern.
3. Hold a physical ruler directly against your monitor.
4. Adjust the slider until the width of **one single square** measures exactly **20mm**.
5. Press `ENTER` to confirm.

### Phase 2: Capture
1. Your webcam feed will appear. Point it at the screen.
2. You will see green boxes around detected markers and blue dots/lines on the grid corners.
3. Move the camera to capture different angles (tilted left/right, up/down, close, and far).
4. Press `SPACE` to capture a frame (the screen will flash green).
5. **Tip:** Don't worry if the grid is partially blocked; if you see blue lines, it is safe to capture.

### Phase 3: Output
After 15 successful captures, the window will close and your terminal will output your specific **Camera Intrinsic Matrix** and **Distortion Coefficients**. Copy these into your pose estimation configuration files.