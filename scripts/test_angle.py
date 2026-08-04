from PIL import Image
from paddleocr import PaddleOCR

ocr = PaddleOCR(lang='ch', use_textline_orientation=True, enable_mkldnn=False)
result = ocr.ocr('/home/admin_/duhua/temp1.webp')
res0 = result[0]

angle = 0
if isinstance(res0, dict):
    doc_res = res0.get('doc_preprocessor_res')
    if isinstance(doc_res, dict):
        angle = doc_res.get('angle', 0)

print(f"Detected Angle: {angle}")
print(f"First box: {res0.get('rec_texts', [])[0] if isinstance(res0, dict) else res0[0]}")
