import numpy as np
from skimage import io, color, img_as_float
from .utils import normalize

from .utils import normalize

class VLight:
    def __init__(self, row=None, col=None):
        """Initialize the VLight class

        Args:
            row (int, optional): height of the image to be processed. Defaults to None.
            col (int, optional): width of the image to be processed. Defaults to None.
        """
        self.row = row
        self.col = col
        self.vlight_lut = None
        self.v = None

    def generate_vlight_lut(self, v):
        """
        Generates and updates the lookup table for VLight based on the parameter v.
        The LUT is kept in floating-point precision for accurate calculations.
        
        Args:
        - v (float): VLight parameter.
        """
        if self.v == v and self.vlight_lut is not None:
            return
        
        b = 1 / (5 * v + 0.05)
        G = 1 - v**2
        
        # Generate LUT using vectorized operations for efficiency
        pixel_values = np.linspace(0, 1, 256, dtype=np.float32)
        lut_values = np.arctan2(-G * (pixel_values + b), pixel_values)
        lut_values = np.interp(lut_values, (lut_values.min(), lut_values.max()), (0, 255)).astype(np.uint8)
       
        self.vlight_lut = lut_values
        self.v = v
    
    def load_img(self, img_file=None, img_array=None):
        """load the image from an ndarray or from an image file

        Args:
            img_file (str, optional): path to the image. Defaults to None.
            img_array (np.ndarray, optional): image in the form of np.ndarray (RGB, np.uint8). Defaults to None.
        """
        if img_array is not None:
            self.img_rgb = img_as_float(img_array)
        else:
            self.img_rgb = img_as_float(io.imread(img_file))

        self.row = self.img_rgb.shape[0]
        self.col = self.img_rgb.shape[1]

    def apply_kernel(self, v, v_channel=False, lut=True):
        """
        Override the apply_kernel method to use the LUT-based approach for faster processing.
        
        Args:
        - img_array (np.ndarray): Input image array in BGR format.
        - v (float): VLight parameter for LUT generation.
        - color (bool, optional): Whether to apply the transformation to the S (color) channel instead of V. Defaults to False.
        - lut (bool, optional): Whether to apply the lut acceleration or not, defaults to True
        Returns:
        - np.ndarray: Enhanced image in BGR format.
        """
        if v_channel:
            ch = 1
        else:
            ch = 2

        if lut is True:
            # Convert the image from RGB to HSV
            img_hsv = (color.rgb2hsv(self.img_rgb) * 255).astype(np.uint8)
            
            # Generate the LUT based on the vlight parameter
            self.generate_vlight_lut(v)
           
            # Apply LUT to the selected channel (V or S)
            img_hsv[:, :, ch] = self.vlight_lut[img_hsv[:, :, ch]]
            print(self.vlight_lut.shape)
            print(img_hsv[:, :, ch].shape)

            # Convert the image back to BGR format
            self.vlight_output = (color.hsv2rgb(img_hsv) * 255).astype(np.uint8)
        else:
            # Convert the image from RGB to HSV
            img_hsv = color.rgb2hsv(self.img_rgb)

            # Apply VLight Algorithm to the selected channel (V or S)
            vlight_input = img_hsv[:, :, ch]
            b = 1 / (5 * v + 0.05)
            G = 1 - v**2
            vlight_phase = np.arctan2(-G * (vlight_input + b), vlight_input)
            vlight_phase_norm = normalize(vlight_phase)
            img_hsv[:, :, ch] = vlight_phase_norm

            # Convert the image back to BGR format
            self.vlight_output = (color.hsv2rgb(img_hsv) * 255).astype(np.uint8)

    def run(self, img_file, v, color=False, lut=True):
        """run the VLight algorithm

        Args:
            - img_file (str): path to the image
            - v (float): VLight Parameteter
            - color (bool, optional): whether to run color enhancement. Defaults to False.
            - lut (bool, optional): Whether to apply the lut acceleration or not, defaults to True
        Returns:
            np.ndarray: enhanced image
        """
        self.load_img(img_file=img_file)
        self.apply_kernel(v=v, v_channel=color, lut=lut)

        return self.vlight_output

    def run_img_array(self, img_array, v, color=False, lut=True):
        """run the VLight LUT accelerated algorithm

        Args:
            - img_array (np.ndarray): Input image array in BGR format.
            - v (float): VLight parameter.
            - color (bool, optional): whether to run color enhancement. Defaults to False.
            - lut (bool, optional): Whether to apply the lut acceleration or not, defaults to True
        Returns:
            np.ndarray: enhanced image
        """
        self.load_img(img_array=img_array)
        self.apply_kernel(v=v, v_channel=color, lut=lut)
        return self.vlight_output