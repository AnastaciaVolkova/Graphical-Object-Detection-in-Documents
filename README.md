# Graphical-Object-Detection-in-Documents
Train network for dataset from http://cvit.iiit.ac.in/usodi/iiitar13k.php

## Target
* Train and deploy network for dataset _Graphical Object Detection in Documents_.

## Things to predict
According to utils/get_statistic.py the following things are going to be predicted:
* Type of object ('signature', 'logo', 'table', 'natural_image', 'figure')
* Posisition of the object (xmin, ymin, xmax, ymax)

Parameter "truncated" should be thought.
