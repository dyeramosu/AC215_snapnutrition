import pandas as pd
import os
import numpy as np
# sklearn
from sklearn.model_selection import train_test_split
import pickle

print("Begin processing....")

RAW_LABELS_CAFE1_PATH = "./snapnutrition_data_bucket/data/raw_data/Nutrition5k_Other/dish_metadata_cafe1.csv"
RAW_LABELS_CAFE2_PATH = "./snapnutrition_data_bucket/data/raw_data/Nutrition5k_Other/dish_metadata_cafe2.csv"
PROCESSED_LABELS_CSV_SAVE_PATH = "./snapnutrition_data_bucket/data/processed_labels/full_cleaned_dish_labels.csv"
TRAIN_SAVE_PATH = "./snapnutrition_data_bucket/data/processed_labels/train_data.pickle"
VAL_SAVE_PATH = "./snapnutrition_data_bucket/data/processed_labels/validation_data.pickle"
TEST_SAVE_PATH = "./snapnutrition_data_bucket/data/processed_labels/test_data.pickle"
DATA_DIR = './snapnutrition_data_bucket/data/raw_data/Nutrition5k'

#get labels from raw dataset
labels = pd.read_csv(RAW_LABELS_CAFE1_PATH, sep=',', header=None,  usecols=range(0,6), names=['dish_id', 'total_calories', 'total_mass', 'total_fat', 'total_carb', 'total_protein'])
labels2 = pd.read_csv(RAW_LABELS_CAFE2_PATH, sep=',', header=None,  usecols=range(0,6), names=['dish_id', 'total_calories', 'total_mass', 'total_fat', 'total_carb', 'total_protein'])
#combine 2 csv's of dish id and nutrition from the 2 cafe's
full_labels_df = pd.concat([labels, labels2], axis=0, ignore_index=True)

#UTILS
#get label for dish
def get_nutrition_from_dish_id(full_labels_df, dish_id):
    total_calories = full_labels_df[full_labels_df['dish_id']==dish_id]['total_calories'].item()
    total_mass = full_labels_df[full_labels_df['dish_id']==dish_id]['total_mass'].item()
    total_fat = full_labels_df[full_labels_df['dish_id']==dish_id]['total_fat'].item()
    total_carb = full_labels_df[full_labels_df['dish_id']==dish_id]['total_carb'].item()
    total_protein = full_labels_df[full_labels_df['dish_id']==dish_id]['total_protein'].item()

    return [np.float32(total_calories), np.float32(total_mass), np.float32(total_fat), np.float32(total_carb), np.float32(total_protein)]

## INSERT LOGIC HERE TO SELECT GOOD LABELS OR PRE-PROCESS LABELS
#exclude bad entires from dataset (EDA determined some foods had errors with having 0 mass and 0 calories)
print("Total entries with 0 calories: ", full_labels_df[full_labels_df['total_calories']==0].shape[0])
print("Total entries in dataset: ", full_labels_df.shape[0])
print('Total good label entries in csv: ', full_labels_df.shape[0] - full_labels_df[full_labels_df['total_calories']==0].shape[0])
issue_dish_id_array = full_labels_df[full_labels_df['total_calories']==0].dish_id.values
#remove 0 calorie images
full_labels_df = full_labels_df[full_labels_df['total_calories']!=0]
#remove filepaths to images with 0 calories
issue_dish_id_array_filepaths = [dish_id for dish_id in issue_dish_id_array] #get issue dish id's with 0 calories
dish_ids_with_rgb = [fname.rstrip(".png") for fname in os.listdir(DATA_DIR)] #get all dishes with overhead images
valid_dish_ids = list(set(dish_ids_with_rgb)-set(issue_dish_id_array_filepaths)) #get only good dishes
#create image filepaths and labels
filenames = [os.path.join(DATA_DIR, fname) for fname in os.listdir(DATA_DIR) if fname != "annotations.json" and fname.rstrip(".png") in valid_dish_ids]  #select rgb images only for now (exclude depth)
labels = [get_nutrition_from_dish_id(full_labels_df, fname.rstrip(".png")) for fname in os.listdir(DATA_DIR) if fname != "annotations.json" and fname.rstrip(".png") in valid_dish_ids]
data_dict = {'filename': filenames, 'label': labels}

print("Num image files: ", len(filenames))
print("Num image labels: ", len(labels))


#Save cleaned labels and image paths for TFRecord Creation Ingestion
final_data = {"filenames" : filenames, "labels": labels}
final_df = pd.DataFrame(data=final_data)
final_df.to_csv(PROCESSED_LABELS_CSV_SAVE_PATH)
print("Successfully saved processed labels and paths to: ", PROCESSED_LABELS_CSV_SAVE_PATH)

#Prepare Data For Train Test Validation Splits
data = zip(labels, filenames)
data = list(data)
validation_percent = 0.3
test_percent = 0.5 # split half so val and test are both 15% of original dataset
# Split data into train / validate
train_xy, validate_xy = train_test_split(data, test_size=validation_percent)
validate_xy, test_xy = train_test_split(validate_xy, test_size=test_percent)
print("train_xy count:",len(train_xy))
print("validate_xy count:",len(validate_xy))
print("test_xy count:",len(test_xy))

# Store data (serialize)
with open(TRAIN_SAVE_PATH, 'wb') as handle:
    pickle.dump(train_xy, handle, protocol=pickle.HIGHEST_PROTOCOL)
with open(VAL_SAVE_PATH, 'wb') as handle:
    pickle.dump(validate_xy, handle, protocol=pickle.HIGHEST_PROTOCOL)
with open(TEST_SAVE_PATH, 'wb') as handle:
    pickle.dump(test_xy, handle, protocol=pickle.HIGHEST_PROTOCOL)

print("End processing....")
