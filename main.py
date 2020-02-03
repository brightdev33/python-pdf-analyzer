import sys
import html2text
import re
import csv
import os
import shutil
from subprocess import call

FILENAME = "issue.pdf"

def validStr(str):
    str = re.sub(r"[\**]", "", str)
    str = re.sub(r"^\s*", "", str)
    str = re.sub(r"\s*$", "", str)
    
    s = re.search("Advanced Academic".upper(), str.upper())
    if(s is not None):
       str = re.sub(r"Level II\s*:", "Level III:", str)
       str = re.sub(r"LEVEL II\s*:", "LEVEL III:", str)

    return str


def logicalStr(str):
    str = re.sub(r"[\s|-]", "_", str).upper()
    str = re.sub(r"_*:_*", ": ", str).upper()
    return str


def main():
    filename = FILENAME[:-4]

    # Remove old files.
    if os.path.exists(filename+"-html.html"):
        os.remove(filename+"-html.html")

    # Change pdf into html.
    call(["poppler-0.68.0\\bin\\pdftohtml.exe", filename+".pdf", "-q", "-s", "-i"])
    html = open(filename+"-html.html", encoding="utf8").read()
    text = html2text.html2text(html)

    resList = []

    # Parse file and return extracted data.

    row = []
    offsetStart = 0
    offsetEnd = 0
    physicalName = ""
    fieldLength = 0
    flag = 0
    cnt = 0

    for line in text.split("\n"):
        s = re.search(r"^(\d)+[–|-](\d)+(\s+[0-9]+).*$", line)
        if(s is None):
            s = re.search(r"^(\d)+[–|-](\d)+$", line)

        if(s is not None):

            if(flag != 0):
                if(fieldLength != 0):
                    cnt = cnt + 1
                    row = [cnt, offsetStart, offsetEnd, physicalName,
                        logicalStr(physicalName), fieldLength]
                    resList.append(row)
                    # print(row)

                row = []
                fieldLength = 0
                physicalName = ""

            s = s.group()
            offsetStart = re.search(r"\d+", s).group()
            osLen = len(offsetStart)+1

            offsetEnd = re.search(r"\d+", s[osLen:]).group()
            osLen = osLen + len(offsetEnd) + 1
            flag = 1

            fl = re.search(r"[0-9]+", s[osLen:])
            if(fl is not None):
                fieldLength = validStr(fl.group())
                osLen = osLen + len(fl.group()) + 1
                flag = 2

            fl = re.search(r"[a-zA-Z]+", s[osLen:])
            if(fl is not None):
                physicalName = validStr(s[osLen:])
                flag = 3

        elif(flag == 1 and re.search(r"[0-9]+", line) is not None):
            fieldLength = validStr(re.search(r"[0-9]+", line).group())
            osLen = len(fieldLength) + 1

            fl = re.search(r"[a-zA-Z]+", line[osLen:])
            if(fl is not None):
                physicalName = validStr(fl.group())

            flag = 2
        elif(flag == 2 and re.search(r"[a-zA-Z]+", line) is not None):
            physicalName = validStr(physicalName + " " + line)

            flag = 3

        elif(flag == 3):
            flag = 4

        elif(flag == 4):
            if(re.search(r"\*{2}.+\*{2}", line) is not None and physicalName.upper() != "BLANK"):
                physicalName = validStr(physicalName + " " + line)

            if(fieldLength != 0):
                cnt = cnt + 1
                row = [cnt, offsetStart, offsetEnd, physicalName,
                    logicalStr(physicalName), fieldLength]
                resList.append(row)
                # print(row)
            
            row = []
            fieldLength = 0
            physicalName = ""
            flag = 0

    # Remove temp file.
    if os.path.exists(filename+"-html.html"):
        os.remove(filename+"-html.html")
    if os.path.exists(filename+"s.html"):
        os.remove(filename+"s.html")

    return resList

if __name__ == "__main__":
  res = main()
  sys.exit(res)
