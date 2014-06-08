import sys
from JackAnalyzer import analyze
from CodeWriter import encode

if __name__ == '__main__':

    root_dir = ''
    try:
        root_dir = sys.argv[1]
    except IndexError:
        print("No input file name")
        exit()

    xml_data, file_names = analyze(root_dir)

    for i in range(len(xml_data)):
        source_code = encode(xml_data[i])
        with open(file_names[i].replace('.jack', '.vm'), 'w') as f:
            f.write(source_code)