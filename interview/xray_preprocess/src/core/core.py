import typing

import cv2
import numpy as np
from pydicom.uid import generate_uid
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np
from scipy import ndimage
from skimage import filters, morphology, measure
from skimage.transform import rotate

def remove_black_background(img, threshold=10):
    # 找出非黑像素
    mask = img > threshold
    
    # 找 bounding box
    coords = np.argwhere(mask)
    y0, x0 = coords.min(axis=0)
    y1, x1 = coords.max(axis=0)
    
    # 裁切
    cropped = img[y0:y1+1, x0:x1+1]
    return cropped

def align_hand_xray(xray_image: np.ndarray) -> np.ndarray:
    plt.imshow(xray_image, cmap='gray')
    plt.show()
    
    img = xray_image.astype(np.float32)
    img_norm = img - img.min()
    img_norm = img_norm / (img_norm.max() + 1e-6)
    img_8u = (img_norm * 255).astype(np.uint8)

    # Binary mask
    _, mask = cv2.threshold(img_8u, 10, 255, cv2.THRESH_BINARY)

    # ---------------------------------------------------------
    # Step 2: Find largest contour = hand
    # ---------------------------------------------------------
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) == 0:
        return xray_image   # fallback, no change

    c = max(contours, key=cv2.contourArea)

    if len(c) < 5:
        return xray_image

    # ---------------------------------------------------------
    # Step 3: Ellipse fitting → get rotation angle
    # ---------------------------------------------------------
    ellipse = cv2.fitEllipse(c)
    angle = ellipse[2]  # default: long axis angle

    # Want long axis vertical → angle ≈ 90
    rotation_deg = angle - 90

    # ---------------------------------------------------------
    # Step 4: Rotate ORIGINAL image (preserve bit depth)
    # ---------------------------------------------------------
    h, w = xray_image.shape
    center = (w // 2, h // 2)

    M = cv2.getRotationMatrix2D(center, rotation_deg, 1.0)
    rotated = cv2.warpAffine(
        xray_image.astype(np.float32),  # 避免精度損失
        M,
        (w, h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=0
    )

    # Cast 回原始 dtype（保持 bit depth）
    rotated = rotated.astype(xray_image.dtype)

    # ---------------------------------------------------------
    # Step 5: Crop bounding box of rotated hand
    # ---------------------------------------------------------
    # create new mask from rotated (again using uint8)
    rot_norm = rotated.astype(np.float32)
    rot_norm = rot_norm - rot_norm.min()
    rot_norm = rot_norm / (rot_norm.max() + 1e-6)
    rot_8u = (rot_norm * 255).astype(np.uint8)

    _, rot_mask = cv2.threshold(rot_8u, 10, 255, cv2.THRESH_BINARY)
    contours2, _ = cv2.findContours(rot_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours2) == 0:
        return rotated

    c2 = max(contours2, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(c2)

    cropped = rotated[y:y+h, x:x+w]
    plt.imshow(cropped, cmap='gray')
    plt.show()
    return cropped


def save_processed_dicom(
    original_ds: np.ndarray, processed_img: np.ndarray, parent_path: Path
) -> typing.Tuple[str, str]:
    ds = original_ds.copy()

    # 更新像素資料
    ds.PixelData = processed_img.astype(original_ds.pixel_array.dtype).tobytes()
    ds.Rows, ds.Columns = processed_img.shape

    # 生成新 UID（匿名化）
    new_uid = generate_uid()
    old_uid = ds.SOPInstanceUID
    ds.SOPInstanceUID = new_uid
    ds.save_as(str(parent_path / f"{new_uid}.dcm"))

    return old_uid, new_uid
