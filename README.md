# AC215 - Milestone2 - SnapNutrition
==============================

Project Organization
<br>
```
├── docker-compose.yml
├── LICENSE
├── notebooks
│   ├── 230922_EDA_of_Nutrition5k_Ben.ipynb
│   ├── FooDD_EDA.ipynb
│   └── Nutrition5k_EDA_Base_Model.ipynb
├── README.md
├── reports
│   └── base_CNN_prediction_example.jpg
└── src
    ├── app
    │   ├── app.py
    │   ├── Dockerfile
    │   ├── Pipfile
    │   ├── Pipfile.lock
    │   ├── static
    │   │   ├── css
    │   │   ├── fonts
    │   │   ├── img
    │   │   └── js
    │   └── templates
    │       ├── layouts
    │       └── pages
    ├── dvc
    │   └── Dockerfile
    └── image_prep
        ├── batch_definitions
        ├── Dockerfile
        ├── image_prep
        │   ├── batch_builder.py
        │   ├── cli.py
        │   ├── function_registry.py
        │   ├── __init__.py
        │   ├── __main__.py
        │   ├── preprocessing_pipeline.py
        │   └── task.py
        ├── pipelines
        ├── Pipfile
        ├── Pipfile.lock
        └── README.md
```

**Team Members**
- Brent Ruttle, [brent.ruttle@gmail.com](brent.ruttle@gmail.com)
- Benjamin Fulroth, [btf355@g.harvard.edu](btf355@g.harvard.edu)
- Deepika Yeramosu, [deepikayeramosu@gmail.com](deepikayeramosu@gmail.com)
- Christina Wang, [wschristina@gmail.com](wschristina@gmail.com)
- Russell Brown, [r.n.brown314@gmail.com](r.n.brown314@gmail.com)

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
This folder contains code that is not part of container - for e.g: EDA, any 🔍 🕵️‍♀️ 🕵️‍♂️ crucial insights, reports or visualizations.

We had the following notebooks for Nutrition5k EDA and Modeling
1. [EDA] 230922_EDA_of_Nutrition5k_Ben.ipynb
2. [EDA + Modeling] Nutrition5k_EDA_Base_Model.ipynb

We had the following notebooks for FooDD dataset: 
1. [EDA] FooDD_EDA.ipynb

The Nutrition5k_EDA_Base_Model.ipynb colab successfully reads images from our team GCS Bucket directly for our base model.
Results from the base CNN on Nutrition5k seem promising so far. One of the best results we noticed from one sample run was: 

![](reports/base_CNN_prediction_example.jpg)

We look forward to more refined results with further exploration.


**Preprocess container**
- This container has code that allows you to define data preprocessing pipelines, and build batches to pad out your image sets.

(1) `src/image_prep/pipelines`
      - This contains yaml files that define preprocessing pipelines. Check src/image_prep/src/function_registry.py to see which functions are available and their parameters.
      - pipelines are referenced later in batch_definition files which are used to actually run the preprocessing

(2) `src/image_prep/batch_definitions`
      - yaml files here are used to define batches. Ex:
```
subsets:
  - "raw_data/FooDD/Apple/1-Samsung-S4-Light Environment/"
  - processed/FooDD/Apple/
  - pipeline_a
  - 100
  - false
```
      - The parameters are, input directory, output directory, pipeline name, n_images, keep_intermediates
      - n_images chooses a random sample of images, seed is specified in `src/image_prep/src/batch_builder.py`
      - keep_intermediates indicates whether intermediate images produced by the pipeline can end up in the batch, or if it should only keep images produced by the last step in the pipeline

(3) To build a batch of processed images, run `docker compose run image_prep python -m src <batch_name>`

(4) Check the examples in the `src/image_prep/pipelines` and `src/image_prep/batch_definitions` folders for the structure of these yaml files. The ending '/' in the paths is important. This main data directory can be configured, but by default it will look for paths within a `data/` folder at the same level as the main project.

**App container**
 - This contains the frontend app that runs in your browser.
 - The frontend is made using Flask and allows user to submit their own food photos and see the model-estimated nutrition info.

**Data version control container**
 - `src/dvc` contains a Dockerfile that installs dvc and also Google Cloud CLI
 - This relies on a `secrets/data-service-account.json` file already existing that has access to the `snapnutrition_data_bucket`
 - the `secrets` folder must be on the same level as the main project, and is not tracked by Git
