import httpx
import tempfile
import os
import re
import logging
from typing import List, Dict, Any, Optional
from PIL import Image
from paddleocr import PaddleOCR
from pydantic import BaseModel
from app.tools.dictionary_tool import lookup_vocab, DictionaryMatch

class OcrResult(BaseModel):
    box: List[List[float]]
    text: str
    confidence: float
    is_chinese: bool
    dictionary: Optional[DictionaryMatch] = None

class OcrError(BaseModel):
    error: str


# Configure logging to hide noisy PaddleOCR logs
logging.getLogger('ppocr').setLevel(logging.ERROR)

# Initialize OCR model once (cache it)
_ocr_instance = None

def get_ocr_instance():
    global _ocr_instance
    if _ocr_instance is None:
        _ocr_instance = PaddleOCR(
            lang='ch',
            use_textline_orientation=True,
            enable_mkldnn=False,
            text_det_limit_side_len=3000,
            text_det_thresh=0.15,
            text_det_box_thresh=0.3,
            text_det_unclip_ratio=1.2,
            use_doc_orientation_classify=False,
            use_doc_unwarping=False
        )
    return _ocr_instance

def contains_chinese(text: str) -> bool:
    """Returns True if string contains at least one CJK Unified Ideograph."""
    return bool(re.search(r'[\u4e00-\u9fa5]', text))


def transform_point_back(pt: List[float], angle: int, img_w: float, img_h: float) -> List[float]:
    x, y = float(pt[0]), float(pt[1])
    if angle == 180:
        return [img_w - x, img_h - y]
    elif angle == 90:
        return [img_w - y, x]
    elif angle == 270:
        return [y, img_h - x]
    else:
        return [x, y]

def run_ocr(image_url: str) -> List[OcrResult | OcrError]:
    """Downloads an image from a URL and runs OCR to extract Chinese text, bounding boxes, and pre-calculated dictionary definitions.
    
    Args:
        image_url: The URL of the image to process.
        
    Returns:
        A list of OcrResult objects. On failure, returns a list containing a single OcrError object.
    """
    try:
        response = httpx.get(image_url, timeout=15.0)
        response.raise_for_status()
    except Exception as e:
        return [OcrError(error=f"Failed to download image: {str(e)}. Please tell the user to try again or check the image format.")]
        
    try:
        pil_img = Image.open(__import__('io').BytesIO(response.content)).convert('RGB')
        img_width, img_height = pil_img.size
    except Exception as e:
        return [OcrError(error=f"Failed to find image size: {str(e)}. Please tell the user to try again or check the image format.")]

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        if 'pil_img' in locals():
            pil_img.save(tmp.name, format="JPEG")
        else:
            tmp.write(response.content)
        tmp_path = tmp.name
        
    try:
        ocr = get_ocr_instance()
        result = ocr.ocr(tmp_path)
        
        extracted = []
        if not result:
            return extracted
            
        res0 = result[0]
        
        # Determine orientation angle if doc_preprocessor ran
        angle = 0
        if isinstance(res0, dict):
            doc_res = res0.get('doc_preprocessor_res')
            if isinstance(doc_res, dict):
                angle = doc_res.get('angle', 0)
        
        # 1. PaddleOCR 3.x / PaddleX dictionary output
        if isinstance(res0, dict) or hasattr(res0, 'get') or hasattr(res0, 'rec_texts'):
            texts = res0.get('rec_texts', []) if hasattr(res0, 'get') else getattr(res0, 'rec_texts', [])
            scores = res0.get('rec_scores', []) if hasattr(res0, 'get') else getattr(res0, 'rec_scores', [])
            polys = res0.get('rec_polys', res0.get('dt_polys', [])) if hasattr(res0, 'get') else getattr(res0, 'rec_polys', getattr(res0, 'dt_polys', []))
            
            for i in range(min(len(texts), len(polys))):
                box = polys[i]
                if hasattr(box, 'tolist'):
                    box = box.tolist()
                
                text_str = str(texts[i]).strip()
                if not text_str:
                    continue
                
                cartesian_box = [transform_point_back(pt, angle, img_width, img_height) for pt in box]
                
                is_ch = contains_chinese(text_str)
                dict_def = lookup_vocab(text_str) if is_ch else None
                if dict_def and hasattr(dict_def, "error"):
                    dict_def = None

                extracted.append(OcrResult(
                    box=cartesian_box,
                    text=text_str,
                    confidence=float(scores[i]) if i < len(scores) else 1.0,
                    is_chinese=is_ch,
                    dictionary=dict_def
                ))
        # 2. Legacy PaddleOCR 2.x list output
        elif isinstance(res0, (list, tuple)):
            for line in res0:
                if isinstance(line, (list, tuple)) and len(line) >= 2:
                    box = line[0]
                    if hasattr(box, 'tolist'):
                        box = box.tolist()
                    cartesian_box = [transform_point_back(pt, angle, img_width, img_height) for pt in box]
                    text_data = line[1]
                    if isinstance(text_data, (list, tuple)):
                        text_str = str(text_data[0]).strip()
                        confidence = float(text_data[1]) if len(text_data) > 1 else 1.0
                    else:
                        text_str = str(text_data).strip()
                        confidence = 1.0
                    if not text_str:
                        continue
                    is_ch = contains_chinese(text_str)
                    dict_def = lookup_vocab(text_str) if is_ch else None
                    if dict_def and hasattr(dict_def, "error"):
                        dict_def = None

                    extracted.append(OcrResult(
                        box=cartesian_box,
                        text=text_str,
                        confidence=confidence,
                        is_chinese=is_ch,
                        dictionary=dict_def
                    ))
        return extracted
    except Exception as e:
        import traceback
        traceback.print_exc()
        return [OcrError(error=f"OCR processing failed: {str(e)}. Please tell the user to try again or check the image format.")]
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
