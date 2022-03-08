import xml.etree.ElementTree as ET
import json

def unicode_to_char_name(font_cmap):
    tree = ET.parse(font_cmap)
    root = tree.getroot()
    cmap = root[0][2]
    
    unicode_to_char = {}
    
    for char in cmap:
        unicode_to_char[char.get('code')] = char.get('name')
    
    return unicode_to_char

char_map = unicode_to_char_name('Asana-cmap.ttx')

to_json = json.dumps(char_map)
f = open('./cmap.json', 'w')
f.write(to_json)
f.close()
