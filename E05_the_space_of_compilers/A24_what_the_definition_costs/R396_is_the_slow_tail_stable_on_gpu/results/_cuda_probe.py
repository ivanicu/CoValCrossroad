import torch
assert torch.cuda.is_available(), 'no cuda'
a = torch.randn(256, 256, dtype=torch.bfloat16, device='cuda')
print('cuda_ok', torch.cuda.get_device_name(0), float((a @ a).float().sum()) == float((a @ a).float().sum()))
