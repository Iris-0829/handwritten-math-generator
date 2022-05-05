import csv
import latex2mathml.converter
import os
import shutil
import pathlib


def parse(filename):
    if not os.path.exists("input"):
        os.makedirs("input")
    if not os.path.exists("output"):
        os.makedirs("output")
    with open(filename) as fd:
        rd = csv.reader(fd, delimiter="\t", quotechar='"')
        i = 1
        for row in rd:
            with open("./input/" + str(i) + ".txt", 'w') as f: #TODO
                mathml = latex2mathml.converter.convert(row[8])
                f.write(mathml)
            os.system("python3.9 generator.py -l mathml input/" + str(i) + ".txt output/" + str(i) + ".inkml")
            i += 1
            # if i > 100:
            #     break

    for k in range(1, i):
        with open('input/' + str(k) + ".inkml", 'r') as file:
            data = file.read().replace('\n', '')
            if '\"boundingboxes\">0' not in data:
                os.remove('input/' + str(k) + '.inkml')


parse('1.tsv')