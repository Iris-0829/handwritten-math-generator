import numpy as np
import xml.etree.ElementTree as ET
import json

glyfTree = ET.parse('./Asana/Asana-glyf.ttx')
glyfRoot = glyfTree.getroot()[0]

glyfTable = {}

for child in glyfRoot:
    glyfTable[child.get('name')] = [child.get('xMin'), 
                                    child.get('yMin'),
                                    child.get('xMax'),
                                    child.get('yMax')]

htmxTree = ET.parse('./Asana/Asana-hmtx.ttx')
htmxRoot = htmxTree.getroot()[0]

for child in htmxRoot:
    name = child.get('name')
    if name in glyfTable:
        glyfTable[name].append(child.get('width'))

to_json = json.dumps(glyfTable)
f = open("glyf.json", "w")
f.write(to_json)
f.close()
   