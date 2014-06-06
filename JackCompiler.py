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

    dump_xml = False
    # dump_xml = True
    if dump_xml:
        print("Compiler Module debug mode activated\n")
        print("=" * 30)

    for i in range(len(xml_data)):
        print("\n\n\nCompiling file #" + str(i + 1) + " (" + file_names[i] + ")")
        if dump_xml:
            # print("Parser debug mode: parsing file #" + str(i + 1) + " (" + file_names[i] + ")")
            print("~" * 20)
            print(xml_data[i].toprettyxml())
            source_code = encode(xml_data[i])
            print("~" * 20)
            print("File number #" + str(i + 1) + " compilation complete\n")
            print ("=" * 30)

        else:
            source_code = encode(xml_data[i])
            with open(file_names[i].replace('.jack', '.vm'), 'w') as f:
                f.write(source_code)

    if dump_xml:
        print("\n\nAll processing finished")