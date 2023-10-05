# Overview
The purpose of this data labels processing container is as follows:

1) Have logic to exclude faulty labels (e.g. 0 mass dishes)
2) Create train, test, and validation splits
3) Have the splits be in the format [(label, image_file_path), ...]

The idea is that more labels and more images could be added to our raw dataset with time. Or we could find issues with our data and want to make exclusions. In those cases, we can simply add add our data selection logic here and recreate our train, test, validation splits. 

**Output**: The output will be 3 csv's one each for train, test, and validation. They will contain 2 columns: 

1) filepaths: string of path to dish image
2) label: array of np.float32 of [total_calories, total_mass, total_fat, total_carb, total_protein]

These outputs will feed into our tfrecords creation container which outputs tfrecords to our Google Bucket.

##Instructions: 

0) Have a Google VM Set-Up according to the data_versioning_control/READEME.md instructions. DVC should be set-up first so that everthing can also be versioned. 
1) Within the VM, go to the git repo root folder ```AC215_snapnutrition``` and run: ```sudo sh data_labels_processing/docker-shell.sh```
2) Output should go to Google Bucket directory specified in labels_processing.py 