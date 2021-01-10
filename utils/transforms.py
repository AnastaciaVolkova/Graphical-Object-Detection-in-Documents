import cv2


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

        for d in data:
            if d['name'] == 'NoObject':
                break
            d['bndbox'].xmin *= k
            d['bndbox'].ymin *= k
            d['bndbox'].xmax *= k
            d['bndbox'].ymax *= k

        return {'image_file': image, 'data': data}

