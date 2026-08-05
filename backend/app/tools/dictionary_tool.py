import os
import zipfile
import threading
import httpx
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class DictionaryDefinition(BaseModel):
    traditional: str
    simplified: str
    pinyin: str
    english: str

class DictionaryMatch(BaseModel):
    word: str
    definitions: List[DictionaryDefinition]

class LookupError(BaseModel):
    error: str


DICT_URL = "https://www.mdbg.net/chinese/export/cedict/cedict_1_0_ts_utf-8_mdbg.zip"
DICT_DIR = os.path.join(os.path.dirname(__file__), "data")
DICT_FILE = os.path.join(DICT_DIR, "cedict_ts.u8")

class TrieNode:
    def __init__(self):
        self.children = {}
        self.definitions = []

class DictionaryTrie:
    def __init__(self):
        self.root = TrieNode()
        
    def insert(self, word: str, definition: dict):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.definitions.append(definition)
        
    def longest_match(self, text: str) -> Optional[Dict[str, Any]]:
        node = self.root
        last_match = None
        match_len = 0
        
        for i, char in enumerate(text):
            if char in node.children:
                node = node.children[char]
                if node.definitions:
                    last_match = node.definitions
                    match_len = i + 1
            else:
                break
                
        if last_match:
            return {"word": text[:match_len], "definitions": last_match}
        return None

_trie = None
_lock = threading.Lock()

def load_dictionary():
    global _trie
    if _trie is not None:
        return
        
    with _lock:
        if _trie is not None:
            return
            
        os.makedirs(DICT_DIR, exist_ok=True)
        if not os.path.exists(DICT_FILE):
            print("Downloading CC-CEDICT dictionary...")
            zip_path = os.path.join(DICT_DIR, "cedict.zip")
            try:
                with httpx.Client(timeout=60.0) as client:
                    resp = client.get(DICT_URL, follow_redirects=True)
                    with open(zip_path, "wb") as f:
                        f.write(resp.content)
                
                with zipfile.ZipFile(zip_path, "r") as z:
                    z.extractall(DICT_DIR)
            finally:
                if os.path.exists(zip_path):
                    os.remove(zip_path)
            print("CC-CEDICT downloaded and extracted.")
            
        trie_instance = DictionaryTrie()
        with open(DICT_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("#"):
                    continue
                parts = line.split(" /")
                if len(parts) < 2: continue
                
                vocab_part = parts[0]
                defs = "/".join(parts[1:]).strip().strip("/")
                
                # format: Trad Simp [pinyin]
                vocab_split = vocab_part.split(" [")
                if len(vocab_split) < 2: continue
                
                words = vocab_split[0].split()
                trad = words[0]
                simp = words[1] if len(words) > 1 else trad
                pinyin = vocab_split[1].rstrip("]")
                
                entry = {"traditional": trad, "simplified": simp, "pinyin": pinyin, "english": defs}
                trie_instance.insert(simp, entry)
                trie_instance.insert(trad, entry)
        _trie = trie_instance
        print("CC-CEDICT Trie dictionary loaded into memory.")

def lookup_vocab(text: str) -> DictionaryMatch | LookupError:
    """Looks up the longest matching Chinese word at the start of the given text.
    
    Args:
        text: A string starting with a Chinese character.
        
    Returns:
        DictionaryMatch on success, LookupError on failure.
    """
    load_dictionary()
    match = _trie.longest_match(text)
    if match:
        defs = [DictionaryDefinition(**d) for d in match["definitions"]]
        return DictionaryMatch(word=match["word"], definitions=defs)
    return LookupError(error=f"No dictionary match found for text: '{text}'. Please try a different word or explain to the user that it might be a name or unlisted compound.")
