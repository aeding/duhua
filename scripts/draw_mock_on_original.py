import json
from PIL import Image, ImageDraw

def draw_boxes(img_path, json_path, out_path):
    img = Image.open(img_path)
    with open(json_path, 'r') as f:
        data = json.load(f)
        
    draw = ImageDraw.Draw(img)
    for item in data:
        box = item['box']
        pts = [(p[0], p[1]) for p in box]
        draw.polygon(pts, outline='red', width=3)
        
    img.save(out_path)
    print(f"Saved {out_path}")

draw_boxes('/home/admin_/duhua/temp1.webp', '/home/admin_/duhua/frontend/src/mockOcrData.json', '/home/admin_/duhua/mock_overlay1.jpg')
draw_boxes('/home/admin_/duhua/temp.jpg', '/home/admin_/duhua/frontend/src/mockOcrData2.json', '/home/admin_/duhua/mock_overlay2.jpg')
