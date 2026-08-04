from paddleocr import PaddleOCR

def print_info(img_path):
    ocr = PaddleOCR(lang='ch', use_textline_orientation=True, enable_mkldnn=False)
    result = ocr.ocr(img_path)
    res0 = result[0]
    print(f"--- {img_path} ---")
    if isinstance(res0, dict):
        print(f"img_info: {res0.get('img_info')}")
        print(f"doc_preprocessor_res: {res0.get('doc_preprocessor_res')}")
    else:
        print("res0 is list")

print_info('/home/admin_/duhua/temp1.webp')
print_info('/home/admin_/duhua/temp.jpg')
