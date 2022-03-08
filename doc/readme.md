Handwritten Math Generator

Requirements:
- Python 3
pip installable packages:
- numpy
- fuzzywuzzy
- matplotlib
- requests

Data files required can be copied from /u/adm-penmath/BrushSearch/BrushSearchData/handwritten-math-generator/datasets/ 
on the scg server into the datasets folder.
Place the gtdict.json file in the unzipped directory.
------------------------------------------

Basic command line usage:

python generator.py [-t input_type] [-l markup_language] input output

input - text file path or string of math expression
Note: if passing in as a string, wrap the input with single quotes i.e.
'$a^{2} + b^{2}$'
output - inkml file path
input_type - "file" or "string"
markup_language - "latex" or "mathml"



------------------------------------------

From a python script or notebook:

import generator

generator.generate(markup_input, input_type, markup_language) 
## Returns list of numpy arrays, corresponding MathML, list of trace group sizes, and number of bounding boxes
## trace group sizes correspond to the list of numpy arrays, i.e. [2, 3] means the first 2 arrays correspond to
## the first trace group, and the next 3 arrays correspond to the second.

generator.generate_inkml(markup_input, output, input_type, markup_language)
## Returns None, creates inkml file at path output

-------------------------------------------

Notes for inputs:

Latex must be wrapped in tags, $ ... $, \[ ... \], \begin{math} ... \end{math}, etc
Otherwise conversion to MathML will not work.

Notes for outputs:

InkML is viewable at http://saskatoon.cs.rit.edu/inkml_viewer/ however does not support the full
functionality of this viewer.

InkML also includes a boundingboxes annotation which will be non zero when a bounding box has been
substituted for a symbol without a sample.


SLTErrors.txt contains MathML that did not return a valid SLT.

-------------------------------------------

Config file:

dataset_name : name of subfolder in datasets
metadata_file: name of ground truth file with metadata
inkfile_prefix: prefix to inkml files containing isolated symbols

next/above/below/over/under/frac/radical_degree scale_factor/shift_h/shift_v mean/sd:
parameters of normal distribution to add spacing noise

matrix_column/row_spacing: space to add in between matrix columns and rows

matrix_rsb: matrix right side bearing (space to add after matrix)

rotation/scale/shear mean/sd:
parameters of normal distribution for distortions

grid_distortion_factor: Perturbation factor for grid distortion

--------------------------------------------
Table Creation:

In the Font folder there are 5 json files:
cmap, glyf, customglyf, latextounicode, mathlatextounicode, symb_to_glyf

latextounicode, mathlatextounicode
- Created by latex2unicode.py
- Requires unicode.xml taken from:
https://www.w3.org/TR/xml-entity-names/#source
- Provides lookup tables to translate latex symbols to unicode

symb_to_glyf
- manually created
- creates a map for non unicode symbols to a glyf name

glyf
- Created by makeGlyfTable.py
- Contains bounding box information provided by the font files

customglyf
- Manually created
- Contains bounding box information not provided by the font files
- Used for trig functions, \lim etc.

cmap
- Created by unicode2charname.py
- Provides lookup table to go from unicode to font's glyf name

invisibleunicode
- Manually created
- Contains unicode symbols which are invisible (e.g. invisible multiplication, function application)

Asana is the current font being used, the ttx files can be extracted from a ttf file using the fonttools package

In the datasets folder there is a script to create the gtdict.json file used to query the dataset
by glyph name.
---------------------------------------------------------------------------

utils Folder

distortions.py
- Handles symbols distortions

get_glyf_info.py
- Used for getting glyf names from unicode or custom glyf table

inkml2array.py
- Used for converting an inkml file into a list of numpy arrays

np2inkml.py
- Used for converting list of numpy arrays into an inkml file

----------------------------------------------------------------------------

datasets Folder

makeGroundTruthTable.py
- Contains make_gt_table function used to create the gtdict.json file.
- gtdict.json provides a lookup table from glyph names to a list of samples


-----------------------------------------------------------------------------

ExpressionClass.py

- Holds python object Expression class which holds symbol and SLT information
- Also contains the main function to recursively combine the Expression into one list of traces
- Accesses config file

------------------------------------------------------------------------------

generator.py

- Wrapper function and entry point
- Contains functions to output inkml file as well as list of numpy arrays

------------------------------------------------------------------------------

math2tree.py

- Used to hold functions which go from latex to mathml, mathml to edges from the slt, and create an Expression which reconstructs the tree.

-------------------------------------------------------------------------------

