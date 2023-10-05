import pandas as pd

RAW_LABELS_CAFE1_PATH = "snapnutrition_data_bucket/data/raw_data/Nutrition5k_Other/dish_metadata_cafe1.csv"
RAW_LABELS_CAFE2_PATH = "snapnutrition_data_bucket/data/raw_data/Nutrition5k_Other/dish_metadata_cafe2.csv"
PROCESSED_LABELS_CSV_SAVE_PATH = "./snapnutrition_data_bucket/data/processed_labels/full_cleaned_dish_labels.csv"

#get labels from raw dataset
labels = pd.read_csv(RAW_LABELS_CAFE1_PATH, sep=',', header=None,  usecols=range(0,6), names=['dish_id', 'total_calories', 'total_mass', 'total_fat', 'total_carb', 'total_protein'])
labels2 = pd.read_csv(RAW_LABELS_CAFE2_PATH, sep=',', header=None,  usecols=range(0,6), names=['dish_id', 'total_calories', 'total_mass', 'total_fat', 'total_carb', 'total_protein'])
#combine 2 csv's of dish id and nutrition from the 2 cafe's
full_labels_df = pd.concat([labels, labels2], axis=0, ignore_index=True)

## INSERT LOGIC HERE TO SELECT GOOD LABELS OR PRE-PROCESS LABELS
#exclude bad entires from dataset (EDA determined some foods had errors with having 0 mass and 0 calories)
print("Total entries with 0 calories: ", full_labels_df[full_labels_df['total_calories']==0].shape[0])
print("Total entries in dataset: ", full_labels_df.shape[0])
print('Total good label entries in csv: ', full_labels_df.shape[0] - full_labels_df[full_labels_df['total_calories']==0].shape[0])

#Save cleaned labels to CSV
full_labels_df.to_csv(PROCESSED_LABELS_CSV_SAVE_PATH)