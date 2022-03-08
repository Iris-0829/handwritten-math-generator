import math2tree as m2t
import argparse
import sys
import logging
from utils.np2inkml import to_inkml

def generate(markup_input, input_type = 'file', markup_language = 'latex'):
    '''
    Generates stroke data for a given latex or mathml input
    
    Parameters
    ----------
    markup_input: str
        Latex or MathML string, or file path to text file
    input_type: str
        Defines whether markup_input is a string or a file path.
        Default to 'file'
    markup_language: str
        Defines whether markup_input is Latex or MathML
        Either 'latex' or 'mathml'
        
    returns: list of numpy arrays
    '''
    
    logging.basicConfig(filename='log.log', level=logging.INFO)
    logging.info(markup_input)
    
    if input_type == 'file':
        with open(markup_input, 'r') as file:
            math_str = file.read()
    else:
        math_str = markup_input
        
    slt_root, mml_str = m2t.get_tree_root(math_str, markup_language = markup_language)
    slt_root.get_traces()
    slt_root.absorb()
    slt_root.scale_traces_v(-1)
    
    output = slt_root.traces
    
    trace_groups = slt_root.num_traces
    bounding_boxes = slt_root.bounding_box
    
    return output, math_str, trace_groups, bounding_boxes

def generate_inkml(markup_input, output, input_type = 'file', markup_language = 'latex'):
    '''
    Generates stroke data for a given latex or mathml input
    
    Parameters
    ----------
    markup_input: str
        Latex or MathML string, or file path to text file
    output: str
        File path for inkml output
    input_type: str
        Defines whether markup_input is a string or a file path.
        Default to 'file'
    markup_language: str
        Defines whether markup_input is Latex or MathML
        Either 'latex' or 'mathml'
        
    returns: None
        Creates inkml file
    '''
    
    np_arrays, math_str, trace_groups, bounding_boxes = generate(markup_input, input_type = input_type, markup_language = markup_language)
    to_inkml(np_arrays, math_str, trace_groups, bounding_boxes, output)


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Generate inkml file of given math expression')
    parser.add_argument("input", help="File path or string of markup language input", type=str)
    parser.add_argument("output", help="Output inkml file path", type=str)
    parser.add_argument("-t", "--input_type", help="file or string", type=str, default='file')
    parser.add_argument("-l", "--markup_language", help="latex or mathml", type=str, default='latex')
    
    args = vars(parser.parse_args())
    if args['input_type'] not in ['file', 'string']:
        print('Input type must be "file" or "string"')
    elif args['markup_language'] not in ['latex', 'mathml']:
        print('Markup Language must be "latex" or "mathml"')
    else:
        generate_inkml(args['input'], args['output'], input_type = args['input_type'], markup_language = args['markup_language'])
