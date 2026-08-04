from paddleocr import PaddleOCR

def print_coords(img_path):
    ocr = PaddleOCR(lang='ch', use_textline_orientation=True, enable_mkldnn=False)
    result = ocr.ocr(img_path)
    res0 = result[0]
    
    texts = res0.get('rec_texts', []) if hasattr(res0, 'get') else getattr(res0, 'rec_texts', getattr(res0, 'dt_polys', []))
    polys = res0.get('rec_polys', res0.get('dt_polys', [])) if hasattr(res0, 'get') else getattr(res0, 'rec_polys', getattr(res0, 'dt_polys', []))
    
    if not texts and isinstance(res0, list):
        polys = [line[0] for line in res0]
        texts = [line[1][0] for line in res0]
        
    print(f"--- {img_path} ---")
    for i in range(min(5, len(texts))):
        print(f"Text: {texts[i]}")
        print(f"Box: {[[int(p[0]), int(p[1])] for p in polys[i]]}")

print_coords('/home/admin_/duhua/temp1.webp')
print_coords('/home/admin_/duhua/temp.jpg')
