import os
import time
import cv2
import matplotlib.pyplot as plt
from PIL import Image
from phycv.vlight_skimage import VLight

def main():
    # Specify the image file path
    img_file = "./assets/input_images/street_scene.png"
    
    # Load the image in BGR format (OpenCV default)
    original_image_bgr = cv2.imread(img_file)
    
    # Convert the original image to RGB format for display purposes
    original_image_rgb = cv2.cvtColor(original_image_bgr, cv2.COLOR_BGR2RGB)
    
    # Define the output path and create the directory if it doesn't exist
    output_path = "./output/"
    os.makedirs(output_path, exist_ok=True)

    # VLight parameter
    v = 0.90

    # Initialize and run VLight (expects and outputs BGR format)
    vlight_cpu = VLight()
    start_time = time.time()
    vlight_output_rgb = vlight_cpu.run_img_array(img_array=original_image_rgb, v=v, color=False, lut=True)
    print(f"Time elapsed: {(time.time() - start_time) * 1000}")
    # Visualize the results
    fig, axes = plt.subplots(1, 2, figsize=(12, 8))

    # Display the original image in RGB format
    axes[0].imshow(original_image_rgb)
    axes[0].axis("off")
    axes[0].set_title("Original Image")

    # Display the VLight output in RGB format
    axes[1].imshow(vlight_output_rgb)
    axes[1].axis("off")
    axes[1].set_title("VLight Low-Light Enhancement")

    # Save the figure with both images displayed side by side
    plt.savefig(os.path.join(output_path, "VLight_CPU_compare.jpg"), bbox_inches="tight")

    # Save the VLight output in RGB format using PIL
    vlight_output_pil = Image.fromarray(vlight_output_rgb)
    vlight_output_pil.save(os.path.join(output_path, "VLight_CPU_output.jpg"))

if __name__ == "__main__":
    main()
    # No LUT: Time elapsed: 175.54783821105957