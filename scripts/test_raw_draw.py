from paddleocr import PaddleOCR
from PIL import Image, ImageDraw

def main():
    img_path = '/home/admin_/duhua/temp1.webp'
    ocr = PaddleOCR(lang='ch', use_textline_orientation=True, enable_mkldnn=False, text_det_limit_side_len=3000)
    result = ocr.ocr(img_path)
    res0 = result[0]
    
    texts = res0.get('rec_texts', []) if hasattr(res0, 'get') else getattr(res0, 'rec_texts', getattr(res0, 'dt_polys', []))
    polys = res0.get('rec_polys', res0.get('dt_polys', [])) if hasattr(res0, 'get') else getattr(res0, 'rec_polys', getattr(res0, 'dt_polys', []))
    
    if not texts and isinstance(res0, list):
        # Legacy list format
        polys = [line[0] for line in res0]
        texts = [line[1][0] for line in res0]
        
    img = Image.open(img_path)
    draw = ImageDraw.Draw(img)
    
    for poly, text in zip(polys, texts):
        pts = [(p[0], p[1]) for p in poly]
        draw.polygon(pts, outline='red', width=3)
        
    out_path = '/home/admin_/duhua/transform_test/raw_paddleocr_output.jpg'
    img.save(out_path)
    print(f"Saved {out_path}")

if __name__ == '__main__':
    main()
