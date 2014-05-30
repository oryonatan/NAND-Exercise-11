__author__ = 'larrath'
import sys
from Tokenizer import tokenize
from Parser import parse

if __name__ == '__main__':

    root_dir = ''
    try:
        root_dir = sys.argv[1]
    except IndexError:
        print("No input file name")
        exit()

    tokenized_data, file_names = tokenize(root_dir)

    if (len(tokenized_data) != len(file_names)):
        raise Exception("XML data and file names count mismatch")

    # print(tokenized_data[0].toprettyxml())
    # print("\n")
    # print(tokenized_data[1].toprettyxml())
    # print("\n")
    # print(tokenized_data[2].toprettyxml())
    debug_mode = False
    # debug_mode = True
    if debug_mode:
        print("Parser Module debug mode activated\n")
        print("=" * 30)
    for i in range(len(tokenized_data)):
        print("\n\n\nParsing file #" + str(i + 1) + " (" + file_names[i] + ")")
        if (i == 25):
            print(tokenized_data[i].toprettyxml())
        if debug_mode:
            # print("Parser debug mode: parsing file #" + str(i + 1) + " (" + file_names[i] + ")")
            print("~" * 20)
            xml_code = parse(tokenized_data[i], True)
            print("~" * 20)
            print("File number #" + str(i + 1) + " parsing complete\n")
            print ("Parsing returned")
            print ("=" * 30)
            break
        else:
            xml_code = parse(tokenized_data[i])
            with open(file_names[i].replace('.jack', '.xml'), 'w') as f:
                f.write(xml_code.toprettyxml())
    if debug_mode:
        print("\n\nAll processing finished")
