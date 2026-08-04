from paddleocr import PaddleOCR
from PIL import Image, ImageDraw
import sys

def test(img_path, out_path):
    ocr = PaddleOCR(lang='ch', use_textline_orientation=True, enable_mkldnn=False)
    result = ocr.ocr(img_path)
    res0 = result[0]
    
    img = Image.open(img_path)
    draw = ImageDraw.Draw(img)
    
    texts = res0.get('rec_texts', []) if hasattr(res0, 'get') else getattr(res0, 'rec_texts', getattr(res0, 'dt_polys', []))
    polys = res0.get('rec_polys', res0.get('dt_polys', [])) if hasattr(res0, 'get') else getattr(res0, 'rec_polys', getattr(res0, 'dt_polys', []))
    
    if not texts and isinstance(res0, list):
        polys = [line[0] for line in res0]
        texts = [line[1][0] for line in res0]
        
    for poly, text in zip(polys, texts):
        pts = [(p[0], p[1]) for p in poly]
        draw.polygon(pts, outline='red', width=3)
        
    img.save(out_path)
    print(f"Saved {out_path}")

test('/home/admin_/duhua/temp1.webp', '/home/admin_/duhua/pure_test1.jpg')
test('/home/admin_/duhua/temp.jpg', '/home/admin_/duhua/pure_test2.jpg')
