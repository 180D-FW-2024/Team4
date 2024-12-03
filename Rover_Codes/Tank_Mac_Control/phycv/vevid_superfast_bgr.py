import numpy as np
import cv2

class VEVID_Superfast_BGR:
    def __init__(self):
        self.vevid_lut = None
        self.V = None
    
    def array_mean_percent(self, image):
        return min(image.mean() / 89.25, 1.0)

    def generate_vevid_lut(self, V):
        """
        Generates and updates the lookup table for VEViD Lite+ based on the parameter P.
        
        Args:
        - P (float): VEViD parameter.
        """
        if self.V == V and self.vevid_lut is not None:
            return
        b = 1 / (5 * V + 0.05)
        G = 1 - V**2
        # Precompute the VEViD Lite+ transformation for each possible pixel value
        lut = np.array([np.arctan2(-G * (pixel_value / 255.0 + b), pixel_value / 255.0) for pixel_value in range(256)])
        # Normalize the output to the range [0, 1] and then scale to [0, 255]
        lut = 255 * (lut - np.min(lut)) / (np.max(lut) - np.min(lut))
        self.vevid_lut = lut.astype(np.uint8)
        self.V = V  # Update the current P value

    def apply_vevid_lut(self, image, V):
        """
        Applies VEViD Lite+ transformation to an image using the current lookup table.
        
        Args:
        - image (numpy.ndarray): Input image.
        - P (float): VEViD parameter.
        
        Returns:
        - numpy.ndarray: VEViD Lite+ transformed image.
        """
        self.generate_vevid_lut(V)
        # Apply VEViD Lite+ transformation using the lookup table
        vevid_transformed = cv2.LUT(image, self.vevid_lut)
        return vevid_transformed

    def apply_adaptive_vevid_lut(self, image):
        V = min(1 - self.array_mean_percent(image), 0.99)
        self.generate_vevid_lut(V)
        return cv2.LUT(image, self.vevid_lut)