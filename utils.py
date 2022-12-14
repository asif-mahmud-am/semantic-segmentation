import os
from io import BytesIO
import tarfile
import tempfile
import cv2
from six.moves import urllib
from copy import deepcopy
from matplotlib import gridspec
from matplotlib import pyplot as plt
import numpy as np
from PIL import Image
from IPython.display import Image as IMG
import tensorflow as tf

segment_map = None
resized_image = None


class DeepLabModel(object):
  

  INPUT_TENSOR_NAME = 'ImageTensor:0'
  OUTPUT_TENSOR_NAME = 'SemanticPredictions:0'
  
  INPUT_SIZE = 513
  FROZEN_GRAPH_NAME = 'frozen_inference_graph'

  def __init__(self, tarball_path):
    """Creates and loads pretrained deeplab model."""
    self.graph = tf.Graph()

    graph_def = None
    
    tar_file = tarfile.open(tarball_path)
    for tar_info in tar_file.getmembers():
      if self.FROZEN_GRAPH_NAME in os.path.basename(tar_info.name):
        file_handle = tar_file.extractfile(tar_info)
        graph_def = tf.GraphDef.FromString(file_handle.read())
        break

    tar_file.close()

    if graph_def is None:
      raise RuntimeError('Cannot find inference graph in tar archive.')

    with self.graph.as_default():
      tf.import_graph_def(graph_def, name='')

    self.sess = tf.Session(graph=self.graph)

  def run(self, image):
    
    width, height = image.size
    resize_ratio = 1.0 * self.INPUT_SIZE / max(width, height)
    print(width, height)
    print("Resize Ratio - {}".format(resize_ratio))
    target_size = (int(resize_ratio * width), int(resize_ratio * height))
    print(target_size)
    # target_size = (width, height)
    resized_image = image.convert('RGB').resize(target_size, Image.ANTIALIAS)
    batch_seg_map = self.sess.run(
        self.OUTPUT_TENSOR_NAME,
        feed_dict={self.INPUT_TENSOR_NAME: [np.asarray(resized_image)]})
    seg_map = batch_seg_map[0]
    
    return resized_image, seg_map


def create_pascal_label_colormap():
  
  colormap = np.zeros((256, 3), dtype=int)
  ind = np.arange(256, dtype=int)

  for shift in reversed(range(8)):
    for channel in range(3):
      colormap[:, channel] |= ((ind >> channel) & 1) << shift
    ind >>= 3

  return colormap


def label_to_color_image(label):
 
  if label.ndim != 2:
    raise ValueError('Expect 2-D input label')

  colormap = create_pascal_label_colormap()

  if np.max(label) >= len(colormap):
    raise ValueError('label value too large.')

  return colormap[label]


def vis_segmentation(image, seg_map):
  """Visualizes input image, segmentation map and overlay view."""
  plt.figure(figsize=(15, 5))
  grid_spec = gridspec.GridSpec(1, 4, width_ratios=[6, 6, 6, 1])

  plt.subplot(grid_spec[0])
  plt.imshow(image)
  plt.axis('off')
  plt.title('input image')

  plt.subplot(grid_spec[1])
  seg_image = label_to_color_image(seg_map).astype(np.uint8)
  plt.imshow(seg_image)
  plt.axis('off')
  plt.title('segmentation map')

  plt.subplot(grid_spec[2])
  plt.imshow(image)
  plt.imshow(seg_image, alpha=0.7)
  plt.axis('off')
  plt.title('segmentation overlay')

  unique_labels = np.unique(seg_map)
  ax = plt.subplot(grid_spec[3])
  plt.imshow(
      FULL_COLOR_MAP[unique_labels].astype(np.uint8), interpolation='nearest')
  ax.yaxis.tick_right()
  plt.yticks(range(len(unique_labels)), LABEL_NAMES[unique_labels])
  plt.xticks([], [])
  ax.tick_params(width=0.0)
  plt.grid('off')
  #plt.show()
  plt.savefig(os.path.join('static/uploads/', "seg.jpg"))


LABEL_NAMES = np.asarray([
    'background', 'aeroplane', 'bicycle', 'bird', 'boat', 'bottle', 'bus',
    'car', 'cat', 'chair', 'cow', 'diningtable', 'dog', 'horse', 'motorbike',
    'person', 'pottedplant', 'sheep', 'sofa', 'train', 'tv'
])

FULL_LABEL_MAP = np.arange(len(LABEL_NAMES)).reshape(len(LABEL_NAMES), 1)
FULL_COLOR_MAP = label_to_color_image(FULL_LABEL_MAP)


MODEL = DeepLabModel("deeplab_model.tar.gz")
#print(MODEL)
print('model loaded successfully!')

def segmentation_output(img):
      """Inferences DeepLab model and visualizes result."""
      IMAGE_NAME = img
      try:
        original_im = Image.open(IMAGE_NAME)
      except IOError:
        print('Cannot retrieve image. Please check url: ' + url)
        return

      print('running deeplab on image')
      resized_im, seg_map = MODEL.run(original_im)
      vis_segmentation(resized_im, seg_map)
      #cv2.imwrite(os.path.join('static/uploads/', "seg.jpg"), seg_map)
      segment_map = seg_map
      resized_image = resized_im
      return resized_im, seg_map
  
def blur_image(org_img,label_number):
  #resized_img = resized_image 
  seg_map = segment_map
  resized_img = cv2.imread("static/uploads/resize.jpg")
  
  numpy_image = np.array(resized_img) 
  
  object_mapping = deepcopy(numpy_image)
  object_mapping[seg_map==label_number] = 255
  object_mapping[seg_map != label_number] = 0
  original_img = Image.open(org_img)
  original_img = np.array(original_img)
 
  mapping_resized = original_img
  mapping_resized = cv2.resize(object_mapping, (original_img.shape[1], original_img.shape[0]), Image.ANTIALIAS)
  gray = cv2.cvtColor(mapping_resized, cv2.COLOR_BGR2GRAY)
  blurred = cv2.GaussianBlur(gray,(15,15),0)
  ret3,thresholded_img = cv2.threshold(blurred,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
  mapping = cv2.cvtColor(thresholded_img, cv2.COLOR_GRAY2RGB)
  blurred_original_image = cv2.GaussianBlur(original_img,
                                            (251,251), 
                                            0)
  #plt.imshow(blurred_original_image)
  layered_image = np.where(mapping != (0,0,0), 
                          original_img, 
                          blurred_original_image)
  plt.imshow(layered_image)
  im_rgb = cv2.cvtColor(layered_image, cv2.COLOR_BGR2RGB)
  cv2.imwrite("static/uploads/final.jpg", im_rgb)
  #IMG("Potrait_Image.jpg")
  #plt.imshow(layered_image)
  #plt.savefig("static/uploads/final.jpg")
  return 1
