# -*- coding: utf-8
from StringIO import StringIO
from lxml import etree
import argparse

DTD_FILE = 'resume.dtd'


def main():
    # parse arguments
    arg_parser = argparse.ArgumentParser(description='Parse an XML resumé.')
    arg_parser.add_argument('filename',
                            type=str,
                            help='the name of the resumé XML file')
    args = arg_parser.parse_args()

    # xml file to lxml etree
    filehandle = open(args.filename)
    xmlstring = filehandle.read()
    filehandle.close()
    tree = etree.XML(xmlstring)

    # validate tree
    dtdfile = open(DTD_FILE)
    dtdstring = dtdfile.read()
    dtd = etree.DTD(StringIO(dtdstring))
    is_valid = dtd.validate(tree)
    print is_valid

if __name__ == '__main__':
    main()
