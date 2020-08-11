import io
import os
from PIL import Image
import shutil

from yolo_labels.yolo_v3_to_v5 import YoloV5DatasetType


class V3ToV5Converter:
    def __init__(
            self,
            input_file: str,
            images_dir: str,
            output_dir: str,
            dataset_type: YoloV5DatasetType
    ):
        self.input_file = input_file
        self.images_dir = images_dir
        self.output_dir = output_dir
        self.dataset_type = dataset_type.value
        self.output_img_dir = None
        self.output_labels_dir = None

    def __call__(self):
        self.create_dirs()
        with io.open(self.input_file, 'r') as input_file:
            for line in input_file.readlines():
                self.write_v5_annotations(line)

    def write_v5_annotations(self, line: str):
        image, *objects = line.split(' ')
        annotations = self.generate_annotations(image, objects)
        output_filename = '{}.txt'.format(os.path.splitext(image)[0])
        with io.open(os.path.join(self.output_labels_dir, output_filename), 'w+') as output_file:
            output_file.write(annotations)
        self.copy_image_file(image)

    def generate_annotations(self, image, objects: list):
        annotations = ''
        for obj in objects:  # type: str
            obj = obj.strip()
            if obj == '':
                continue
            annotations += self.stringify_object_data(image, obj)

        return annotations

    def stringify_object_data(self, image, obj: str) -> str:
        *bbox, label_id = obj.strip().split(',')
        normalized_bbox = self.normalize_bbox(image, bbox)
        annotation_list = [label_id] + normalized_bbox
        annotation_list = [str(item) for item in annotation_list]

        return ' '.join(annotation_list) + '\n'

    def normalize_bbox(self, image_filename: str, bbox: list):
        image = Image.open(os.path.join(self.images_dir, image_filename))  # type: Image.Image
        height, width = image.size
        float_bbox = [float(item) for item in bbox]

        return [float_bbox[0]/width, float_bbox[1]/height, float_bbox[2]/width, float_bbox[3]/height]

    def create_dirs(self):
        os.mkdir(os.path.join(self.output_dir, self.dataset_type))
        self.output_img_dir = os.path.join(self.output_dir, self.dataset_type, 'images')
        os.mkdir(self.output_img_dir)
        self.output_labels_dir = os.path.join(self.output_dir, self.dataset_type, 'labels')
        os.mkdir(self.output_labels_dir)

    def copy_image_file(self, image):
        shutil.copy2(
            os.path.join(self.images_dir, image),
            os.path.join(self.output_img_dir, image)
        )