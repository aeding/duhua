import os
import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class VocabWord(BaseModel):
    word: str
    pinyin: Optional[str] = None
    english: Optional[str] = None

class VocabResponse(BaseModel):
    status: str
    word: Optional[str] = None
    vocab_list: Optional[List[VocabWord]] = None
    error: Optional[str] = None


VOCAB_DB_FILE = os.path.join(os.path.dirname(__file__), "data", "vocab.json")

def _load_vocab() -> List[Dict[str, Any]]:
    if os.path.exists(VOCAB_DB_FILE):
        with open(VOCAB_DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def _save_vocab(vocab: List[Dict[str, Any]]):
    os.makedirs(os.path.dirname(VOCAB_DB_FILE), exist_ok=True)
    with open(VOCAB_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(vocab, f, ensure_ascii=False, indent=2)

def manage_vocab(action: str, word_data: Optional[VocabWord] = None) -> VocabResponse:
    """Manages the user's saved vocabulary. Use this to save words for flashcards or retrieve them to generate quizzes.
    
    Args:
        action: The action to perform. Can be "add", "list", or "clear".
        word_data: If action is "add", this should be a VocabWord containing at minimum a "word" key.
        
    Returns:
        VocabResponse indicating the result.
    """
    vocab = _load_vocab()
    
    if action == "add":
        if not word_data or not word_data.word:
            return VocabResponse(status="error", error="Missing 'word' in word_data. Please provide the word you want to add.")
        
        # Avoid duplicates
        for entry in vocab:
            if entry["word"] == word_data.word:
                return VocabResponse(status="already_exists", word=word_data.word)
                
        vocab.append(word_data.model_dump(exclude_none=True))
        _save_vocab(vocab)
        return VocabResponse(status="success", word=word_data.word)
        
    elif action == "list":
        vocab_list = [VocabWord(**item) for item in vocab]
        return VocabResponse(status="success", vocab_list=vocab_list)
        
    elif action == "clear":
        _save_vocab([])
        return VocabResponse(status="cleared")
        
    else:
        return VocabResponse(status="error", error=f"Unknown action: {action}. Please use 'add', 'list', or 'clear'.")
