#!/usr/bin/python
# -*- coding: utf-8 -*-

# Taken from
# http://sujitpal.blogspot.de/2011/11/resume-management-with-xmlresume-
# python.html

# requires odfpy

import getopt
import string
import sys

from xml.etree.ElementTree import parse
from odf.opendocument import OpenDocumentText
from odf.style import FontFace
from odf.style import ListLevelProperties
from odf.style import ParagraphProperties
from odf.style import Style
from odf.style import TextProperties
from odf.text import List
from odf.text import ListItem
from odf.text import ListLevelStyleBullet
from odf.text import ListStyle
from odf.text import P
from odf.text import Span


class ResumeModel:

    def __init__(self):
        self.name = None
        self.address = None
        self.phone = None
        self.email = None
        self.contacts = []
        self.objective_title = None
        self.objectives = []
        self.skillarea_title = None
        self.skillset_titles = []
        self.skillsets = [[]]
        self.jobs_title = None
        self.job_titles = []
        self.job_employers = []
        self.job_periods = []
        self.job_descriptions = []
        self.job_achievements = [[]]
        self.academics_title = None
        self.academics = []
        self.awards_title = None
        self.awards = []

    def to_string(self):
        print "name=", self.name
        print "address=", self.address
        print "phone=", self.phone
        print "email=", self.email
        for contact in self.contacts:
            print "contact=", contact
        print "objective_title", self.objective_title
        for objective in self.objectives:
            print "objective=", objective
        print "skillarea_title=", self.skillarea_title
        for skillset_title in self.skillset_titles:
            print "skillset_title:", skillset_title
        for skillset in self.skillsets:
            print "skillset=", ",".join(skillset)
        print "jobs_title=", self.jobs_title
        for job_title in self.job_titles:
            print "job_title=", job_title
        for job_employer in self.job_employers:
            print "job_employer=", job_employer
        for job_description in self.job_descriptions:
            print "job_description=", job_description
        for job_period in self.job_periods:
            print "job_period=", job_period
        for job_achievement in self.job_achievements:
            for job_achievement_item in job_achievement:
                print "achievement_item=", job_achievement_item
        print "academics_title", self.academics_title
        for academic in self.academics:
            print "academic=", academic
        print "awards_title=", self.awards_title
        for award in self.awards:
            print "award=", award


