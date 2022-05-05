Handwritten math generator 

## Update in the code 
- To convert the MathML strings to SLT (symbol layout tree), the url is changed from http://mathbrush.cs.uwaterloo.ca:3000/convert_to_slt to http://mathbrush.cs.uwaterloo.ca:80/convert_to_slt
- In the original code, if the input is LaTeX string, math2tree.py converts the LaTeX string to MathML using https://latexml.mathweb.org/convert. All the ns0 prefix in the xml output is removed. 
- Add symbols that are don't have handwritten data in the CROHME isolated training dataset in the Missing_symbol.txt

--------------------------------------
### tsv_parser
- the input is a path to the tsv file with LaTeX strings 
- create a set of handwritten math expressions without bounding boxes

--------------------------------------
### Remove the bounding boxes and add handwritten symbols
The generator firstly constructs the layout of the input expressions, put available handwritten symbols from the dataset and apply distortions. There are only available 101 symbols in the CROHME dataset. If there is no handwritten symbol in the training dataset, the generator will give a warning and place an empty bounding box in the output. 


<img width="600" alt="Screen Shot 2022-05-04 at 3 18 45 PM" src="https://user-images.githubusercontent.com/59985531/166809815-6fd6ffea-fc28-483b-9caa-ebf08fec3139.png">
<img width="600" alt="Screen Shot 2022-05-04 at 3 17 26 PM" src="https://user-images.githubusercontent.com/59985531/166809821-ce8dd2a9-0c2a-4d51-84b6-4be0120e6a95.png">
<img width="600" alt="Screen Shot 2022-05-04 at 3 17 12 PM" src="https://user-images.githubusercontent.com/59985531/166809822-bdeb7288-1361-4153-b8cc-21613ccdbdc6.png">

To add handwritten symbols as ground truth, we need to update the training dataset and create a new gtdict.json file. 

1. Using [MathBrush](http://mathbrush.cs.uwaterloo.ca), write the expression which is to be tested.
2. Click the download button, second from the bottom on the left.
3. Convert the downloaded JSON file to inkml file with json2inkml.py file. 
4. Open the InkML file and follow this template.
```
<ink xmlns="http://www.w3.org/2003/InkML">
<traceFormat>
<channel name="X" type="decimal"/>
<channel name="Y" type="decimal"/>
</traceFormat><annotation type="truth"></annotation>
<annotation type="UI">101_alfonso_0</annotation>
<trace id="16">
745 67, 742 69, 735 84, 731 105, 731 110, 731 114, 731 118, 731 123, 731 127, 731 131, 732 135, 733 139, 734 142, 735 146, 736 149, 737 152, 738 155, 739 158, 740 160, 741 162, 742 164, 743 165, 744 166, 745 167, 746 167
</trace>
<traceGroup>
	<traceGroup xml:id="0">
		<annotation type="truth"></annotation>
		<traceView traceDataRef="16"/>
	</traceGroup>
</traceGroup>
</ink>

```
5. Add the corresponding id and symbol in the iso_GT.txt file, for example, 101_alfonso_0. 


