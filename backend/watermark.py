from backend.const import (ID_WMi_tuple, WStart, P, alpha, Delta)
from fastapi.exceptions import HTTPException
import cv2
from pathlib import Path
import numpy as np
import scipy.sparse
from scipy.fft import dctn, idctn
from skimage.color import rgb2ycbcr, ycbcr2rgb
import hashlib



def embed_watermark(input_path: Path, output_path: Path, ID_WMi: ID_WMi_tuple):
    """
    Add an invisible watermark to provided image.
    """

    Wi = int.from_bytes(hashlib.sha256(str(ID_WMi.Wi).encode('utf-8')).digest(), 'big')

    #  Algorithm constants
    L = ID_WMi.Li  # watermark length
    K = 2 * WStart + L  # LV vector size

    if K > P * (P + 1) / 2:
        raise HTTPException(400, "Watermark length (Li) too big")

    # Try to open the image
    I = cv2.imread(str(input_path))
    if I is None:
        raise HTTPException(400, "Unsupported file")

    # BGR -> RGB
    I = I[..., ::-1]

    # Generate, filter and shape the watermark
    AWMi = np.random.default_rng(seed=Wi).standard_normal(size=L)
    NCoef = 11
    AWMFi = np.zeros(L)

    for i in range(L - NCoef + 1):
        Sum = 0
        for j in range(NCoef):
            Sum += AWMi[i + j]
        AWMFi[i] = Sum

    AWMFi /= NCoef
    AWMFi[L - NCoef :] = AWMFi[:NCoef]

    Min = 0.2
    F = np.array(
        [(i * (1 - Min) + Min - L) / (1 - L) for i in range(1, L + 1)], dtype=np.float64
    )

    WMi = AWMFi * F
    WMi = (1 / np.std(WMi, ddof=1)) * WMi

    # Convert image to YCbCr color space and apply DCT transform to the Y (luminance) channel
    I_double = I.astype(np.float64) / 255
    YCBCR_Image = rgb2ycbcr(I_double) / 255
    Y_Image = YCBCR_Image[..., 0]
    DCT_I = dctn(Y_Image, norm="ortho")

    Size_DCT_I = DCT_I.shape
    if ID_WMi.ni + P - 1 > Size_DCT_I[0] or ID_WMi.mi + P - 1 > Size_DCT_I[1]:
        raise HTTPException(
            400,
            "Choose smaller starting row and column. Also make sure that the image that is being processed is at least 256x256.",
        )

    # Extract DCT coef. in a matrix EA, than traverse it in zig-zag fashion to form LV
    DCT_IW = DCT_I.copy()
    EA = DCT_IW[ID_WMi.ni - 1 : ID_WMi.ni - 1 + P, ID_WMi.mi - 1 : ID_WMi.mi - 1 + P]
    LV = np.concatenate([np.diagonal(EA[::-1, :], k)[::-1] for k in range(1 - P, 1)])

    # Embed the watermark in the linear vector
    WEnd = WStart + L - 1
    DLV = np.std(LV[WStart - 1 : WEnd], ddof=1)
    WMV = LV
    WMV[WStart - 1 : WEnd] = LV[WStart - 1 : WEnd] + alpha * DLV * WMi

    # Reconstruct the matrix from the modified vector
    indices = np.cumsum(np.concatenate([np.arange(1, P), [P], np.arange(1, P)[::-1]]))[
        : P - 1
    ]
    diags = (x[::-1] for x in np.split(WMV, indices))
    diags_matrix = scipy.sparse.diags(diags, range(-P + 1, 1), (P, P)).toarray()[::-1]
    mask = np.tri(P, dtype=bool)[::-1]
    np.putmask(EA, mask, diags_matrix)

    # Perform inverse DCT to get back to the Y (Luminance) channel
    WMI_Y = idctn(DCT_IW, norm="ortho")

    # Apply the new channel to the image and convert it back to RGB
    YCBCR_WImage = YCBCR_Image.copy()
    YCBCR_WImage[..., 0] = WMI_Y
    WMI = ycbcr2rgb((YCBCR_WImage * 255)).clip(0, 1)

    # Save the watermarked image
    cv2.imwrite(
        str(output_path),
        cv2.cvtColor(((WMI * 255).astype(np.float32)), cv2.COLOR_RGB2BGR),
    )



def read_watermark(input_path: Path, ID_WMi: ID_WMi_tuple):
    """
    Check if the provided image contains an invisible watermark.
    """
    Wi = int.from_bytes(hashlib.sha256(str(ID_WMi.Wi).encode('utf-8')).digest(), 'big')

    #  Algorithm constants
    L = ID_WMi.Li  # watermark length
    K = 2 * WStart + L  # LV vector size

    if K > P * (P + 1) / 2:
        raise HTTPException(400, "Watermark length (Li) too big")

    # Try to open the image
    I = cv2.imread(str(input_path))
    if I is None:
        raise HTTPException(400, "Unsupported file")

    # BGR -> RGB, unit8 -> float64
    I = I[..., ::-1].astype(np.float64)

    # Generate, filter and shape the watermark
    AWMi = np.random.default_rng(seed=Wi).standard_normal(size=L)
    NCoef = 11
    AWMFi = np.zeros(L)
    for i in range(L - NCoef + 1):
        Sum = 0
        for j in range(NCoef):
            Sum += AWMi[i + j]
        AWMFi[i] = Sum
    AWMFi /= NCoef
    AWMFi[L - NCoef :] = AWMFi[:NCoef]

    Min = 0.2
    F = np.array(
        [(i * (1 - Min) + Min - L) / (1 - L) for i in range(1, L + 1)], dtype=np.float64
    )

    WMi = AWMFi * F
    WMi = (1 / np.std(WMi, ddof=1)) * WMi

    # Convert image to YCbCr color space and apply DCT transform to the Y (luminance) channel
    I_double = I.astype(np.float64) / 255
    YCBCR_Image = rgb2ycbcr(I_double) / 255
    WMI_Y = YCBCR_Image[..., 0]
    DCT_WMIm = dctn(WMI_Y, norm="ortho")

    Size_DCT_WMIm = DCT_WMIm.shape
    if ID_WMi.ni + P - 1 > Size_DCT_WMIm[0] or ID_WMi.mi + P - 1 > Size_DCT_WMIm[1]:
        raise HTTPException(
            400,
            "Choose smaller starting row and column. Also make sure that the image that is being processed is at least 256x256.",
        )

    # Extract DCT coef. in a matrix EAm, than traverse it in zig-zag fashion to form LVm
    EAm = DCT_WMIm[ID_WMi.ni - 1 : ID_WMi.ni + P - 1, ID_WMi.mi - 1 : ID_WMi.mi + P - 1]
    LVm = np.concatenate([np.diagonal(EAm[::-1, :], k)[::-1] for k in range(1 - P, 1)])

    # Extract only the data needed for correlation and remove any offset
    LVm1 = LVm[:K]
    LVm1 = LVm1 - np.mean(LVm1)
    WMi1 = WMi - np.mean(WMi)

    # Cross-correlation function
    Cxy = np.array(
        [np.sum(LVm1[i : L + i] * WMi1) / L for i in range(2 * WStart)],
        dtype=np.float64,
    )
    I_Max = np.argmax(Cxy)

    # Watermark check based on Cxy maximum
    if I_Max < (WStart - Delta - 1) or I_Max > (WStart + Delta - 1):
        is_watermarked = False
    else:
        is_watermarked = True

    return {"is_watermarked": is_watermarked}