class XmlResumeParser():

    def __init__(self, input_file, target):
        self.target = target
        self.input = open(input_file, "r")
        self.root = parse(input_file).getroot()
        self.breadcrumb = []
        self.model = ResumeModel()
        self.skillset_idx = -1
        self.job_idx = -1
        self.degree_idx = -1
        self.award_idx = -1

    def close(self):
        self.input.close()

    def parse(self):
        self.parse_r(self.root)

    def parse_r(self, parent):
        if not self.process_target(parent, self.target):
            return
        self.breadcrumb.append(parent.tag)
        self.process_element(parent)
        for child in list(parent):
            self.parse_r(child)
        self.breadcrumb.pop()

    def process_target(self, parent, target):
        target_attr = parent.attrib.get("target")
        if target is None:
            if target_attr is None:
                return True
            else:
                return False
        else:
            if target_attr is None:
                return True
            else:
                if target.find('+') > -1 or target.find(',') > -1:
                    op = "+" if target.find('+') > -1 else ","
                    target_set = set(target.split(op))
                    target_attr_set = set(target_attr.split(op))
                    if target.find('+') > -1:
                        return True if len(target_set.intersection(target_attr_set)) \
                            == len(target_set) else False
                    else:
                        return True if len(target_set.intersection(target_attr_set)) > 0 \
                            else False
                else:
                    return True if target_attr == target else False

    def process_element(self, elem):
        key = "/".join(self.breadcrumb)
        tag = elem.tag
        last_tag = self.breadcrumb[-1:][0]
        if key.startswith("resume/header/name/"):
            self.model.name = self.append(self.model.name, elem.text)
        elif key.startswith("resume/header/address/"):
            if tag == "street":
                self.model.address = elem.text
            elif tag == "city" or tag == "state":
                self.model.address = self.append(
                    self.model.address, elem.text, ", ")
            elif tag == "zip":
                self.model.address = self.append(
                    self.model.address, elem.text, " ")
        elif key.startswith("resume/header/contact/"):
            if tag == "phone":
                self.model.phone = "PHONE: " + elem.text
            elif tag == "email":
                self.model.email = "EMAIL: " + elem.text
            else:
                self.model.contacts.append(string.upper(
                    elem.tag) + ": " + elem.text)
        elif key == "resume/objective":
            self.model.objective_title = self.get_title(elem)
        elif key.startswith("resume/objective/"):
            self.model.objectives.append(elem.text)
        elif key == "resume/skillarea":
            self.model.skillarea_title = self.get_title(elem)
        elif key == "resume/skillarea/skillset":
            self.skillset_idx = self.skillset_idx + 1
            self.model.skillset_titles.append(self.get_title(elem))
            self.model.skillsets.append([])
        elif key == "resume/skillarea/skillset/skill":
            if elem.attrib.get("level") != None:
                self.model.skillsets[self.skillset_idx].append(elem.text +
                                                               " (" + elem.attrib.get("level") + ")")
            else:
                self.model.skillsets[self.skillset_idx].append(elem.text)
        elif key == "resume/history":
            self.model.jobs_title = self.get_title(elem)
        elif key == "resume/history/job":
            self.job_idx = self.job_idx + 1
            self.model.job_achievements.append([])
        elif key.startswith("resume/history/job/"):
            if tag == "jobtitle":
                self.model.job_titles.append(elem.text)
            elif tag == "employer":
                self.model.job_employers.append(elem.text)
            elif tag == "from":
                if len(list(elem)) == 1:
                    date_from = self.format_date(list(elem)[0])
                    self.model.job_employers[self.job_idx] = \
                        self.model.job_employers[
                            self.job_idx] + " (" + date_from
            elif tag == "to":
                if len(list(elem)) == 1:
                    date_to = self.format_date(list(elem)[0])
                    self.model.job_employers[self.job_idx] = \
                        self.model.job_employers[
                            self.job_idx] + " - " + date_to + ")"
            elif tag == "description":
                self.model.job_descriptions.append(elem.text)
            elif tag == "achievement":
                self.model.job_achievements[self.job_idx].append(elem.text)
        elif key == "resume/academics":
            self.model.academics_title = self.get_title(elem)
        elif key == "resume/academics/degrees/degree":
            self.degree_idx = self.degree_idx + 1
            self.model.academics.append([])
        elif key.startswith("resume/academics/degrees/degree/"):
            if tag == "level":
                self.model.academics[self.degree_idx] = elem.text
            elif tag == "major":
                self.model.academics[self.degree_idx] = \
                    self.model.academics[self.degree_idx] + ", " + elem.text
            elif tag == "institution":
                self.model.academics[self.degree_idx] = \
                    self.model.academics[
                        self.degree_idx] + " from " + elem.text
            elif tag == "from":
                if len(list(elem) == 1):
                    from_date = self.format_date(list(elem)[0])
                    self.model.academics[self.degree_idx] = \
                        self.model.academics[
                            self.degree_idx] + " (" + elem.text
            elif tag == "to":
                if len(list(elem) == 1):
                    to_date = self.format_date(list(elem)[0])
                    self.model.academics[self.degree_idx] = \
                        self.model.academics[
                            self.degree_idx] + " - " + elem.text + ")"
        elif key == "resume/awards":
            self.model.awards_title = self.get_title(elem)
        elif key == "resume/awards/award":
            self.award_idx = self.award_idx + 1
            self.model.awards.append([])
        elif key.startswith("resume/awards/award/"):
            if tag == "title":
                self.model.awards[self.award_idx] = elem.text
            elif tag == "organization":
                self.model.awards[self.award_idx] = \
                    self.model.awards[self.award_idx] + " from " + elem.text
            elif tag == "date":
                award_date = self.format_date(elem)
                self.model.awards[self.award_idx] = \
                    self.model.awards[self.award_idx] + " (" + award_date + ")"

    def format_date(self, elem):
        if elem.tag != "date":
            return elem.tag
        dmy = ["", "", ""]
        for child in list(elem):
            if child.tag == "day":
                dmy[0] = child.text
            elif child.tag == "month":
                dmy[1] = child.text
            elif child.tag == "year":
                dmy[2] = child.text
            else:
                continue
        filtered_dmy = filter(lambda e: len(e) > 0, dmy)
        if len(filtered_dmy) > 0:
            return " ".join(filtered_dmy)

    def get_title(self, elem):
        title = elem.attrib.get("title")
        if title is None:
            return string.upper(elem.tag)
        else:
            return title

    def append(self, buf, strg, sep=" "):
        if strg == None:
            strg = ""
        if buf == None:
            buf = strg
        else:
            buf = buf + sep + strg
        return buf


