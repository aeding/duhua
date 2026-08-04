import pytest
from app.tools.ocr_tool import run_ocr

def test_ocr_tool_integration():
    test_image_url = "https://cdn.hanzihero.com/images/blog/one-piece-chapter-1-2febd5f01ab64a5629a86358c2ca9934.webp"
    results = run_ocr(test_image_url)
    
    assert isinstance(results, list)
    assert len(results) > 0
    assert "error" not in results[0]
    
    # Check structure of first item
    first_item = results[0]
    assert "box" in first_item
    assert "text" in first_item
    assert "confidence" in first_item
    assert len(first_item["box"]) == 4
