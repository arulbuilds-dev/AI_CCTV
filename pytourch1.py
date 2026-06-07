import torch

print("Torch Version:", torch.__version__)
print("CUDA Runtime:", torch.version.cuda)
print("CUDA Available:", torch.cuda.is_available())
print("GPU Count:", torch.cuda.device_count())

if torch.cuda.is_available():
    print("GPU Name:", torch.cuda.get_device_name(0))