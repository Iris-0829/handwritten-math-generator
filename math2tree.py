import re
import requests
import ExpressionClass as EC
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import tostring, fromstring
import json
import logging
from utils.get_glyf_info import get_glyf_name, isfloat

def math_to_edges(math_str, markup_language = 'latex'):
    '''
    Convert latex text file to list of slt edges
    '''
    
    if markup_language == 'latex':
        
        mml_str = latex2mathml(math_str)
    else:
        mml_str = math_str
        
    headers = {'Content-Type': 'text/plain; charset=UTF-8'}
    convert2slt = 'http://mathbrush.cs.uwaterloo.ca:3000/convert_to_slt'
    
    req = requests.post(convert2slt, data = mml_str.encode('utf-8'), headers = headers)
    
    slt = req.json()
    if slt == ['(W!,!0)', '(W!,!0,)']:
        with open('SLTErrors.txt', mode='a') as SLTfile:
            SLTfile.write('\n' + mml_str + '\n')
            
    edge_list = trim_slt_list(slt)
    
    for i in range(len(edge_list)):
        edge_list[i] = parse_edge(edge_list[i])
    edge_list.sort(key = lambda x : len(x[3]))
    return edge_list, mml_str

def trim_slt_list(slt_list):
    
    target_idx = 0
    for i in range(len(slt_list)):
        num_commas = slt_list[i].count(',')
        if num_commas == 2:
            target_idx = i
            
    trimmed_slt_list = slt_list[target_idx + 1 :]
    stripped_slt_list = list(map(lambda x: x.strip('()'), trimmed_slt_list))
    edge_list = list(map(lambda x: x.split(','), stripped_slt_list))
    
    return edge_list

def parse_edge(edge):
    parent = edge[0]
    child = edge[1]
    relation = edge[2]
    path_from_root = edge[3]
    
    if any(map(str.isdigit, path_from_root)):
        compressed_list = re.split('(\d+)',path_from_root)[1:]
        decompressed = ''
        for i in range(0, len(compressed_list), 2):
            number = int(compressed_list[i])
            rel = compressed_list[i + 1]
            decompressed = decompressed + (number * rel)
            
        path_from_root = decompressed
    
    if '!' in parent:
        if parent[0] == 'f' or parent[0] == 'F':
            parent = 'frac'
        elif parent[0] == 'r' or parent[0] == 'R':
            parent = 'radical'
        elif parent[0] == 'M' or parent[0] == 'm':
            parent = 'Matrix' + '|_|' + parent[parent.index('!') + 1 : -3] + '|_|' + parent[-3:]
        elif parent[0] == 'T' or parent[0] == 't':
            parent = 'Text' + '|_|' + parent[parent.index('!') + 1 :]
        else:
            parent = parent[parent.index('!') + 1 :]
            
    if '!' in child:
        if child[0] == 'f' or child[0] == 'F':
            child = 'frac'
        elif child[0] == 'r' or child[0] == 'R':
            child = 'radical'
        elif child[0] == 'M' or child[0] == 'm':
            child = 'Matrix' + '|_|' + child[child.index('!') + 1 : -3] + '|_|' + child[-3:]
        elif child[0] == 'T' or child[0] == 't':
            child = 'Text' + '|_|' + child[child.index('!') + 1 :]
        else:
            child = child[child.index('!') + 1:]
            
    return parent, child, relation, path_from_root

def edge_list_to_expression_tree(edge_list):
    root = None
    for edge in edge_list:
        
        parent = get_glyf_name(edge[0])
        
        child = get_glyf_name(edge[1])
        
        edge_type = edge[2]
        rel_to_root = edge[3]
        if root is None and rel_to_root =='':
            root = EC.Expression(parent)

        current_parent = root
        
        for rel in rel_to_root:
                
            if rel == 'n':
                current_parent = current_parent.next
            elif rel == 'a':
                current_parent = current_parent.above
            elif rel == 'b':
                current_parent = current_parent.below
            elif rel == 'o':
                current_parent = current_parent.over
            elif rel == 'u':
                current_parent = current_parent.under
            elif rel == 'w':
                current_parent = current_parent.within
            elif rel == 'e':
                current_parent = current_parent.element
            elif rel =='c':
                current_parent = current_parent.radical_degree
            else:
                print("Unknown relation " + rel)
                return None
            
        if edge_type == 'n':
            current_parent.next = EC.Expression(child)
        elif edge_type == 'a':
            current_parent.above = EC.Expression(child)
        elif edge_type == 'b':
            current_parent.below = EC.Expression(child)
        elif edge_type == 'o':
            current_parent.over = EC.Expression(child)
        elif edge_type == 'u':
            current_parent.under = EC.Expression(child)
        elif edge_type == 'w':
            current_parent.within = EC.Expression(child)
        elif edge_type == 'e':
            current_parent.element = EC.Expression(child)
        elif edge_type == 'c':
            current_parent.radical_degree = EC.Expression(child)
        else:
            print("Unknown relation " + edge_type)
            return None
        
    return root

def get_tree_root(math_input, markup_language = 'latex'):
    '''
    returns root of input expression slt
    '''
    edge_list, mml_str = math_to_edges(math_input, markup_language = markup_language)
    tree_root = edge_list_to_expression_tree(edge_list)
    return tree_root, mml_str


def latex2mathml(latex_str):
    
    ET.register_namespace("", "http://www.w3.org/1998/Math/MathML")
    req = requests.post('https://latexml.mathweb.org/convert', data = {'tex': latex_str, 'profile':'fragment'})
    result = req.json()['result']
    start_math_idx = result.find('<math')
    end_math_idx = result.find('</math>')
    mathml_str = result[start_math_idx:end_math_idx + 7]
    
    tree = fromstring(mathml_str)
    
    ## Remove alttext from the math tag and annotation at the end since
    ## it can cause issues with the slt conversion
    del(tree.attrib['alttext'])

    annotation = tree[0][-1]
    tree[0].remove(annotation)

    mathml_string = tostring(tree, encoding = 'unicode')
    return mathml_string
