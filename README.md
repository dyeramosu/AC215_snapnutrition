# AC215 - Milestone2 - SnapNutrition
==============================

Project Organization
<br>
`Need to update structure (Ben)`
------------
      ├── LICENSE
      ├── README.md
      ├── notebooks
      ├── references
      ├── requirements.txt
      ├── setup.py
      └── src
            ├── preprocessing
            │   ├── Dockerfile
            │   ├── preprocess.py
            │   └── requirements.txt
            └── validation
                  ├── Dockerfile
                  ├── cv_val.py
                  └── requirements.txt


--------

**Team Members**
- Brent Ruttle, [brent.ruttle@gmail.com](brent.ruttle@gmail.com)
- Benjamin Fulroth, [btf355@g.harvard.edu](btf355@g.harvard.edu)
- Deepika Yeramosu, [deepikayeramosu@gmail.com](deepikayeramosu@gmail.com)
- Christina Wang, [wschristina@gmail.com](wschristina@gmail.com)
- Russel Brown, [r.n.brown314@gmail.com](r.n.brown314@gmail.com)

**Group Name**
SnapNutrition

**Project**
In this project we aim to develop an application that can estimate calories and macronutrients of food from user submitted photos of food using computer vision.

### Milestone2 ###

**Datasets**

We focused our efforts on the exploration and processing of two very different datasets containing images of food.

1. The first dataset named `Nutrition 5K` consists of 180GB of images and videos of food.  As this dataset is so large we narrowed our focus to only images taken directly above a plate of food.  In addition, we anticipate that this dataset will be more difficult to develop a predictive model as it consists of entire dishes with multiple foods and ingredients.  That said, we have begun initial model development and results are promising.
2. The second dataset is named `FooDD` and consists of images of single foods (apples, bread, etc.) but not all images are the same size which presents a challenge during initial preprocessing.  This challenge is being addressed in our preprocessing container below.

**Notebooks**

We had the following notebooks for Nutrition5k EDA and Modeling
1. [EDA] 230922_EDA_of_Nutrition5k_Ben.ipynb
2. [EDA + Modeling] Nutrition5k_EDA_Base_Model.ipynb

We had the following notebooks for FooDD dataset: 
1. [EDA] FooDD_EDA.ipynb

The Nutrition5k_EDA_Base_Model.ipynb colab successfully reads images from our team GCS Bucket directly for our base model.
Results from the base CNN on Nutrition5k seem promising so far. One of the best results we noticed from one sample run was: 

![](reports/base_CNN_prediction_example.jpg)

We look forward to more refined results with further exploration.

`Stopped editing here.. (Christina)`

**Preprocess container**
- This container reads 100GB of data and resizes the image sizes and stores it back to GCP
- Input to this container is source and destincation GCS location, parameters for resizing, secrets needed - via docker
- Output from this container stored at GCS location

(1) `src/preprocessing/preprocess.py`  - Here we do preprocessing on our dataset of 100GB, we reduce the image sizes (a parameter that can be changed later) to 128x128 for faster iteration with our process. Now we have dataset at 10GB and saved on GCS. 

(2) `src/preprocessing/requirements.txt` - We used following packages to help us preprocess here - `special butterfly package` 

(3) `src/preprocessing/Dockerfile` - This dockerfile starts with  `python:3.8-slim-buster`. This <statement> attaches volume to the docker container and also uses secrets (not to be stored on GitHub) to connect to GCS.

To run Dockerfile - `Instructions here`

**Cross validation, Data Versioning**
- This container reads preprocessed dataset and creates validation split and uses dvc for versioning.
- Input to this container is source GCS location, parameters if any, secrets needed - via docker
- Output is flat file with cross validation splits
  
(1) `src/validation/cv_val.py` - Since our dataset is quite large we decided to stratify based on species and kept 80% for training and 20% for validation. Our metrics will be monitored on this 20% validation set. 

(2) `requirements.txt` - We used following packages to help us with cross validation here - `iterative-stratification` 

(3) `src/validation/Dockerfile` - This dockerfile starts with  `python:3.8-slim-buster`. This <statement> attaches volume to the docker container and also uses secrets (not to be stored on GitHub) to connect to GCS.

To run Dockerfile - `Instructions here`

**Notebooks** 
This folder contains code that is not part of container - for e.g: EDA, any 🔍 🕵️‍♀️ 🕵️‍♂️ crucial insights, reports or visualizations.
