import os
import argparse
import numpy as np
from matplotlib import pyplot as plt
from paz.datasets import FERPlus
from paz.backend.image import show_image, resize_image, make_mosaic

from pipelines import CalculateEigenFaces, PostrocessEigenFace
from pipelines import CalculateFaceWeights
from processors import PlotEmbeddings, ExtractFaces

description = 'Eigenfaces algorithm on pure numpy'
data_path = os.path.join(os.path.expanduser('~'), '.keras/paz/datasets/')
data_path = os.path.join(data_path, 'FERPlus')
parser = argparse.ArgumentParser(description=description)
parser.add_argument('-p', '--data_path', type=str,
                    default=data_path, help='Default root data path')
parser.add_argument('-tr', '--train_split', type=str, default='train',
                    help='Split for training data')
parser.add_argument('-v', '--total_variance', type=float, default=0.95,
                    help='Total variance for selecting number of eigenfaces')
args = parser.parse_args()

# extract dataset
data_manager = FERPlus(args.data_path, args.train_split)
data = data_manager.load_data()
faces = ExtractFaces()(data)

# calculate eigenfaces
calculate_eigenfaces = CalculateEigenFaces(args.total_variance)
eigenvalues, eigenfaces, mean_face = calculate_eigenfaces(faces)

# plot eigenvalues
show_image(mean_face.astype('uint8'))
plt.plot(eigenvalues[:30])
plt.show()

# plot post-processed eigenfaces
postprocess = PostrocessEigenFace(shape=(48, 48))
postprocessed_eigenfaces = np.zeros((len(eigenfaces), 48, 48, 1))
for arg, eigenface in enumerate(eigenfaces):
    postprocessed_eigenfaces[arg, :, :, 0] = postprocess(eigenface)
mosaic = make_mosaic(postprocessed_eigenfaces[:80], (10, 8))
show_image(mosaic)

# project new images to eigenspace
faces, num_projected_faces = np.expand_dims(np.moveaxis(faces, -1, 0), -1), 100
project = CalculateFaceWeights(eigenfaces, mean_face, with_crop=False)
images, weights = [], np.zeros((num_projected_faces, len(eigenvalues)))
for face_arg, face in enumerate(faces[:num_projected_faces]):
    images.append(resize_image(face, (20, 20)).astype('uint8'))
    weights[face_arg, :] = project(face)

# plot embeddings
plot = PlotEmbeddings(epsilon=0)
plot(weights[:, :2], images)
plt.show()
