import numpy as np
import cv2

class VEVID_Superfast:
    def __init__(self):
        self.vevid_lut = None
        self.V = None

    def array_mean_percent(self, image):
        return min(image.mean() / 89.25, 1.0)

    def generate_vevid_lut(self, V):
        """
        Generates and updates the lookup table for VEViD Lite+ based on the parameter P.
        The LUT is kept in floating-point precision for accurate calculations.
        
        Args:
        - P (float): VEViD parameter.
        """
        if self.V == V and self.vevid_lut is not None:
            return  # No need to regenerate the LUT if V hasn't changed
        
        b = 1 / (5 * V + 0.05)
        G = 1 - V**2
        
        # Generate LUT using vectorized operations for efficiency
        pixel_values = np.linspace(0, 1, 256, dtype=np.float32)
        lut_values = np.arctan2(-G * (pixel_values + b), pixel_values)
        lut_values = np.interp(lut_values, (lut_values.min(), lut_values.max()), (0, 255)).astype(np.uint8)
        
        self.vevid_lut = lut_values
        self.V = V

    def apply_vevid_lut(self, image, V):
        """
        Applies the VEViD Lite+ transformation to the V channel of an HSV image using the current LUT.
        
        Args:
        - image (numpy.ndarray): Input BGR image.
        - P (float): VEViD parameter to be used if LUT needs to be regenerated.
        
        Returns:
        - numpy.ndarray: Image with VEViD Lite+ transformed V channel, in BGR format.
        """
        self.generate_vevid_lut(V)
        
        # Convert image from BGR to HSV
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Apply LUT to V channel
        v_channel_transformed = cv2.LUT(hsv_image[:, :, 2], self.vevid_lut)
        
        # Replace V channel with transformed values and convert back to BGR
        hsv_image[:, :, 2] = v_channel_transformed
        bgr_transformed = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)
        
        return bgr_transformed
    
    def apply_adaptive_vevid_lut(self, image):
        # Convert image from BGR to HSV
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        vevid_input = hsv_image[:, :, 2]

        V = min(1 - self.array_mean_percent(vevid_input), 0.99)
        self.generate_vevid_lut(V)
        
        # Apply LUT to V channel
        v_channel_transformed = cv2.LUT(vevid_input, self.vevid_lut)
        
        # Replace V channel with transformed values and convert back to BGR
        hsv_image[:, :, 2] = v_channel_transformed
        bgr_transformed = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)
        
        return bgr_transformed