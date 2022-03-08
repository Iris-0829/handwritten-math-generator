import json
import logging
from unicodedata import normalize

def get_tables():
    
    cmap_file = open('./Font/cmap.json')
    symbol_to_glyf_file = open('./Font/symb_to_glyf.json')
    invis_unicode_file = open('./Font/invisibleunicode.json')
    
    unicode_to_glyf = json.load(cmap_file)
    symbol_to_glyf = json.load(symbol_to_glyf_file)
    invis_unicode = json.load(invis_unicode_file)
    
    
    cmap_file.close()
    symbol_to_glyf_file.close()
    invis_unicode_file.close()
    return unicode_to_glyf, symbol_to_glyf, invis_unicode

def get_glyf_name(s):
    
    unicode_to_glyf, symbol_to_glyf, invis_unicode = get_tables()
    
    if len(s) == 1:
        
        ns = normalize('NFKC', s)
        
        if len(ns) == 1:
            s = ns
        
        unicode = hex(ord(s.strip())).lower()
        
        if unicode in unicode_to_glyf:
            glyf_name = unicode_to_glyf[unicode]
            
            return glyf_name
        elif unicode in invis_unicode:
            return "invis"
        else:
            log_str = "No glyf for unicode " + unicode
            logging.warning(log_str)
            print(log_str)
            return s
            
    else:
        
        if s == 'frac':
            return s
        elif s in symbol_to_glyf:
            glyf_name = symbol_to_glyf[s]
            return glyf_name
        elif isfloat(s):
            return s
        elif s[0:6] == "Matrix" or s[0:4] == "Text":
            return s
        else:
            log_str = "Interpreting " + s + " as text"
            logging.info(log_str)
            print(log_str)
            return 'Text|_|' + s

def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False
