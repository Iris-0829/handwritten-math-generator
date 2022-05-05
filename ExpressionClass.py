# -*- coding: utf-8 -*-
import json
import random
import logging
import warnings
import numpy as np
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import utils.distortions as dist
from fuzzywuzzy import fuzz
from utils.inkml2array import inkML_to_np
from utils.get_glyf_info import get_glyf_name, isfloat


class Expression:
    '''
    Class to hold tree structure and trace (stroke) information
    '''
        
    def __init__(self, name):
        '''
        Initialized instance of class
        '''
        self.name = name
        self.traces = None
        self.num_traces = []
        self.trace_idx = None # Index of sample in database
        
        self.next = None
        self.above = None # Superscript
        self.below = None # Subscript
        self.over = None
        self.under = None 
        self.within = None
        self.radical_degree = None
        self.element = None # Next Matrix element
        
        self.xmax = None
        self.xmin = None
        self.ymax = None
        self.ymin = None
        self.width = None
        self.height = None
        self.rsb = None # Right Side Bearing
        
        self.bounding_box = 0
        
    def child_list(self):
        return [self.next, self.above, self.below, self.over, self.under, 
                self.within, self.element, self.radical_degree]
    
    def calc_bounds(self):
        if self.traces is None:
            print('Need to get_traces first')
            pass
        elif self.name == 'invis' or self.name == 'space':
            pass
        else:
            trace_xmaxs = []
            trace_xmins = []
            trace_ymaxs = []
            trace_ymins = []

            for i in range(len(self.traces)):
                trace_max = np.amax(self.traces[i], axis = 1)
                trace_min = np.amin(self.traces[i], axis = 1)
                trace_xmaxs.append(trace_max[0])
                trace_xmins.append(trace_min[0])
                trace_ymaxs.append(trace_max[1])
                trace_ymins.append(trace_min[1])

            self.xmax = max(trace_xmaxs) if len(trace_xmaxs) != 0 else 0
            self.xmin = min(trace_xmins) if len(trace_xmins) != 0 else 0
            self.ymax = max(trace_ymaxs) if len(trace_ymaxs) != 0 else 0
            self.ymin = min(trace_ymins) if len(trace_ymins) != 0 else 0
            self.width = self.xmax - self.xmin
            self.height = self.ymax - self.ymin
    
    def scale_traces(self, factor):
        
        for i in range(len(self.traces)):
            self.traces[i] = self.traces[i] * factor
    
    def scale_traces_h(self, factor):
        
        for i in range(len(self.traces)):
            self.traces[i][0] = self.traces[i][0] * factor
        
        self.calc_bounds()
        
    def scale_traces_v(self, factor):
        
        for i in range(len(self.traces)):
            self.traces[i][1] = self.traces[i][1] * factor
        
        self.calc_bounds()
        
    def scale_within_width(self, width, start):
        
        within_width = self.within.xmax + 100
        factor = within_width/width
        
        for i in range(len(self.traces)):
            for j in range(self.traces[i][0].shape[0]):
                if self.traces[i][0][j] > start:
                    self.traces[i][0][j] = (self.traces[i][0][j] - start) * factor + start
    
    def shift_traces(self, x, y):
        
        for i in range(len(self.traces)):
            self.traces[i][0] = self.traces[i][0] + x
            self.traces[i][1] = self.traces[i][1] + y
    
    def get_traces(self):
        '''
        Obtains trace (stroke) data from target source
        '''
        if self.name[0:6] == 'Matrix':
            
            pass
        
        elif self.name == "invis":
            self.traces = []
            self.xmax = 0
            self.xmin = 0
            self.ymax = 0
            self.ymin = 0
            self.width = 0
            self.height = 0
            self.rsb = 0
            
            
        elif (isfloat(self.name) or self.name[0:4] == 'Text') and self.name != 'infinity':
             
                
            symbol_list = list(self.name if self.name[0:4] != 'Text' else self.name[7:])
            glyf_list = list(map(get_glyf_name, symbol_list))
            if len(glyf_list) == 0:
                glyf_list = ['space']
            Exp_list = list(map(Expression, glyf_list))
            
            for i in range(len(Exp_list) - 1):
                Exp_list[i].next = Exp_list[i + 1]
            
            sub_root = Exp_list[0]
            
            sub_root.get_traces()
            
            sub_root.absorb()
            
            self.traces = sub_root.traces
            self.bounding_box = sub_root.bounding_box
            self.trace_idx = sub_root.trace_idx
            idx = sub_root.trace_idx
            
            self.rsb = sub_root.rsb
            self.calc_bounds()
        
        elif self.name == 'space':
            self.traces = []
            self.xmax = 0
            self.xmin = 0
            self.ymax = 1000
            self.ymin = 0
            self.width = 0
            self.height = 0
            self.rsb = 1000

        else:
            with open('./datasets/{0}/gtdict.json'.format(config['dataset_name']), 'r') as gt_file:
                ground_truth_table = json.load(gt_file)
            with open('./datasets/{0}/{1}'.format(config['dataset_name'], config['metadata_file']), 'r') as metadata_file:
                metadata = metadata_file.readlines()
            
            if self.name == '¯':
                self.name = 'hyphen'
            
            if self.name not in ground_truth_table and self.name != 'frac':
                
                ## Insert bounding box for symbol with no sample
                
                log_str = "No handwritten data for symbol " + self.name

                with open("Missing_symbol.txt", "a+") as f:
                    f.write(self.name + '\n')
                logging.warning(log_str)
                warnings.warn(log_str)
                
                
                glyf_info = glyfs[self.name]
                glyf_xmin = int(glyf_info[0])
                glyf_ymin = int(glyf_info[1])
                glyf_xmax = int(glyf_info[2])
                glyf_ymax = int(glyf_info[3])
                full_width = int(glyf_info[4])
                
                bounding_box = [[glyf_xmin, glyf_xmax, glyf_xmax, glyf_xmin, glyf_xmin],
                                [glyf_ymin, glyf_ymin, glyf_ymax, glyf_ymax, glyf_ymin]]
                self.traces = [np.array(bounding_box)]
                self.rsb = full_width - glyf_xmax
                self.calc_bounds()
                self.bounding_box = 1
                 
            else:
                
                idx_list = ground_truth_table[self.name if not self.name in ['minus', 'frac', '¯'] else 'hyphen']

                if self.trace_idx is None:
                    idx = random.choice(idx_list)
                    self.traces = inkML_to_np('./datasets/{0}/{1}{2}.inkml'.format(config['dataset_name'],
                                                                                   config['inkfile_prefix'],
                                                                                   idx))
                    self.trace_idx = idx
                else:
                    idx = max(idx_list, key=lambda x:fuzz.ratio(metadata[x], metadata[self.trace_idx]))
                    self.traces = inkML_to_np('./datasets/{0}/{1}{2}.inkml'.format(config['dataset_name'],
                                                                                   config['inkfile_prefix'],
                                                                                   idx))
                self.calc_bounds()

                if self.name not in glyfs and not self.name == 'frac':
                    print(self.name + ' does not have a glyf')

                else:

                    glyf_info = glyfs[self.name if not self.name in ['frac', 'hyphen'] else 'minus']
                    glyf_xmin = int(glyf_info[0])
                    glyf_ymin = int(glyf_info[1])
                    glyf_xmax = int(glyf_info[2])
                    glyf_ymax = int(glyf_info[3])
                    full_width = int(glyf_info[4])

                    glyf_width = glyf_xmax - glyf_xmin
                    glyf_height = glyf_ymax - glyf_ymin

                    if self.height > self.width:
                        scale_factor = glyf_height/self.height
                    else:
                        scale_factor = glyf_width/self.width

                    self.scale_traces(scale_factor)
                    self.shift_traces(glyf_xmin, glyf_ymin)

                    self.rsb = full_width - glyf_xmax
                    self.num_traces = [len(self.traces)]

                    self.distort()
                    self.calc_bounds()
                
        for child in self.child_list():
            if child is not None:

                child.trace_idx = self.trace_idx
                child.get_traces()
    
        
    def show_symbol(self, axis = 'off'):
        for i in range(len(self.traces)):
            plt.plot(self.traces[i][0], self.traces[i][1], color='black')
        plt.axis('scaled')
        plt.axis(axis)
        plt.show
    
    def absorb_next(self):
        shift_noise_h = np.random.normal(config['next_shift_h_mean'], config['next_shift_h_sd'])
        shift_noise_v = np.random.normal(config['next_shift_v_mean'], config['next_shift_v_sd'])
        
        self.next.shift_traces(self.xmax + self.rsb + shift_noise_h, shift_noise_v)
        
        self.traces.extend(self.next.traces)
        self.num_traces.extend(self.next.num_traces)
        self.bounding_box += self.next.bounding_box
        
        self.rsb = self.next.rsb
        
        self.next = None
        
        self.calc_bounds()
        
    def absorb_above(self):
        
        scale_factor = np.random.normal(config['above_scale_mean'], config['above_scale_sd'])
        shift_noise_h = np.random.normal(config['above_shift_h_mean'], config['above_shift_h_sd'])
        shift_noise_v = np.random.normal(config['above_shift_v_mean'], config['above_shift_v_sd'])
        
        self.above.scale_traces(scale_factor)
        
        self.above.shift_traces(self.xmax + self.rsb * 1/2 + shift_noise_h, self.ymax + shift_noise_v)
        
        self.traces.extend(self.above.traces)
        self.num_traces.extend(self.above.num_traces)
        self.bounding_box += self.above.bounding_box
        
        self.above = None
    
    def absorb_below(self):
        
        scale_factor = np.random.normal(config['below_scale_mean'], config['below_scale_sd'])
        shift_noise_h = np.random.normal(config['below_shift_h_mean'], config['below_shift_h_sd'])
        shift_noise_v = np.random.normal(config['below_shift_v_mean'], config['below_shift_v_sd'])
        
        self.below.scale_traces(scale_factor)
        
        self.below.shift_traces(self.xmax + self.rsb * 1/2 + shift_noise_h, 
                                shift_noise_v + (0 if not self.name == 'integral' else  self.ymin))
        self.traces.extend(self.below.traces)
        self.num_traces.extend(self.below.num_traces)
        self.bounding_box += self.below.bounding_box
        
        self.below = None
    
    
    def absorb_over(self):
        
        scale_factor = np.random.normal(config['over_scale_mean'], config['over_scale_sd'])
        shift_up = config['over_shift_up']
        shift_noise_h = np.random.normal(config['over_shift_h_mean'], config['over_shift_h_sd'])
        shift_noise_v = np.random.normal(config['over_shift_v_mean'], config['over_shift_v_sd'])
        
        self.over.scale_traces(scale_factor)
        self.over.calc_bounds()
        
        xshift = self.width * 1/2 - self.over.width * 1/2 + self.xmin
        yshift = self.ymax - self.over.ymin + shift_up
        
        self.over.shift_traces(xshift + shift_noise_h, yshift + shift_noise_v)
        
        self.traces.extend(self.over.traces)
        self.num_traces.extend(self.over.num_traces)
        self.bounding_box += self.over.bounding_box
        
        self.over = None
    
    def absorb_under(self, scale_factor = None, shift_down = None):
        
        if scale_factor is None:
            scale_factor = np.random.normal(config['under_scale_mean'], config['under_scale_sd'])
        if shift_down is None:
            shift_down = config['under_shift_down']
        shift_noise_h = np.random.normal(config['under_shift_h_mean'], config['under_shift_h_sd'])
        shift_noise_v = np.random.normal(config['under_shift_v_mean'], config['under_shift_v_sd'])
        
        self.under.scale_traces(scale_factor)
        self.under.calc_bounds()
        
        xshift = self.width * 1/2 - self.under.width * 1/2 + self.xmin
        yshift = - self.under.ymax + self.ymin - shift_down
        
        self.under.shift_traces(xshift + shift_noise_h, yshift + shift_noise_v)
        
        self.traces.extend(self.under.traces)
        self.num_traces.extend(self.under.num_traces)
        self.bounding_box += self.under.bounding_box
        
        self.under = None
        
    def absorb_fraction(self):
        
        new_width = max(self.over.width, self.under.width)
        
        width_scale_factor = np.random.normal(config['frac_scale_factor_mean'], config['frac_scale_factor_sd'])

        self.scale_traces_h(new_width/self.width * width_scale_factor)
        self.calc_bounds()
        
        over_shift_up = config['frac_over_shift_up']
        under_shift_down = config['frac_under_shift_down']
        over_shift_noise_h = np.random.normal(config['over_shift_h_mean'], config['over_shift_h_sd'])
        over_shift_noise_v = np.random.normal(config['over_shift_v_mean'], config['over_shift_v_sd'])
        under_shift_noise_h = np.random.normal(config['under_shift_h_mean'], config['under_shift_h_sd'])
        under_shift_noise_v = np.random.normal(config['under_shift_v_mean'], config['under_shift_v_sd'])
        
        
        
        self.over.shift_traces(1/2 * self.width - 1/2 * self.over.width + self.xmin + over_shift_noise_h, 
                               self.ymax - self.over.ymin + over_shift_up + over_shift_noise_v)
        
        self.under.shift_traces(1/2 * self.width - 1/2 * self.under.width + self.xmin + under_shift_noise_h, 
                                -self.under.ymax + self.ymin - under_shift_down + under_shift_noise_v)
        
        self.traces.extend(self.over.traces)
        self.num_traces.extend(self.over.num_traces)
        self.traces.extend(self.under.traces)
        self.num_traces.extend(self.under.num_traces)
        self.bounding_box += (self.over.bounding_box + self.under.bounding_box)
        
        self.over = None
        self.under = None
    
    def absorb_radical_degree(self):
        scale_factor = np.random.normal(config['radical_degree_scale_factor_mean'],
                                        config['radical_degree_scale_factor_sd'])
        shift_noise_h = np.random.normal(config['radical_degree_shift_h_mean'], 
                                         config['radical_degree_shift_h_sd'])
        shift_noise_v = np.random.normal(config['radical_degree_shift_v_mean'],
                                         config['radical_degree_shift_v_sd'])
        
        self.radical_degree.scale_traces(scale_factor)
        
        self.radical_degree.shift_traces(self.xmin - 0.5 * scale_factor * self.radical_degree.xmax + shift_noise_h, 
                                         0.75 * self.ymax + shift_noise_v)
        self.traces.extend(self.radical_degree.traces)
        self.num_traces.extend(self.radical_degree.num_traces)
        self.bounding_box += self.radical_degree.bounding_box
        
        self.radical_degree = None
        
    
    def absorb_within(self):
        
        x1, y1, x2, y2 = largest_empty_rectangle(self)
        
        self.scale_traces_v(self.within.height/(y2 - y1))
        
        x1, y1, x2, y2 = largest_empty_rectangle(self)
        
        
        self.scale_within_width(x2 - x1, x1)
        
        self.within.shift_traces(x1, y1 - self.within.ymin )
        
        self.traces.extend(self.within.traces)
        self.num_traces.extend(self.within.num_traces)
        self.bounding_box += self.within.bounding_box
        self.calc_bounds()
        
        self.within = None
        
    def absorb_matrix(self):
        
        matrix_data = self.name.split('|_|')
        
        brackets = list(matrix_data[1])
        
        num_rows = int(matrix_data[2][0])
            
        num_cols = int(matrix_data[2][-1])

        num_elems = num_rows * num_cols
        
        cur_elem = self
        elems = np.empty((num_rows, num_cols),dtype='object')
        if num_rows == 1:
            matrix_internal = self.within
            matrix_internal.absorb()
            
            bracket_glyf_names = list(map(get_glyf_name, brackets))
            bracket_symbols = list(map(Expression, bracket_glyf_names))

            for brack in bracket_symbols:

                brack.get_traces()

            if len(bracket_symbols) == 1:
                bracket_symbols[0].next = matrix_internal
                bracket_symbols[0].absorb_next()
                self.traces = bracket_symbols[0].traces
                self.bounding_box = bracket_symbols[0].bounding_box
                self.num_traces = bracket_symbols[0].num_traces
                self.rsb = matrix_internal.rsb
            elif len(bracket_symbols) == 2:
                bracket_symbols[0].next = matrix_internal
                matrix_internal.next = bracket_symbols[1]
                matrix_internal.absorb_next()
                bracket_symbols[0].absorb_next()
                self.traces = bracket_symbols[0].traces
                self.bounding_box = bracket_symbols[0].bounding_box
                self.num_traces = bracket_symbols[0].num_traces
                self.rsb = bracket_symbols[1].rsb
            
        else:
            for r in range(num_rows):
                for c in range(num_cols):
                    if r == 0 and c == 0:
                        elems[r, c] = cur_elem.within
                        cur_elem = cur_elem.within
                    else:
                        elems[r, c] = cur_elem.element
                        cur_elem = cur_elem.element

                    if cur_elem is not None:
                        cur_elem.absorb()


            # Set height of all elements of a row to be equal
            for s in range(num_rows):
                row = elems[s]
                row_ymins = []
                row_ymaxs = []
                for elem in row:
                    row_ymins.append(elem.ymin)
                    row_ymaxs.append(elem.ymax)
                row_ymin = min(row_ymins)
                row_ymax = min(row_ymaxs)
                for elem in row:
                    elem.ymin = row_ymin
                    elem.ymax = row_ymax

            # Set width of all elements of a columns to be equal
            for d in range(num_cols):
                col = elems[:, d]
                col_xmins = []
                col_xmaxs = []
                for elem in col:
                    col_xmins.append(elem.xmin)
                    col_xmaxs.append(elem.xmax)
                col_xmin = min(col_xmins)
                col_xmax = max(col_xmaxs)
                for elem in col:
                    elem.xmin = col_xmin
                    elem.xmax = col_xmax

            # Assemble rows
            for t in range(num_rows):
                row = elems[t]
                for e in range(num_cols - 1):
                    row[e].next = row[e + 1]
                    row[e].rsb = config['matrix_column_spacing']
                    row[e].element = None
                row[0].absorb()
                row[0].calc_bounds()


            # Stack rows
            for f in range(num_rows - 2, -1, -1):
                row = elems[f]
                row[0].under = elems[f+1, 0]
                row[0].absorb_under(scale_factor = 1, shift_down = config['matrix_row_spacing'])
                row[0].calc_bounds()

            matrix_internal = elems[0, 0]

            matrix_internal.calc_bounds()

            bracket_glyf_names = list(map(get_glyf_name, brackets))
            bracket_symbols = list(map(Expression, bracket_glyf_names))

            for brack in bracket_symbols:

                brack.get_traces()
                brack.scale_traces(matrix_internal.height/brack.height)
                brack.calc_bounds()

                brack.shift_traces(0, matrix_internal.ymin - brack.ymin)

            if len(bracket_symbols) == 0:
                self.traces = matrix_internal.traces
                self.num_traces = matrix_internal.num_traces
                self.bounding_box = matrix_internal.bounding_box

            elif len(bracket_symbols) == 1:
                bracket_symbols[0].next = matrix_internal
                bracket_symbols[0].absorb_next()
                self.traces = bracket_symbols[0].traces
                self.num_traces = bracket_symbols[0].num_traces
                self.bounding_box = bracket_symbols[0].bounding_box
                
            elif len(bracket_symbols) == 2:
                bracket_symbols[0].next = matrix_internal
                matrix_internal.next = bracket_symbols[1]
                matrix_internal.absorb_next()
                bracket_symbols[0].absorb_next()
                self.traces = bracket_symbols[0].traces
                self.num_traces = bracket_symbols[0].num_traces
                self.bounding_box = bracket_symbols[0].bounding_box 

        self.calc_bounds()
        if num_rows > 1:
            self.shift_traces(0, 0.5 * self.height - self.ymax)
            self.rsb = config['matrix_rsb']

        self.within = None

    
    def absorb(self):
        if self.name[0:6] == 'Matrix' and self.traces is None:
            self.absorb_matrix()
        
        if self.name == 'summation':
            self.over = self.above if self.above is not None else self.over
            self.above = None
            self.under = self.below if self.below is not None else self.under
            self.below = None
        
        if self.within is not None:
            self.within.absorb()
            self.within.calc_bounds()
            self.absorb_within()
        if self.radical_degree is not None and self.radical_degree.name != "two":
            self.radical_degree.absorb()
            self.radical_degree.calc_bounds()
            self.absorb_radical_degree()
            self.calc_bounds()
        
        if self.above is not None:
            self.above.absorb()
            self.absorb_above()
            if self.below is None:
                self.calc_bounds()
                self.rsb = 90
        if self.below is not None:
            self.below.absorb()
            self.absorb_below()
            self.calc_bounds()
            self.rsb = 90
        
        
        if self.name == 'frac':
            self.over.absorb()
            self.under.absorb()
            self.absorb_fraction()
            
        
        if self.over is not None:
            self.over.absorb()
            self.over.calc_bounds()
            self.absorb_over()
        if self.under is not None:
            self.under.absorb()
            self.under.calc_bounds()
            self.absorb_under()
       
        if self.next is not None:
            self.next.absorb()
            self.absorb_next()
            self.calc_bounds()
    
    def distort(self):
        distortion = np.random.randint(0, 5)
        
        if distortion == 0:
            alpha = np.random.normal(config['shear_mean'], config['shear_sd'])
            for i in range(len(self.traces)):
                self.traces[i][0], self.traces[i][1] = dist.distortHorizShear(self.traces[i][0], self.traces[i][1], alpha)
                
        elif distortion == 1:
            
            alpha = np.random.normal(config['shear_mean'], config['shear_sd'])
            for i in range(len(self.traces)):
                self.traces[i][0], self.traces[i][1] = dist.distortVertShear(self.traces[i][0], self.traces[i][1], alpha)
                
        elif distortion == 2:
            
            alpha = np.random.normal(config['rotation_mean'], config['rotation_sd'])
            for i in range(len(self.traces)):
                self.traces[i][0], self.traces[i][1] = dist.distortRotate(self.traces[i][0], self.traces[i][1], alpha)
                
        elif distortion == 3:
            
            scale_factor = np.random.normal(config['scale_distort_mean'], config['scale_distort_sd'])
            for i in range(len(self.traces)):
                self.traces[i][0], self.traces[i][1] = dist.distortScale(self.traces[i][0], self.traces[i][1], scale_factor)
        
        elif distortion == 4:
            
            noise_x = np.random.normal(0, 1000 * config['grid_distortion_factor'], (4, 1))
            noise_y = np.random.normal(0, 1000 * config['grid_distortion_factor'], (4, 1))
            noise = np.concatenate((noise_x, noise_y), axis = 1)

            src = np.array([[0, 0], 
                           [0, 1000], 
                           [1000, 0], 
                           [1000, 1000]])
            dst = src + noise
            
            coeffs = dist.warp_distortion_coeffs(src, dst)
            for i in range(len(self.traces)):
                self.traces[i][0], self.traces[i][1] = dist.warp_transformation(coeffs, self.traces[i][0], self.traces[i][1])


