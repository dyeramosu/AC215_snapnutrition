# AC215 - Milestone3 - SnapNutrition

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

## Milestone3

### **Main Objectives for Milestone**

The main objectives for our project on this milestone:

1. Build a comprehensive containerized data pipeline with extraction, transformation, and dataset versioning capabilities.
2. Implement distributed computing using Dask as well as integrate Cloud Storage using Googles Cloud Storage options.
3. Scale up our model training by developing a containerized training workflow that uses Google's Vertex AI platform for serverless training, Weights and Biases for model metric tracking, and Google cloud storage to store models for inference. 

### **Datasets**

Our main dataset is named `Nutrition 5K` where we focus on overhead images of food dishes and corresponding labels of total_calories, total_mass, total_fat, total_carb, total_protein.

### **Architecture Diagram**

![](block_diagram.drawio.svg)
**Note:** the diagram above includes a depiction of an inference container. We have the set-up for incorporating a 
future inference container, but it is not an objective for this milestone and thus not included at this time.

### **Notebooks**

The [highlight notebook](./notebooks/classification_models_wandb_deepika.ipynb) for this milestone shows how we use **dask** to 
compute image metrics and preprocess the image (re-sizing, etc.). This notebook additionally trains on a couple model types including 
MobileNet for transfer learning. Finally, it also connects to **weights and biases** for training output metrics tracking.

These notebook components were also containerized in this project into several containers for preprocessing, dataset-splitting,
TFRecords creation, and model training on Vertex.

- All project Jupyter notebooks and dataset EDA [here](./notebooks)
- Weights and Biases product page [here](https://wandb.ai/site)
- Vertex AI product page [here](https://cloud.google.com/vertex-ai?hl=en)

### **Containers**

We built the following containers for our project:

1) [Data Versioning Control](./data_versioning_control)
2) [Data Labels Processing and Train, Test, Validation Split](./data_labels_processing)
3) [TFRecords Creation](./tfrecords_creation)
4) [Model Training](./model-training)
5) [App Frontend Container:](./src/app) Note that this container will be used later in our project.
6) [Image Processing](./src/image_prep) Note: Multiple processing options including data augmentation.

