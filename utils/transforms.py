import cv2
import random
import torch


class ToNormGreyFloat:
    def __call__(self, data4net):
        image, data = data4net['image_file'], data4net['data']
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = image/255.0
        return {'image_file': image, 'data': data}


class Resize:
    def __init__(self, scale):
        self.scale = scale

    def __call__(self, data4net):
        image, data = data4net['image_file'], data4net['data']

        # Maximum size of image should be equal to scale.
        h = image.shape[0]
        w = image.shape[1]

        k = float(self.scale) / max(w, h)

        if w > h:
            h = float(h) * k
            w = self.scale
        else:
            w = float(w) * k
            h = self.scale
        image = cv2.resize(image, (int(w), int(h)))

        data['boxes'] *= k

        return {'image_file': image, 'data': data}


class Crop:
    def __init__(self, cropped_size):
        self.cropped_size = cropped_size

    def __call__(self, data4net):
        image, data = data4net['image_file'], data4net['data']

        # Generate random shift.
        shift_x = random.randint(0, image.shape[1] - self.cropped_size[1])
        shift_y = random.randint(0, image.shape[0] - self.cropped_size[0])

        # Crop image. Shift is defined randomly.
        image = image[shift_y:shift_y+self.cropped_size[0], shift_x:shift_x+self.cropped_size[1]]

        # Shift rectangle.
        for d in data['boxes']:
            d -= torch.tensor([shift_x, shift_y, shift_x, shift_y])

        return {'image_file': image, 'data': data}