def get_glyf_table():
    glyf_file = open('./Font/glyf.json')
    custom_glyf_file = open('./Font/customglyf.json')
    
    glyfs = json.load(glyf_file)
    custom_glyfs = json.load(custom_glyf_file)
    
    glyf_file.close()
    custom_glyf_file.close()
    
    glyfs.update(custom_glyfs)
    return glyfs

glyfs = get_glyf_table()

def load_config():
    config_file = open('config.json')
    config = json.load(config_file)
    config_file.close()
    return config

config = load_config()

def largest_empty_rectangle(symbol, n = 25):
    '''
    Finds the largest empty rectangle
    returns the bottom right and top left coordinates of the maximal rectangle
    
    Creates a binary array 
    '''
    xgrid = np.linspace(symbol.xmin, symbol.xmax, num = n)
    ygrid = np.linspace(symbol.ymin, symbol.ymax, num = n)
    z = np.zeros((n, n))
    
    traces = symbol.traces
    for trace in traces:
        xvals = trace[0]
        yvals = trace[1]
        for i in range(xvals.shape[0]):
            
            xval = xvals[i]
            yval = yvals[i]
            
            xidx = np.argmin(xval >= xgrid)
            yidx = np.argmin(yval >= ygrid)
            
            z[xidx][yidx] = 1
    
    xmin, ymin, xmax, ymax = largest_zero_subarray(z)
    
    
        
    return xgrid[xmin], ygrid[ymin], xgrid[xmax], ygrid[ymax]

def largest_zero_subarray(a):
    '''
    https://stackoverflow.com/questions/2478447/find-largest-rectangle-containing-only-zeros-in-an-n%C3%97n-binary-matrix
    Largest rectangular subarray of zeros
    '''
    
    skip = 1
    area_max = (0, [])
    w = np.zeros(dtype=int, shape=a.shape)
    h = np.zeros(dtype=int, shape=a.shape)
    nrows = a.shape[0]
    ncols = a.shape[1]
    for r in range(nrows):
        for c in range(ncols):
            if a[r][c] == skip:
                continue
            if r == 0:
                h[r][c] = 1
            else:
                h[r][c] = h[r-1][c]+1
            if c == 0:
                w[r][c] = 1
            else:
                w[r][c] = w[r][c-1]+1
            minw = w[r][c]
            for dh in range(h[r][c]):
                minw = min(minw, w[r-dh][c])
                area = (dh+1)*minw
                if area > area_max[0]:
                    area_max = (area, [(r-dh, c-minw+1, r, c)])

    return area_max[1][0]

