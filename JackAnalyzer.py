__author__ = 'larrath'

from Tokenizer import tokenize
from Parser import parse

def analyze(root_dir):
    
    if (len(root_dir) == 0):
        print("No input file name")
        exit()

    tokenized_data, file_names = tokenize(root_dir)

    if (len(tokenized_data) != len(file_names)):
        raise Exception("XML data and file names count mismatch")

    parsed_files = []

    for i in range(len(tokenized_data)):
        parsed_files.append(parse(tokenized_data[i]))
        # print(('*' * 20) + "\tFile #" + str(i) + '\t' + ('*' * 20))
        # print(parsed_files[-1].toprettyxml())

    
    return parsed_files, file_names