from skimage import img_as_float
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import normalized_root_mse
from skimage.transform import resize
from skimage import io


def mse_ssim(url1, url2):

    img1 = img_as_float((io.imread(url1)))
    img2 = img_as_float((io.imread(url2)))

    if (img1.shape != img2.shape):
        max0 = max(img1.shape[0], img2.shape[0])
        max1 = max(img1.shape[1], img2.shape[1])
        img2 = resize(img2, (max0, max1))
        img1 = resize(img1, (max0, max1))

    mse = normalized_root_mse(img1, img2, normalization='min-max')
    simiStruc = ssim(img1 , img2 , multichannel = True)

    indiceSimilitud = ((1 - mse) + simiStruc) / 2

    return indiceSimilitud
