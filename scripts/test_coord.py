from paddleocr import PaddleOCR
from PIL import Image
ocr = PaddleOCR(lang='ch', use_textline_orientation=True, enable_mkldnn=False)
result = ocr.ocr('/home/admin_/duhua/temp1.webp')
res0 = result[0]
texts = res0.get('rec_texts', []) if hasattr(res0, 'get') else getattr(res0, 'rec_texts', [])
polys = res0.get('rec_polys', res0.get('dt_polys', [])) if hasattr(res0, 'get') else getattr(res0, 'rec_polys', getattr(res0, 'dt_polys', []))
for i in range(3):
    print(f"Original from PaddleOCR: {texts[i]} -> {polys[i]}")
