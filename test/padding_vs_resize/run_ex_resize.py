import onnxruntime as rt
import numpy as np
import cv2
from torchvision.transforms.functional import normalize
import torch
import os
from tqdm import tqdm

def img2tensor(imgs, bgr2rgb=True, float32=True):
    """Numpy array to tensor.

    Args:
        imgs (list[ndarray] | ndarray): Input images.
        bgr2rgb (bool): Whether to change bgr to rgb.
        float32 (bool): Whether to change to float32.

    Returns:
        list[tensor] | tensor: Tensor images. If returned results only have
            one element, just return tensor.
    """

    def _totensor(img, bgr2rgb, float32):
        if img.shape[2] == 3 and bgr2rgb:
            if img.dtype == 'float64':
                img = img.astype('float32')
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = torch.from_numpy(img.transpose(2, 0, 1))
        if float32:
            img = img.float()
        return img

    if isinstance(imgs, list):
        return [_totensor(img, bgr2rgb, float32) for img in imgs]
    else:
        return _totensor(imgs, bgr2rgb, float32)

def tensor2img(tensor, rgb2bgr=True, out_type=np.uint8, min_max=(0, 1)):
    """Convert torch Tensors into image numpy arrays.

    After clamping to [min, max], values will be normalized to [0, 1].

    Args:
        tensor (Tensor or list[Tensor]): Accept shapes:
            1) 4D mini-batch Tensor of shape (B x 3/1 x H x W);
            2) 3D Tensor of shape (3/1 x H x W);
            3) 2D Tensor of shape (H x W).
            Tensor channel should be in RGB order.
        rgb2bgr (bool): Whether to change rgb to bgr.
        out_type (numpy type): output types. If ``np.uint8``, transform outputs
            to uint8 type with range [0, 255]; otherwise, float type with
            range [0, 1]. Default: ``np.uint8``.
        min_max (tuple[int]): min and max values for clamp.

    Returns:
        (Tensor or list): 3D ndarray of shape (H x W x C) OR 2D ndarray of
        shape (H x W). The channel order is BGR.
    """
    if not (torch.is_tensor(tensor) or (isinstance(tensor, list) and all(torch.is_tensor(t) for t in tensor))):
        raise TypeError(f'tensor or list of tensors expected, got {type(tensor)}')

    if torch.is_tensor(tensor):
        tensor = [tensor]
    result = []
    for _tensor in tensor:
        _tensor = _tensor.squeeze(0).float().detach().cpu().clamp_(*min_max)
        _tensor = (_tensor - min_max[0]) / (min_max[1] - min_max[0])

        n_dim = _tensor.dim()
        if n_dim == 4:
            img_np = make_grid(_tensor, nrow=int(math.sqrt(_tensor.size(0))), normalize=False).numpy()
            img_np = img_np.transpose(1, 2, 0)
            if rgb2bgr:
                img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        elif n_dim == 3:
            img_np = _tensor.numpy()
            img_np = img_np.transpose(1, 2, 0)
            if img_np.shape[2] == 1:  # gray image
                img_np = np.squeeze(img_np, axis=2)
            else:
                if rgb2bgr:
                    img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        elif n_dim == 2:
            img_np = _tensor.numpy()
        else:
            raise TypeError(f'Only support 4D, 3D or 2D tensor. But received with dimension: {n_dim}')
        if out_type == np.uint8:
            # Unlike MATLAB, numpy.unit8() WILL NOT round by default.
            img_np = (img_np * 255.0).round()
        img_np = img_np.astype(out_type)
        result.append(img_np)
    if len(result) == 1:
        result = result[0]
    return result

model_name ="SF.11.onnx"
logger = open('a.txt', mode='w')

sess_options = rt.SessionOptions()

providers = ['CPUExecutionProvider']
# sess = rt.InferenceSession(model_name, providers=rt.get_available_providers())
sess = rt.InferenceSession(model_name, providers=providers)

input_name = sess.get_inputs()[0].name
output_name = sess.get_outputs()[0].name

root_path = r"padding/LQ/"

for file_name in tqdm(os.listdir(root_path)):
    if not file_name.endswith('.png'):
        continue
    source_img = cv2.imread(root_path + file_name)
    if (source_img.shape[0] >= 512) or (source_img.shape[0] >= 512):
        continue
    source_img_shape = source_img.shape
    reszie_img = cv2.resize(source_img, (512, 512))
    
    d = img2tensor(reszie_img / 255., bgr2rgb=True, float32=True)
    img_data=normalize(d, (0.5,0.5,0.5), (0.5,0.5,0.5), inplace=True)
    img_data = img_data.unsqueeze(0).to(torch.float16)
    pred = sess.run([output_name], {input_name: img_data.numpy()})[0]
    pred = torch.tensor(pred)
    save = tensor2img(pred.squeeze(0), rgb2bgr=True, min_max=(-1, 1))

    cv2.imwrite(r"resize_result/512/" + file_name, save)    
    save = cv2.resize(save, (source_img_shape[0], source_img_shape[1]))
    cv2.imwrite(r"resize_result/old/" + file_name, save)

logger.flush()
logger.close()
