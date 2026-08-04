import os
import json
from typing import List, Dict, Any, Optional

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

def manage_vocab(action: str, word_data: Optional[Dict[str, Any]] = None) -> Any:
    """Manages the user's saved vocabulary. Use this to save words for flashcards or retrieve them to generate quizzes.
    
    Args:
        action: The action to perform. Can be "add", "list", or "clear".
        word_data: If action is "add", this should be a dictionary containing at minimum a "word" key and optionally "pinyin" and "english".
        
    Returns:
        The result of the operation. For "list", returns the list of saved words.
    """
    vocab = _load_vocab()
    
    if action == "add":
        if not word_data or "word" not in word_data:
            return {"error": "Missing 'word' in word_data"}
        
        # Avoid duplicates
        for entry in vocab:
            if entry["word"] == word_data["word"]:
                return {"status": "already_exists"}
                
        vocab.append(word_data)
        _save_vocab(vocab)
        return {"status": "success", "word": word_data["word"]}
        
    elif action == "list":
        return vocab
        
    elif action == "clear":
        _save_vocab([])
        return {"status": "cleared"}
        
    else:
        return {"error": f"Unknown action: {action}"}
