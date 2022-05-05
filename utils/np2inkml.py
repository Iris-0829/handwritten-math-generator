import numpy as np
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, Comment, tostring, ElementTree
from xml.dom import minidom



def to_inkml(np_input, latex_truth, trace_groups, bounding_boxes, filename):
    
    np.set_printoptions(suppress=True)
    ink = Element('ink', attrib={'xmlns':"http://www.w3.org/2003/InkML"})
    traceFormat = SubElement(ink, 'traceFormat')
    channel_x = SubElement(traceFormat, 'channel', attrib={'name':"X", 'type':"decimal"})
    channel_y = SubElement(traceFormat, 'channel', attrib={'name':"Y", 'type':"decimal"})
    
    annotation_truth = SubElement(ink, 'annotation', 
                                  attrib = {'type':'truth'})
    annotation_truth.text = latex_truth
    annotation_bb = SubElement(ink, 'annotation',
                               attrib = {'type':'boundingboxes'})
    annotation_bb.text = str(bounding_boxes)
    annotationXML = SubElement(ink, 'annotationXML',
                               attrib = {'type':'truth', 'encoding':"Content-MathML"})

    for i in range(len(np_input)):
        trace = np.transpose(np_input[i])
        trace_string = np.array2string(trace, separator=' ', precision = 4, floatmode = 'fixed')
        trace_string = trace_string.replace('[', '').replace(']', '').replace('\n', ',')
        trace_i = SubElement(ink, 'trace', attrib={'id':str(i)})
        trace_i.text = trace_string.lstrip()

    #xmlstr = minidom.parseString(ET.tostring(ink)).toprettyxml(indent="   ")
    with open(filename, "wb") as f:
        f.write(ET.tostring(ink))

    with open(filename, 'r') as f:
        newlines = []
        for line in f.readlines():
            newlines.append(line.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&"))
    with open(filename, 'w') as f:
        for line in newlines:
            f.write(line)
