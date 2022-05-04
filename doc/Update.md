Handwritten math generator 

## Update in the code 
- To convert the MathML strings to SLT (symbol layout tree), the url is changed from http://mathbrush.cs.uwaterloo.ca:3000/convert_to_slt to http://mathbrush.cs.uwaterloo.ca:80/convert_to_slt
- In the original code, if the input is LaTeX string, math2tree.py converts the LaTeX string to MathML using https://latexml.mathweb.org/convert. All the ns0 prefix in the xml output is removed. 

--------------------------------------
### tsv_parser
- The input is a path to the tsv file with LaTeX strings 
- create a set of handwritten math expressions without bounding boxes

--------------------------------------
### Remove the bounding boxes and add handwritten symbols
There are only available 101 symbols in the CROHME dataset. If there is no handwritten symbol in the training dataset, the generator will give a warning and place an empty bounding box in the output. 


<img width="600" alt="Screen Shot 2022-05-04 at 3 18 45 PM" src="https://user-images.githubusercontent.com/59985531/166809815-6fd6ffea-fc28-483b-9caa-ebf08fec3139.png">
<img width="600" alt="Screen Shot 2022-05-04 at 3 17 26 PM" src="https://user-images.githubusercontent.com/59985531/166809821-ce8dd2a9-0c2a-4d51-84b6-4be0120e6a95.png">
<img width="600" alt="Screen Shot 2022-05-04 at 3 17 12 PM" src="https://user-images.githubusercontent.com/59985531/166809822-bdeb7288-1361-4153-b8cc-21613ccdbdc6.png">