**Data Version Control Container**
 - This container is meant to run in a Google Cloud VM and reads from our Google Cloud Storage Bucket.
 - We use an open source tool called DVC (product page [here](https://dvc.org/doc)) for versioning our datasets stored in Google Cloud Bucket
 - We mainly track our raw images and corresponding labels, as well as our generated TFRecords.
 - [Full Details Here: data versioning control README.md](./data_versioning_control/README.md)

**Data Labels Processing and Train, Test, Validation Split**

 - This container is meant to run in a Google Cloud VM and reads from our Google Cloud Storage Bucket.
 - As input, it reads the raw image and label data, and saves the formatted filepaths + labels as pickle files into the Bucket.
 - These pickle files are already split into train, test, and validation splits for ingestion by the TFRecords container
 - [Full Details Here: data labels processing README.md](./data_labels_processing/README.md)

**TFRecords Creation Container**
 - This container is meant to run in a Google Cloud VM and reads from our Google Cloud Storage Bucket.
 - This container is expected to read the output of the **Data Labels Processing and Train, Test, Validation Split** container. 
 - It reads the train, test, validation splits pickle files, and subsequently creates TFRecords
 - This step includes some image preprocessing, re-sizing, etc. before saving the TFRecords into the Bucket. 
 - These TFRecords are prepped for consumption either by our Google Colab notebooks or by our **Model Training Container**
 - [Full Details Here: TFRecords Creation README.md](./tfrecords_creation/README.md)

**Model Training Container**

- This contains the code necessary to package our training script, execute a job in Vertex AI, and track model progress in Weights and Biases.
- The training script currently uses a simple VGG-like model architecture for simplicity at this stage of the project. Later milestones will see usage of more complex architectures
- The scripts also make use of TF Records and TF Data pipelines for faster data preprocessing. See the `task.py` script to understand how we've implemented these features
- The `README.md` in this container gives detailed instructions on how to build the container, package the training scripts, and execute the packages in Vertex AI.
- The current configuration of this container allows us to manipulate a YAML file called `model_config.yml` to more easily change hyperparameters. Later versions will allow more control over model architectures and tracking within Weights and Biases.
- [Full Details Here: model-training README.md](./model-training/README.md)

**App Front-End Container**

 - This contains the frontend app that runs in your browser.
 - The frontend is made using Flask and allows user to submit their own food photos and see the model-estimated nutrition info.
 - Visit [here](./src/app) for container directory

**Image Processing Container**

 - This container has code that allows you to define data preprocessing pipelines with Luigi 
 - You can build batches to increase the size of your image datasets and make them more robust to variations in image quality. 
 - **Note:** Augmented image data is not currently used in our training at this time. 
 - [Full Details Here: Image Processing Containers README.md](./src/image_prep/README.md)

**Full Project Directory Structure**
<br>
```
.
├── LICENSE
├── README.md
├── block_diagram.drawio.svg
├── data
│   └── raw_data
│       ├── FooDD.dvc
│       ├── Nutrition5k_Other.dvc
│       └── Nutrition5k_realsense_overhead.dvc
├── docker-compose.yml
├── model-training
│   ├── Dockerfile
│   ├── LICENSE
│   ├── Pipfile
│   ├── Pipfile.lock
│   ├── README.md
│   ├── cli-multi-gpu.sh
│   ├── cli.py
│   ├── cli.sh
│   ├── docker-entrypoint.sh
│   ├── docker-shell.bat
│   ├── docker-shell.sh
│   ├── package
│   │   ├── PKG-INFO
│   │   ├── setup.py
│   │   └── trainer
│   │       ├── __init__.py
│   │       ├── model_config.yml
│   │       ├── task.py
│   │       └── task_multi_gpu.py
│   ├── package-trainer.sh
│   ├── serverless-training.png
│   └── trainer.tar.gz
├── notebooks
│   ├── 230922_EDA_of_Nutrition5k_Ben.ipynb
│   ├── FooDD_EDA.ipynb
│   └── Nutrition5k_EDA_Base_Model.ipynb
├── reports
│   ├── base_CNN_prediction_example.jpg
│   ├── command_line.png
│   ├── vertex_ai.png
│   ├── wanb_3.png
│   ├── wandb_1.png
│   └── wandb_2.png
├── secrets
│   └── model-training.json
└── src
    ├── app
    │   ├── Dockerfile
    │   ├── Pipfile
    │   ├── Pipfile.lock
    │   ├── app.py
    │   ├── static
    │   │   ├── css
    │   │   │   ├── custom_styles.css
    │   │   │   └── styles.css
    │   │   ├── fonts
    │   │   │   ├── glyphicons-halflings-regular.eot
    │   │   │   ├── glyphicons-halflings-regular.svg
    │   │   │   ├── glyphicons-halflings-regular.ttf
    │   │   │   ├── glyphicons-halflings-regular.woff
    │   │   │   └── glyphicons-halflings-regular.woff2
    │   │   ├── img
    │   │   │   ├── 1837-diabetic-pecan-crusted-chicken-breast_JulAug20DF_clean-simple_061720 Background Removed.png
    │   │   │   ├── 1837-diabetic-pecan-crusted-chicken-breast_JulAug20DF_clean-simple_061720.jpg
    │   │   │   ├── construction_img.jpeg
    │   │   │   └── sample_upload_file_ui.png
    │   │   └── js
    │   │       ├── main.js
    │   │       └── scripts.js
    │   └── templates
    │       ├── layouts
    │       │   └── main.html
    │       └── pages
    │           ├── home.html
    │           ├── results.html
    │           ├── under_construction.html
    │           └── upload_photo.html
    ├── dvc
    │   └── Dockerfile
    └── image_prep
        ├── Dockerfile
        ├── Pipfile
        ├── Pipfile.lock
        ├── README.md
        ├── batch_definitions
        │   └── batch_a
        ├── image_prep
        │   ├── __init__.py
        │   ├── __main__.py
        │   ├── batch_builder.py
        │   ├── cli.py
        │   ├── function_registry.py
        │   ├── preprocessing_pipeline.py
        │   └── task.py
        ├── image_preprocessing_definition.png
        ├── image_preprocessing_output.png
        └── pipelines
            ├── pipeline_a
            ├── pipeline_b
            ├── pipeline_c
            ├── pipeline_d
            └── pipeline_e

```
