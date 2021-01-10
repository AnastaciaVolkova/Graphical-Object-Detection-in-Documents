import sys
import os
import cv2
import random
import get_description
from get_description import Rect
import transforms
from matplotlib import pyplot as plt


# Returns train or test data: path to image file and objects boundaries and their names
class DocObjDataSet:
    max_objs_num = 64
    image_size = 512

    def __init__(self, image_directory, xml_directory):
        self.xml_files = [os.path.join(xml_directory, f) for f in os.listdir(xml_directory)
                          if os.path.exists(os.path.join(xml_directory, f)) and os.path.splitext(f)[-1] == ".xml"]
        self.image_directory = image_directory
        self.file_id = 0

    def __iter__(self):
        self.file_id = 0
        return self

    def __next__(self):
        if self.file_id < len(self.xml_files):
            obj = self.getitem(self.file_id)
            self.file_id += 1
            return obj
        else:
            raise StopIteration

    def __getitem__(self, item):
        return self.getitem(item)

    def __len__(self):
        return len(self.xml_files)

    def getitem(self, idx):
        # Get objects, which are described in current xml document.
        objs = get_description.get_documnt_objects(self.xml_files[idx])

        # Check if image file exists.
        file_name = os.path.join(self.image_directory, objs['filename'])
        if not os.path.exists(file_name):
            raise "File %s doesn't exist" % file_name

        image = cv2.imread(file_name)
        # Data for net: image file and its objects names and their bounds.
        data4net = {'image_file': image, 'data': [None] * DocObjDataSet.max_objs_num}

        # Save all objects in current xml file.
        for i, obj in enumerate(objs['objects']):
            if i >= DocObjDataSet.max_objs_num:
                raise "Number of objects in file exceeds the maximum number"
            data4net['data'][i] = {}
            data4net['data'][i]['name'] = obj.name
            data4net['data'][i]['bndbox'] = obj.bndbox

        for i in range(len(objs['objects']), DocObjDataSet.max_objs_num):
            data4net['data'][i] = {}
            data4net['data'][i]['name'] = 'NoObject'
            data4net['data'][i]['bndbox'] = Rect(0, 0, 0, 0)

        trans = [transforms.ToNormGreyFloat(), transforms.Resize(DocObjDataSet.image_size)]
        for t in trans:
            data4net = t(data4net)

        return data4net


def main():
    if len(sys.argv) != 3:
        raise "Invalid command line"

    if not os.path.exists(sys.argv[1]):
        raise "Directory doesn't exist"

    if sys.argv[2] not in ["training", "test"]:
        raise "Invalid type of data"

    image_directory = os.path.join(sys.argv[1], sys.argv[2] + "_images")

    if not os.path.exists(image_directory):
        raise "Image directory doesn't exist"

    data_directory = os.path.join(sys.argv[1], sys.argv[2] + "_xml")

    if not os.path.exists(data_directory):
        raise "Xml directory doesn't exist"

    data_loader = DocObjDataSet(image_directory, data_directory)
    idx = random.randint(0, 9333)
    plt.imshow(data_loader[idx]['image_file'], cmap='gray')
    for d in data_loader[idx]['data']:
        if d['name'] == 'NoObject':
            break
        print(d['name'])
        plt.plot(
            [d['bndbox'].xmin, d['bndbox'].xmin, d['bndbox'].xmax, d['bndbox'].xmax],
            [d['bndbox'].ymin, d['bndbox'].ymax, d['bndbox'].ymax, d['bndbox'].ymin],
            '*')
    plt.show()
    pass
    '''
    for i, obj in enumerate(data_loader):
        if i%100 == 0:
            print(i)
            print(obj)
    '''


if __name__ == "__main__":
    main()
