# charon - *C*ell *H*e*A*lth *R*ecogniti*O*n *N*etwork
Charon is a python library that is based on TensorFlow. It uses small neuronal networks to recognise the viability of cells in DAPI coloured images of cell cultures.

The general idea is that experts classify viability of single cells in images of cell culture. This is most often done with two categories (alive & dead), but can be increased into more categories (e.g. healthy dying dead etc.). The neuronal network is based on the tensorFlow object recognition model and than trained to recognise the different cell categories. Once this is done and a sufficient detection precission is achieved the system can trace any number of images.

To facilitate usage with researchers that have limited background in computer science charon offers the possibility to rrun it through a web-server system.

## Installation

1.  CUDA 
2.  cudNN 
3.  tensorFlow 
4.  tensorFlowModels
5.  labelImg
6.  nginx


## Process
1.  label Images
2.  Pick suitable interference graph / network
3.  train
4.  refine
5.  train
6.  use

## Server Usage
 ???

## Install on Ubuntu 20.04

* Get current Nvidia driver for GPU
* Install Anaconda 
  * Download from https://www.anaconda.com/
  ```
    $ bash Anaconda3-2020.02-Linux-x86_64.sh 
  ```
* Create new environment and activate it
  ```
    $ conda create --name tf python=3.7
    $ conda activate tf
  ```
* Installing conda packages 
  ```
    $ conda update -n base -c defaults conda
    $ conda install ipython
    $ conda install pandas
    $ conda install -c conda-forge opencv
    $ conda install numpy
    $ conda install scipy
    $ conda install tensorflow-gpu
    $ conda install -c anaconda protobuf

  ```
* Installing/Updating pip
  ```
    $ python -m pip install --upgrade pip
  ```
* Installing Pip packages 
  ```
    $ pip install pillow
    $ pip install lxml
    $ pip install contextlib2
    $ pip install jupyter
    $ pip install matplotlib
    $ pip install pandas
    $ pip install opencv-python
    $ pip install --user pycocotools
    ???? pip3 install model-zoo
  ```
  * Get tensorflow model zoo from https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/installation.md using this command:
  ```
    $ git clone https://github.com/tensorflow/models.git
  ```
  * Now its time to build protobufs and install the models
  ```
      $ cd /path/to/models/research
      $ protoc --python_out=. .\object_detection\protos\anchor_generator.proto .\object_detection\protos\argmax_matcher.proto .\object_detection\protos\bipartite_matcher.proto .\object_detection\protos\box_coder.proto .\object_detection\protos\box_predictor.proto .\object_detection\protos\eval.proto .\object_detection\protos\faster_rcnn.proto .\object_detection\protos\faster_rcnn_box_coder.proto .\object_detection\protos\grid_anchor_generator.proto .\object_detection\protos\hyperparams.proto .\object_detection\protos\image_resizer.proto .\object_detection\protos\input_reader.proto .\object_detection\protos\losses.proto .\object_detection\protos\matcher.proto .\object_detection\protos\mean_stddev_box_coder.proto .\object_detection\protos\model.proto .\object_detection\protos\optimizer.proto .\object_detection\protos\pipeline.proto .\object_detection\protos\post_processing.proto .\object_detection\protos\preprocessor.proto .\object_detection\protos\region_similarity_calculator.proto .\object_detection\protos\square_box_coder.proto .\object_detection\protos\ssd.proto .\object_detection\protos\ssd_anchor_generator.proto .\object_detection\protos\string_int_label_map.proto .\object_detection\protos\train.proto .\object_detection\protos\keypoint_box_coder.proto .\object_detection\protos\multiscale_anchor_generator.proto .\object_detection\protos\graph_rewriter.proto .\object_detection\protos\calibration.proto .\object_detection\protos\flexible_grid_anchor_generator.proto
      $ python setup.py build
      $ python setup.py install

  ```





