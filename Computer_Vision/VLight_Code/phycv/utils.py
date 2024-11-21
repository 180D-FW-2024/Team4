import numpy as np


def normalize(x):
    """normalize the input to 0-1

    Args:
        x (np.ndarray or torch.Tensor): input array or tensor

    Returns:
        np.ndarray or torch.Tensor
    """
    return (x - x.min()) / (x.max() - x.min())


def cart2pol(x, y):
    """convert cartesian coordiates to polar coordinates

    Args:
        x (np.ndarray): cartesian coordinates in x direction
        y (np.ndarray): cartesian coordinates in y direction

    Returns:
        tuple: polar coordinates theta and rho
    """
    theta = np.arctan2(y, x)
    rho = np.hypot(x, y)
    return (theta, rho)



def denoise(img, rho, sigma_LPF):
    """apply a low pass filter to denoise the image

    Args:
        img (np.ndarray): original image
        rho (np.ndarray): polar coordinates
        sigma_LPF (float): variance of the low pass filter

    Returns:
        np.ndarray: denoised image
    """
    img_orig_f = np.fft.fft2(img)
    expo = np.fft.fftshift(
        np.exp(
            -0.5 * np.power((np.divide(rho, np.sqrt((sigma_LPF**2) / np.log(2)))), 2)
        )
    )
    img_filtered = np.real(np.fft.ifft2((np.multiply(img_orig_f, expo))))

    return img_filtered


def morph(img, feature, thresh_min, thresh_max):
    """apply morphological operation to transform analog features to digial features

    Args:
        img (np.ndarray): original image
        feature (np.ndarray): analog feature
        thresh_min (0<= float <=1): minimum thershold, we keep features < quantile(feature, thresh_min)
        thresh_max (0<= float <=1): maximum thershold, we keep features < quantile(feature, thresh_min)

    Returns:
        np.ndarray: digital features (binary edge)
    """
    # downsample feature to reduce computational time of np.quantile() for large arrays
    if len(feature.shape) == 3:
        quantile_max = np.quantile(feature[::4, ::4, ::4], thresh_max)
        quantile_min = np.quantile(feature[::4, ::4, ::4], thresh_min)
    elif len(feature.shape) == 2:
        quantile_max = np.quantile(feature[::4, ::4], thresh_max)
        quantile_min = np.quantile(feature[::4, ::4], thresh_min)

    digital_feature = np.zeros(feature.shape)
    digital_feature[feature > quantile_max] = 1
    digital_feature[feature < quantile_min] = 1
    digital_feature[img < (np.amax(img) / 20)] = 0

    return digital_feature.astype(np.float32)
