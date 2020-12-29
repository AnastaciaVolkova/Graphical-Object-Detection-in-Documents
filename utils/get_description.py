import xml.etree.ElementTree as ET
import sys
import os
from dataclasses import  dataclass

@dataclass
class Rect:
    xmin: int
    ymin: int
    xmax: int
    ymax: int


@dataclass
class DocumentObject:
    name: str
    pose: str
    truncated: bool
    difficult: bool
    bndbox: Rect


def main():
    # Check correctness of command line.
    if len(sys.argv) != 2:
        raise "Wrong command line"

    # Check xml file existence
    file_xml = sys.argv[1]
    if not os.path.exists(file_xml):
        raise "File %s doesn't exist" % file_xml

    # Parse xml and get document object data
    doc_obj_lst = get_documnt_object(file_xml)

    for i in doc_obj_lst:
        print(i)


# Function returns list of document objects datum (DocumentObject), which are contained in current xml.
# file_xml - input xml file to parse
def get_documnt_object(file_xml):
    tree = ET.parse(file_xml)
    root = tree.getroot()

    document_objects = list()
    for obj in root.findall('object'):
        name = obj.find('name').text
        pose = obj.find('pose').text
        truncated = obj.find('truncated').text
        diffucult = obj.find('difficult').text
        bndbox = obj.find('bndbox')
        bndbox_rec = Rect(int(bndbox.find('xmin').text), \
                     int(bndbox.find('ymin').text), \
                     int(bndbox.find('xmax').text), \
                     int(bndbox.find('ymax').text))
        document_objects.append(DocumentObject(name, pose, truncated, diffucult, bndbox_rec))
    return document_objects


if __name__ == "__main__":
    main()
