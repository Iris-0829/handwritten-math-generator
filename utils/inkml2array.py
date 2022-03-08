import numpy as np
import xml.etree.ElementTree as ET

def inkML_to_np(filename):
    '''
    inkML_to_traces takes an inkml file and returns a list of numpy arrays
    Each numpy array represents the coordinates of a trace (stroke)
    '''
    tree = ET.parse(filename)
    root = tree.getroot()
    traces = []
    xmax = ''

    for child in root:
        if 'trace' in child.tag and child.get('id') is not None:
            coords = child.text
            coords = coords.strip()
            coords = coords.split(',')
            for i in range(len(coords)):
                coords[i] = coords[i].strip().split(' ')
            npcoords = np.array(coords, dtype=np.float32).T
            npcoords = npcoords[:2, :]
            tracemax = np.amax(npcoords, axis = 1)
            tracemin = np.amin(npcoords, axis = 1)
            if xmax == '':
                xmax = tracemax[0]
                ymax = tracemax[1]
                xmin = tracemin[0]
                ymin = tracemin[1]
            else:
                xmax = max(tracemax[0], xmax)
                ymax = max(tracemax[1], ymax)
                xmin = min(tracemin[0], xmin)
                ymin = min(tracemin[1], ymin)
            traces.append(npcoords)
    
    for i in range(len(traces)):
        # Set lower left corner to 0, 0
        traces[i] = traces[i] - np.expand_dims([xmin, ymax], axis = 1)
        # Flip y-axis
        traces[i][1] = -traces[i][1]

    return traces