import xml.etree.ElementTree as ET
import json

def get_latex(character):
    '''
    Returns latex and mathlatex strings
    '''
    latex = None
    mathlatex = None
    
    
    for data in character:
        if data.tag == 'latex' and latex is None:
            latex = data.text.strip()
        
        if data.tag == 'mathlatex' and mathlatex is None:
            mathlatex = data.text.strip()
              
    return latex, mathlatex

def latex_to_unicode_dict():
    '''
    Creates 2 dictionaries, mapping latex and mathlatex to unicode
    '''
    
    # Get unicode character lsit
    filename = './unicode.xml'
    tree = ET.parse(filename)
    root = tree.getroot()
    charlist = root[4]
    
    # initialize dictionaries
    latex_to_unicode = {}
    mathlatex_to_unicode = {}
    
    #iterate through characters
    for character in charlist:
        character_id = character.get('id')
        character_id = character_id.lstrip('U0')
        character_id = '0x' + character_id.lower()
        
        latex, mathlatex = get_latex(character)
        
        if latex is not None and latex not in latex_to_unicode:
            latex_to_unicode[latex] = character_id
        if mathlatex is not None and mathlatex not in mathlatex_to_unicode:
            mathlatex_to_unicode[mathlatex] = character_id
    
    return latex_to_unicode, mathlatex_to_unicode


latex_to_unicode, mathlatex_to_unicode = latex_to_unicode_dict()

latex_to_json = json.dumps(latex_to_unicode)
f = open('./latex2unicode.json', 'w')
f.write(latex_to_json)
f.close()

mathlatex_to_json = json.dumps(mathlatex_to_unicode)
f = open('./mathlatex2unicode.json', 'w')
f.write(mathlatex_to_json)
f.close()