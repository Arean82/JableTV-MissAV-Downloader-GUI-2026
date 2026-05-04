#!/usr/bin/env python
# coding: utf-8
"""Refactored translation manager that loads locales from JSON files."""

import os
import json

# Local storage for loaded strings
_STRINGS = {}
_current_lang = 'zh'

def set_lang(lang: str):
    global _current_lang, _STRINGS
    _current_lang = lang
    
    # Lazy load the language file if not already in memory
    if lang not in _STRINGS:
        # Resolve path relative to this file
        base_path = os.path.dirname(__file__)
        file_path = os.path.join(base_path, 'locales', f'{lang}.json')
        
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    _STRINGS[lang] = json.load(f)
            except Exception as e:
                print(f"[Locales] Error loading {lang}.json: {e}")
                _STRINGS[lang] = {}
        else:
            print(f"[Locales] Locale file not found: {file_path}")
            _STRINGS[lang] = {}

def T(key: str, **kwargs) -> str:
    """Translate a key to the current language."""
    # Ensure current language is loaded
    if _current_lang not in _STRINGS:
        set_lang(_current_lang)
        
    # Fallback chain: Requested Lang -> zh -> key itself
    lang_dict = _STRINGS.get(_current_lang, {})
    s = lang_dict.get(key)
    
    if s is None:
        # Try fallback to zh if current isn't zh
        if _current_lang != 'zh':
            if 'zh' not in _STRINGS:
                set_lang('zh')
            s = _STRINGS.get('zh', {}).get(key, key)
        else:
            s = key
            
    if kwargs:
        try:
            return s.format(**kwargs)
        except Exception:
            return s
    return s

def get_lang() -> str:
    return _current_lang

# Default initialization
set_lang('zh')
