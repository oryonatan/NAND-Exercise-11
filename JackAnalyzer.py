__author__ = 'larrath'
import sys
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
        # print("\n\n\nParsing file #" + str(i + 1) + " (" + file_names[i] + ")")
        parsed_files.append(parse(tokenized_data[i]))
    
    return parsed_files, file_names

