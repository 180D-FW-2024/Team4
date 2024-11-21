import os
import cv2
import matplotlib.pyplot as plt
from PIL import Image

from phycv.vlight import VLight
from phycv.vevid import VEVID

def main():
    # indicate image file, height and width of the image
    img_file = "./assets/input_images/street_scene.png"
    original_image = cv2.imread(img_file)  # Load the original image in BGR format
    output_path = "./output/"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # VLight parameters
    v = 0.90

    # Run VLight CPU version (expects and outputs BGR)
    vlight_cpu = VLight()
    vlight_output_cpu = vlight_cpu.run(img_file=img_file, v=v, color=False, lut=True)

    # Run VEViD CPU version (expects and outputs BGR)
    vevid_cpu = VEVID()
    vevid_output_cpu = vevid_cpu.run(img_file=img_file, S=1, T=0.01, b=(1 / (5 * v + 0.05)), G=(1 - v**2))

    # Visualize the results
    f, axes = plt.subplots(1, 3, figsize=(18, 8))  # 3 images, so adjust figure size

    # Display original BGR image (converted to RGB for visualization)
    axes[0].imshow(cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB))
    axes[0].axis("off")
    axes[0].set_title("Original Image")

    # Display VLight output (converted to RGB for visualization)
    axes[1].imshow(cv2.cvtColor(vlight_output_cpu, cv2.COLOR_BGR2RGB))
    axes[1].axis("off")
    axes[1].set_title("PhyCV Low-Light Enhancement")

    # Display Vevid image (converted to RGB for visualization)
    axes[2].imshow(cv2.cvtColor(vevid_output_cpu, cv2.COLOR_BGR2RGB))
    axes[2].axis("off")
    axes[2].set_title("VEViD Image")

    # Save the figure with all three images displayed side by side
    plt.savefig(os.path.join(output_path, "VLight_VEViD_compare.jpg"), bbox_inches="tight")

    # Save the VLight output in BGR format as a separate image
    vlight_cpu_result = Image.fromarray(cv2.cvtColor(vlight_output_cpu, cv2.COLOR_BGR2RGB))
    vlight_cpu_result.save(os.path.join(output_path, "VLight_CPU_output.jpg"))

if __name__ == "__main__":
    main()
