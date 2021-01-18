import sys
import os
import cv2
import random
import get_description
import transforms
from matplotlib import pyplot as plt
import matplotlib.patches as patches
import torch
from matplotlib.pyplot import cm
import numpy as np


# Returns train or test data: path to image file and objects boundaries and their names
class DocObjDataSet:
    image_size = 512
    cropped_size = 256
    class_map = {
        'figure': 0,
        'logo': 1,
        'table': 2,
        'signature': 3,
        'natural_image': 4
    }

    def __init__(self, image_directory, xml_directory, to_transform=True):
        self.xml_files = [os.path.join(xml_directory, f) for f in os.listdir(xml_directory)
                          if os.path.exists(os.path.join(xml_directory, f)) and os.path.splitext(f)[-1] == ".xml"]
        self.image_directory = image_directory
        self.file_id = 0
        self.device = torch.device('cuda')
        self.to_transform = to_transform

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
        data4net = {'image_file': image,
                    'data': {
                        'boxes': torch.zeros((len(objs['objects']), 4), dtype=torch.float32, device=self.device),
                        'labels': torch.zeros((len(objs['objects'])), dtype=torch.int64, device=self.device)}}

        # Save all objects in current xml file.
        for i, obj in enumerate(objs['objects']):
            data4net['data']['labels'][i] = DocObjDataSet.class_map[obj.name]
            c = np.array([obj.bndbox.xmin, obj.bndbox.ymin, obj.bndbox.xmax, obj.bndbox.ymax])
            data4net['data']['boxes'][i] = torch.from_numpy(c)

        if self.to_transform:
            trans = [transforms.ToNormGreyFloat(),
                     transforms.Resize(DocObjDataSet.image_size),
                     transforms.Crop((DocObjDataSet.cropped_size, DocObjDataSet.cropped_size))]

            for t in trans:
                data4net = t(data4net)

        data4net['image_file'] = torch.tensor(data4net['image_file'], device=self.device, dtype=torch.float32)
        data4net['image_file'] = torch.unsqueeze(data4net['image_file'], 0)
        return data4net

    @staticmethod
    def collate(x):
        image, targets = zip(*[d.values() for d in x])
        return {'image': image, 'target': targets}


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

    data_set = DocObjDataSet(image_directory, data_directory)
    # idx = random.randint(0, 9333)
    idx = 0
    item = data_set[idx]
    fig, ax = plt.subplots(1)
    ax.imshow(item['image_file'].cpu().squeeze(0).numpy(), cmap='gray')
    color = iter(cm.rainbow(np.linspace(0, 1, item['data']['boxes'].shape[0])))

    for obj_boxes in item['data']['boxes']:
        ax.add_patch(
            patches.Rectangle(obj_boxes[0:2],
                              obj_boxes[2]-obj_boxes[0],
                              obj_boxes[3]-obj_boxes[1],
                              linewidth=1, edgecolor=next(color), facecolor='none'))
    plt.show()


if __name__ == "__main__":
    main()