class TextResumeWriter():

    def __init__(self, filename):
        self.file = open(filename, 'w')

    def write(self, model):
        self.writeln(model.name)
        self.writeln(model.address)
        self.writeln(", ".join([model.phone, model.email]))
        self.writeln(", ".join(model.contacts))
        self.writeln("-" * 80)
        self.writeln(model.objective_title)
        self.writeln()
        self.writeln("\n".join(model.objectives))
        self.writeln("-" * 80)
        self.writeln(model.skillarea_title)
        self.writeln()
        for i in range(0, len(model.skillset_titles)):
            self.writeln(model.skillset_titles[
                         i] + ": " + ",".join(model.skillsets[i]))
        self.writeln("-" * 80)
        self.writeln(model.jobs_title)
        for i in range(0, len(model.job_titles)):
            self.writeln()
            self.writeln(model.job_titles[i])
            self.writeln(model.job_employers[i])
            self.writeln(model.job_descriptions[i])
            for achievement in model.job_achievements[i]:
                self.writeln("* " + achievement)
        self.writeln("-" * 80)
        self.writeln(model.academics_title)
        self.writeln()
        for academic in model.academics:
            self.writeln("* " + academic)
        self.writeln("-" * 80)
        self.writeln(model.awards_title)
        self.writeln()
        for award in model.awards:
            self.writeln("* " + award)

    def writeln(self, s=None):
        if s != None:
            self.file.write(s)
        self.file.write("\n")

    def close(self):
        self.file.close()


