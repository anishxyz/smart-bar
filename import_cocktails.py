import os
import certifi
import pandas as pd
from pymongo import MongoClient

# Read the CSV file
current_directory = os.getcwd()
csv_file = os.path.join(current_directory, 'file.csv')
data = pd.read_csv(csv_file)

# Connect to MongoDB
client = MongoClient('MONGODB_URI', tlsCAFile=certifi.where())
db = client['cocktails_db']
print(db)
collection = db['cocktails']

# Iterate through the CSV rows and create a document for each row
for index, row in data.iterrows():
    print(row)
    document = {
        'drink_name': row['strDrink'],
        'alcoholic': row['strAlcoholic'],
        'category': row['strCategory'],
        'drink_thumb': row['strDrinkThumb'],
        'glass': row['strGlass'],
        'IBA': row['strIBA'],
        'date_modified': row['dateModified'],
        'instructions': row['strInstructions'],
        'ingredients': []
    }

    # Iterate through the ingredients and measures and add them to the document
    for i in range(1, 16):
        ingredient_col = f'strIngredient{i}'
        measure_col = f'strMeasure{i}'

        if not pd.isna(row[ingredient_col]):
            ingredient = {
                'name': row[ingredient_col],
                'measure': row[measure_col] if not pd.isna(row[measure_col]) else ''
            }
            document['ingredients'].append(ingredient)

    # Insert the document into the MongoDB collection
    collection.insert_one(document)

# Close the MongoDB connection
client.close()