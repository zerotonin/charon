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

## Known Issues
 * Folder Structure should be automated in training UtilS

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
    $ conda env create -f charon/charon.yaml 
    $ conda activate charon   
  ```
* Testing the installation
  * Test Tensorflow
  ```
    $ ipython
    import tensorflow as tf    
    tf.__version__  
  ```
  output should be something like '1.15.0'


  * Get tensorflow model zoo from https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/installation.md using this command:
  ```
    $ git clone --single-branch --branch r1.13.0 git@github.com:tensorflow/models.git
  ```
  * Now its time to build protobufs and install the models
  ```
    $ cd /path/to/models/research
    $ protoc object_detection/protos/*.proto --python_out=.
    $ pip install .

  ```
  * Add the object detection scripts to python path
  ```
    $ ipython
    import sys 
    sys.path.append('/path/to/models/research/object_detection')    

* Get the pretrained model from http://download.tensorflow.org/models/object_detection/faster_rcnn_inception_v2_coco_2018_01_28.tar.gz and unpack it in/ path/to/models/research/object_detection
  ```
* Testing with another model
    If you want to be sure that your installation was complete you can test it with a pre made
    model. By using this notebook and directly jumping to the cell with imports! If you run the full
    label IT WILL START IN models/research/object_detection/colab_tutorials/ and therefore it CANNOT load the data. Hence you need to add a os.chdir('/path/to/model') to load example data and import pathlib.  Or you run the third cell!
  ```
    jupyter notebook models/research/object_detection/colab_tutorials/object_detection_tutorial.ipynb 
  ```

* open .bashrc and add following line
  ```
    $ cd  ~
    $ nano .bashrc
  ```
    in file add:
  ```
    export PYTHONPATH="$PYTHONPATH:/home/${YOUR_USERNAME}/models/research/slim"
  ```

* Check the methods in adaptTFconfigFile of training_utils.py
  Because newer versions of the model zoo update there config files you have to check if the line numbers
  in the following functions are still correct:
  * updateLabelNum()
  * updateCheckPoint()
  * updateRecordPosition()
  * updateTestImageNum()