class OdfResumeWriter():

    def __init__(self, filename):
        self.filename = filename
        self.doc = OpenDocumentText()
        # font
        self.doc.fontfacedecls.addElement((FontFace(name="Arial",
                                                    fontfamily="Arial", fontsize="10", fontpitch="variable",
                                                    fontfamilygeneric="swiss")))
        # styles
        style_standard = Style(name="Standard", family="paragraph",
                               attributes={"class": "text"})
        style_standard.addElement(
            ParagraphProperties(punctuationwrap="hanging",
                                writingmode="page", linebreak="strict"))
        style_standard.addElement(TextProperties(fontname="Arial",
                                                 fontsize="10pt", fontsizecomplex="10pt", fontsizeasian="10pt"))
        self.doc.styles.addElement(style_standard)
        # automatic styles
        style_normal = Style(name="ResumeText", parentstylename="Standard",
                             family="paragraph")
        self.doc.automaticstyles.addElement(style_normal)

        style_bold_text = Style(
            name="ResumeBoldText", parentstylename="Standard",
            family="text")
        style_bold_text.addElement(TextProperties(fontweight="bold",
                                                  fontweightasian="bold", fontweightcomplex="bold"))
        self.doc.automaticstyles.addElement(style_bold_text)

        style_list_text = ListStyle(name="ResumeListText")
        style_list_bullet = ListLevelStyleBullet(level="1",
                                                 stylename="ResumeListTextBullet", numsuffix=".", bulletchar=u'\u2022')
        style_list_bullet.addElement(ListLevelProperties(spacebefore="0.1in",
                                                         minlabelwidth="0.2in"))
        style_list_text.addElement(style_list_bullet)
        self.doc.automaticstyles.addElement(style_list_text)

        style_bold_para = Style(name="ResumeH2", parentstylename="Standard",
                                family="paragraph")
        style_bold_para.addElement(TextProperties(fontweight="bold",
                                                  fontweightasian="bold", fontweightcomplex="bold"))
        self.doc.automaticstyles.addElement(style_bold_para)

        style_bold_center = Style(name="ResumeH1", parentstylename="Standard",
                                  family="paragraph")
        style_bold_center.addElement(TextProperties(fontweight="bold",
                                                    fontweightasian="bold", fontweightcomplex="bold"))
        style_bold_center.addElement(ParagraphProperties(textalign="center"))
        self.doc.automaticstyles.addElement(style_bold_center)

    def write(self, model):
        self.doc.text.addElement(P(text=model.name, stylename="ResumeH1"))
        self.doc.text.addElement(P(text=model.address, stylename="ResumeH1"))
        self.doc.text.addElement(P(text=", ".join([model.phone, model.email]),
                                   stylename="ResumeH1"))
        for contact in model.contacts:
            self.doc.text.addElement(P(text=contact, stylename="ResumeH1"))
        self.nl()
        self.doc.text.addElement(P(text=model.objective_title,
                                   stylename="ResumeH1"))
        self.nl()
        for objective in model.objectives:
            self.doc.text.addElement(P(text=objective, stylename="ResumeText"))
        self.nl()
        self.doc.text.addElement(P(text=model.skillarea_title,
                                   stylename="ResumeH1"))
        self.nl()
        for i in range(0, len(model.skillset_titles)):
            skillset_line = P(text="")
            skillset_line.addElement(Span(text=model.skillset_titles[i],
                                          stylename="ResumeBoldText"))
            skillset_line.addElement(Span(
                text=": ", stylename="ResumeBoldText"))
            skillset_line.addText(", ".join(model.skillsets[i]))
            self.doc.text.addElement(skillset_line)
        self.nl()
        self.doc.text.addElement(P(
            text=model.jobs_title, stylename="ResumeH1"))
        for i in range(0, len(model.job_titles)):
            self.nl()
            self.doc.text.addElement(P(text=model.job_titles[i],
                                       stylename="ResumeH2"))
            self.doc.text.addElement(P(text=model.job_employers[i],
                                       stylename="ResumeH2"))
            self.doc.text.addElement(P(text=model.job_descriptions[i],
                                       stylename="ResumeText"))
            achievements_list = List(stylename="ResumeTextList")
            for achievement in model.job_achievements[i]:
                achievements_listitem = ListItem()
                achievements_listitem.addElement(P(text=achievement,
                                                   stylename="ResumeText"))
                achievements_list.addElement(achievements_listitem)
            self.doc.text.addElement(achievements_list)
        self.nl()
        self.doc.text.addElement(P(text=model.academics_title,
                                   stylename="ResumeH1"))
        academics_list = List(stylename="ResumeTextList")
        for academic in model.academics:
            academics_listitem = ListItem()
            academics_listitem.addElement(P(
                text=academic, stylename="ResumeText"))
            academics_list.addElement(academics_listitem)
        self.doc.text.addElement(academics_list)
        self.nl()
        self.doc.text.addElement(P(
            text=model.awards_title, stylename="ResumeH1"))
        awards_list = List(stylename="ResumeTextList")
        for award in model.awards:
            awards_listitem = ListItem()
            awards_listitem.addElement(P(text=award, stylename="ResumeText"))
            awards_list.addElement(awards_listitem)
        self.doc.text.addElement(awards_list)
        self.nl()

    def nl(self):
        self.doc.text.addElement(P(text="\n", stylename="ResumeText"))

    def close(self):
        self.doc.save(self.filename)


def usage(msg=None):
    if msg:
        print "ERROR: %s" % (msg)
    print "Usage: %s -i input.xml -o output_file [-t target]" % (sys.argv[0])
    print "OPTIONS:"
    print "-i | --input    : input resume.xml file"
    print "-o | --output : output file name. Suffix dictates output format"
    print "                            : supported formats (txt, odt)"
    print "-t | --target : filters elements for target if specified"
    print "                            : (optional, default is None)"
    print "-h | --help     : print this message"
    sys.exit(2)


def get_writer(output):
    output_format = output.split(".")[-1:][0]
    if output_format == "txt":
        return TextResumeWriter(output)
    elif output_format == "odt":
        return OdfResumeWriter(output)
    else:
        return None


def main():
    try:
        (opts, args) = getopt.getopt(sys.argv[1:], "i:o:t:h",
                                     ["input", "output", "target", "help"])
    except:
        usage()
    if len(opts) == 0:
        usage()
    target = None
    for opt in opts:
        (key, value) = opt
        if key in ("-h", "--help"):
            usage()
        elif key in ("-i", "--input"):
            input = value
        elif key in ("-o", "--output"):
            output = value
        elif key in ("-t", "--target"):
            target = value
    if input is None or output is None:
        usage("Input and Output is mandatory")
    writer = get_writer(output)
    if writer is None:
        usage("Unsupported output format")
    parser = XmlResumeParser(input, target)
    parser.parse()
    writer.write(parser.model)
    parser.close()
    writer.close()

if __name__ == "__main__":
    main()
