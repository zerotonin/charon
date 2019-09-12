# **charon** - **C**ell **H**e**A**lth **R**ecogniti**O**n **N**etwork

Charon is a python library that is based on TensorFlow. It uses small neuronal networks to recognise the viability of cells in DAPI coloured images of cell cultures.
The general idea is that experts classify viability of single cells in images of cell culture. This is most often done with two categories (alive & dead), but can be increased into more categories (e.g. healthy dying dead etc.). The neuronal network is based on the tensorFlow object recognition model and than trained to recognise the different cell categories. Once this is done and a sufficient detection precission is achieved the system can trace any number of images.
To facilitate usage with researchers that have limited background in computer science charon offers the possibility to rrun it through a web-server system.


