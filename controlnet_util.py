import torch

from diffusers import StableDiffusionControlNetPipeline, ControlNetModel, UNet2DConditionModel

controlnet = ControlNetModel.from_single_file("C:/code/pths/controlnet/models/control_sd15_scribble.pth")

# https://huggingface.co/docs/diffusers/main/en/api/models/controlnet#diffusers.ControlNetModel.forward
down_block_res_samples, mid_block_res_sample = controlnet(
        a,
        801,
        encoder_hidden_states=b,
        controlnet_cond=image,
        conditioning_scale=1.0,
        guess_mode=False,
        return_dict=False,
    )

c_unet = UNet2DConditionModel.from_pretrained(r"D:\lqh12\a-sd-based-models\sdv15", torch_dtype=torch.float16)

# https://huggingface.co/docs/diffusers/main/en/api/models/unet2d-cond#diffusers.UNet2DConditionModel.forward
output = c_unet()

# Omost
# https://huggingface.co/docs/diffusers/v0.20.0/en/api/pipelines/controlnet_sdxl#controlnet-with-stable-diffusion-xl
controlnet = ControlNetModel.from_pretrained(
    "diffusers/controlnet-canny-sdxl-1.0-small",
    torch_dtype=torch.float16
)

# https://huggingface.co/docs/diffusers/v0.20.0/en/api/pipelines/controlnet_sdxl#diffusers.StableDiffusionXLControlNetPipeline.__call__.example
