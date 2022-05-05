import json
import os.path as osp
import sys
import os

def create_inkml(jsonFile, root_dir, fileName):
    input_strokes = json.load(open(jsonFile))
    name = os.path.splitext(os.path.basename(fileName))[0]
    with open(osp.join(root_dir, name + ".inkml"), "w") as f:
        f.write('<ink xmlns=\"http://www.w3.org/2003/InkML\">\n' +
                '<traceFormat>\n' +
                '<channel name="X" type="decimal"/>\n' +
                '<channel name="Y" type="decimal"/>\n' +
                '</traceFormat>\n')
        for stroke in input_strokes:
            f.write('<trace id="' + str(stroke['strokeId']) + '">\n')
            f.write(", ".join([" ".join(map(str, point.values())) for point in stroke['points']]) + "\n</trace>\n")
        f.write("</ink>")

def json_to_inkml(input_string):
    input_strokes = json.loads(input_string)
    output_string = '''<ink xmlns=\"http://www.w3.org/2003/InkML\">
                    <traceFormat>
                    <channel name="X" type="decimal"/>
                    <channel name="Y" type="decimal"/>
                    </traceFormat>\n'''
    for stroke in input_strokes:
        output_string += '<trace id="' + str(stroke['strokeId']) + '">\n'
        output_string += ", ".join([" ".join(map(str, point.values())) for point in stroke['points']]) + "\n</trace>\n"
    output_string += "</ink>"
    return output_string