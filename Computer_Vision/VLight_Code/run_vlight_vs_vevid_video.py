import os
import cv2
import numpy as np
import imageio.v3 as iio
from phycv.vlight import VLight
from phycv.vevid import VEVID

def main():
    # Indicate the video to be processed
    video_file = "./assets/input_videos/video_building.mp4"
    cap = cv2.VideoCapture(video_file)

    if not cap.isOpened():
        print("Error: Cannot open video file.")
        return

    output_path = "./output/"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Get video properties
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Create an empty array to store the VLight output
    vlight_out_vid = np.zeros((length, frame_h, frame_w, 3), dtype=np.uint8)
    vevid_out_vid = np.zeros((length, frame_h, frame_w, 3), dtype=np.uint8)

    # VLight parameters
    v = 0.70
    vlight = VLight()
    vevid = VEVID()

    # Process each frame
    concat_frames = []
    for i in range(length):
        ret, frame = cap.read()
        if not ret:
            break

        # Convert frame to RGB for consistency with the rest of the code (OpenCV default is BGR)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # VLight expects BGR frames, so process the frame using VLight
        vlight_output = vlight.run_img_array(img_array=frame_rgb, v=v, color=False, lut=True)
        vlight_out_vid[i] = vlight_output

        # Process the frame with vevid algorithm
        vevid_output = vevid.run_array(img_array=frame, S=1, T=0.01, b=(1 / (5 * v + 0.05)), G=(1 - v**2))
        vevid_out_vid[i] = vevid_output

        # Concatenate original, VLight, and vevid output side by side
        concat_frame = np.concatenate((frame_rgb, vlight_output, cv2.cvtColor(vevid_output, cv2.COLOR_RGB2BGR)), axis=1)
        concat_frames.append(concat_frame)

    print("Creating video...")

    # Create video from the processed frames
    iio.imwrite(os.path.join(output_path, "VLight_VEViD_video_demo.mp4"), concat_frames, fps=fps)

    # Release video capture
    cap.release()
    print("Processing complete.")

if __name__ == "__main__":
    main()
