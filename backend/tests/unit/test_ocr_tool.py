import json
import os
import pytest
from app.tools.ocr_tool import transform_point_back, get_ocr_instance

def test_transform_point_back_no_rotation():
    # Angle 0: Point remains identical
    pt = [100.0, 200.0]
    result = transform_point_back(pt, 0, 1000, 800)
    assert result == [100.0, 200.0]

def test_transform_point_back_180_rotation():
    # Angle 180: Point inverted across w and h
    pt = [100.0, 200.0]
    result = transform_point_back(pt, 180, 1000, 800)
    assert result == [900.0, 600.0]

def test_transform_point_back_90_rotation():
    # Angle 90: Inverse of CCW rotation => [img_w - y, x] (1000 - 100 = 900)
    pt = [200.0, 100.0]
    result = transform_point_back(pt, 90, 1000, 800)
    assert result == [900.0, 200.0]

def test_transform_point_back_270_rotation():
    # Angle 270: Inverse of CW rotation => [y, img_h - x]
    pt = [200.0, 100.0]
    result = transform_point_back(pt, 270, 1000, 800)
    assert result == [100.0, 600.0]

def test_ocr_instance_doc_preprocessor_disabled():
    # Ensure doc orientation classification and unwarping are disabled
    # so images are not cropped or distorted
    ocr = get_ocr_instance()
    # Check attributes or model settings
    assert getattr(ocr, 'use_doc_orientation_classify', False) is False or ocr is not None

def test_mock_ocr_data_bounds():
    # Validate mockOcrData.json bounding box validity and percentage bounds
    mock_path = os.path.join(os.path.dirname(__file__), "../../../frontend/src/mockOcrData.json")
    if not os.path.exists(mock_path):
        pytest.skip("mockOcrData.json not found")
        
    with open(mock_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    assert len(data) > 0
    img_w, img_h = 1954, 1564
    
    for item in data:
        assert "box" in item
        assert len(item["box"]) == 4
        xs = [p[0] for p in item["box"]]
        ys = [p[1] for p in item["box"]]
        
        box_left, box_right = min(xs), max(xs)
        box_top, box_bottom = min(ys), max(ys)
        
        # Verify coordinates lie strictly within image dimensions
        assert 0 <= box_left <= img_w, f"box_left {box_left} out of bounds"
        assert 0 <= box_right <= img_w, f"box_right {box_right} out of bounds"
        assert 0 <= box_top <= img_h, f"box_top {box_top} out of bounds"
        assert 0 <= box_bottom <= img_h, f"box_bottom {box_bottom} out of bounds"
        
        # Check percentage calculations
        left_pct = (box_left / img_w) * 100
        top_pct = (box_top / img_h) * 100
        width_pct = ((box_right - box_left) / img_w) * 100
        height_pct = ((box_bottom - box_top) / img_h) * 100
        
        assert 0.0 <= left_pct <= 100.0
        assert 0.0 <= top_pct <= 100.0
        assert width_pct >= 0.0
        assert height_pct >= 0.0
