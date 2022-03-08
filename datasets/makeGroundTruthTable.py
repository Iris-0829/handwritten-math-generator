import csv
import json

def make_gt_table(folder, filename):
    ground_truth_file = open('./'+ folder + '/' + filename)
    groud_truth_file_reader = csv.reader(ground_truth_file)
    gtdict = {}
    unicode_to_glyf, symbol_to_glyf, latex_to_unicode, mathlatex_to_unicode = load_tables()
    i = 0
    for row in groud_truth_file_reader:
        symbol = row[1]
        if symbol in latex_to_unicode:
            symbol = latex_to_unicode[symbol]
            symbol = unicode_to_glyf[symbol]
        elif symbol in mathlatex_to_unicode:
            symbol = mathlatex_to_unicode[symbol]
            symbol = unicode_to_glyf[symbol]
        elif symbol in symbol_to_glyf:
            symbol = symbol_to_glyf[symbol]
        else:
            print(symbol + ' not found in tables')
            symbol = 'notintables'
    
        if symbol in gtdict:
            gtdict[symbol].append(i)
        else:
            gtdict[symbol] = [i]
    
        i += 1
    to_json = json.dumps(gtdict)
    f = open('./'+ folder +'/gtdict.json', 'w')
    f.write(to_json)
    f.close()


def load_tables():
    
    cmap_file = open('../Font/cmap.json')
    symbol_to_glyf_file = open('../Font/symb_to_glyf.json')
    latex_file = open('../Font/latextounicode.json')
    mathlatex_file = open('../Font/mathlatextounicode.json')
    
    unicode_to_glyf = json.load(cmap_file)
    symbol_to_glyf = json.load(symbol_to_glyf_file)
    latex_to_unicode = json.load(latex_file)
    mathlatex_to_unicode = json.load(mathlatex_file)
    
    cmap_file.close()
    symbol_to_glyf_file.close()
    latex_file.close()
    mathlatex_file.close()
    return unicode_to_glyf, symbol_to_glyf, latex_to_unicode, mathlatex_to_unicode
    
    