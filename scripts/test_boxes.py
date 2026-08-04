import json
from PIL import Image

with open('/home/admin_/duhua/frontend/src/mockOcrData.json', 'r') as f:
    data = json.load(f)

img = Image.open('/home/admin_/duhua/temp1.webp')
w, h = img.size
print(f"Original image size: {w}x{h}")

for i, item in enumerate(data[:3]):
    print(f"Box {i} (text: {item['text']}): {item['box']}")

