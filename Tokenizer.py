__author__ = 'yonatan'

import os
import xml.dom.minidom as minidom
import re
import sys

java_style_escape = False

keywords = ('class',
            'constructor',
            'function',
            'method',
            'field',
            'static',
            'var',
            'int',
            'char',
            'boolean',
            'void',
            'true',
            'false',
            'null',
            'this',
            'let',
            'do',
            'if',
            'else',
            'while',
            'return')
symbols = set("~{}()[].,;+-*/&|<>=-")


def clean_inline_comments(line):
    #line = re.sub("//.*", '', line).strip()
    return line


def append_to_top(XML, element_type, char):
    node = XML.createElement(element_type)
    node_text = XML.createTextNode(" " + char + " ")
    node.appendChild(node_text)
    XML.documentElement.appendChild(node)


def append_string(XML, all_text, i):
    end_of_string = all_text.find('"', i + 1)
    tmp_str = all_text[i + 1: end_of_string]
    if java_style_escape:
        tmp_str = re.sub("\\\\t", "\t", tmp_str)  # java mishandles tabs in strings   :(
        tmp_str = re.sub("/\\\\", "/", tmp_str)  # java mishandles some escaping
    append_to_top(XML, "stringConstant", tmp_str)
    return end_of_string


def append_number(XML, all_text, i, tmp_str):
    while tmp_str.isdigit():
        i += 1
        tmp_str += all_text[i]
    append_to_top(XML, "integerConstant", tmp_str[:-1])
    return i-1


def append_keyword_or_identifier(XML, all_text, i):
    tmp_str = re.findall("([A-Za-z_][A-Za-z_0-9]*)", all_text[i:])[0]
    if tmp_str in keywords:
        append_to_top(XML, "keyword", tmp_str)
    else:
        append_to_top(XML, "identifier", tmp_str)
    return i + len(tmp_str) - 1


def clean_comments(text):
    i = 0
    in_string = False
    text_copy = []
    while i < len(text):
        char = text[i]
        if char == '"':
            in_string = not in_string
            text_copy.append(char)

        elif not in_string and text[i:i+2] == "//":
            i+=2
            while text[i] != "\n":
                i+=1


        elif text[i:i+2] == "/*" and in_string:
            text_copy.append(char)

        elif text[i:i+2] == "/*" and not in_string:
            i+=2
            while text[i:i+2] != "*/":
                i+=1
            i+=1
            text_copy.append(" ")

        elif char != "\n":
            text_copy.append(char)
        i +=  1

    return "".join(text_copy)





def create_XML(filename):
    with open(filename) as f:
        all_text = f.read()
    #file_lines = list(map(clean_inline_comments, file_lines))  # remove spaces
    #all_text = " ".join(file_lines)
    all_text = clean_comments(all_text)

    XML = minidom.getDOMImplementation().createDocument(None, "tokens", None)

    i = 0
    while i < len(all_text):
        tmp_str = all_text[i]
        if tmp_str in symbols:
            append_to_top(XML, "symbol", tmp_str)

        elif tmp_str is '"':
            i = append_string(XML, all_text, i)

        elif tmp_str.isdigit():
            i = append_number(XML, all_text, i, tmp_str)

        elif tmp_str in (' ', '\t'):
            pass

        else:
            i = append_keyword_or_identifier(XML, all_text, i)
        i += 1

    return XML

def tokenize(filename):
    files = []
    debug = False
    xml_files = []
    if filename.endswith(".jack"):
        files.append(filename)
    else:
        files = ([filename + os.sep + file_path
                  for file_path in os.listdir(filename)
                  if file_path.endswith(".jack")])
    for file in files:
        print(file)
        xml_files.append(create_XML(file))

#        if debug:
#            print(xm.documentElement.toprettyxml())
#            with open(file.replace('.jack', '_debug_.xml'), 'w') as f:
#                f.write(xm.documentElement.toprettyxml())
#        else:
#            with open(file.replace('.jack', '.xml'), 'w') as f:
#                f.write(xm.documentElement.toprettyxml())

    return xml_files, files



if __name__ == '__main__':
    debug = False
    if debug:
        print("DEBUG")

    try:
        file_name = sys.argv[1]
    except IndexError:
        print("No input file name")
        exit()
    files = []

    if file_name.endswith(".jack"):
        files.append(file_name)
    else:
        files = ([file_name + os.sep + file_path
                  for file_path in os.listdir(file_name)
                  if file_path.endswith(".jack")])
    for file in files:
        xm = create_XML(file)

        if debug:
            print(xm.documentElement.toprettyxml())
            with open(file.replace('.jack', '_debug_.xml'), 'w') as f:
                f.write(xm.documentElement.toprettyxml())
        else:
            with open(file.replace('.jack', '.xml'), 'w') as f:
                f.write(xm.documentElement.toprettyxml())