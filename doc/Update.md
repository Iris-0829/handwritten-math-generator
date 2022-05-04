Handwritten math generator 

## Update in the code 
- To convert the MathML strings to SLT (symbol layout tree), the url is changed from http://mathbrush.cs.uwaterloo.ca:3000/convert_to_slt to http://mathbrush.cs.uwaterloo.ca:80/convert_to_slt
- In the original code, if the input is LaTeX string, math2tree.py converts the LaTeX string to MathML using https://latexml.mathweb.org/convert. All the ns0 prefix in the xml output is removed. 

--------------------------------------
tsv_parser
- The input is a path to the tsv file with LaTeX strings 
- create a set of handwritten math expressions without bounding boxes



