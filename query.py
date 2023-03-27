import os
import certifi
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


# Connect to MongoDB
mongodb_uri = os.getenv('MONGODB_URI')
client = MongoClient(mongodb_uri, tlsCAFile=certifi.where())
db = client['cocktails_db']
collection = db['cocktails']

# List the ingredients you have (case-insensitive)
ingredients_available = ['Tequila', 'Lemon', 'Lime', 'Rum', 'Dry Vermouth', 'Sweet Vermouth', 'Gin']

# Set the 'diff' value
diff = 2

# Query MongoDB to find cocktails that can be made with the ingredients
results = collection.find({
    'ingredients.name': {'$in': ingredients_available}
})


# Function to check if a base ingredient is in the available ingredients list
def is_base_ingredient_available(base_ingredient, available_ingredients):
    for ingredient in available_ingredients:
        if base_ingredient.lower() in ingredient.lower():
            return True
    return False


# Print the cocktails that can be made with the available ingredients and within the diff limit
print("Cocktails you can make with the available ingredients and within the diff limit:")
for result in results:
    missing_ingredients = 0
    for ingredient in result['ingredients']:
        if not is_base_ingredient_available(ingredient['name'], ingredients_available):
            missing_ingredients += 1

    if missing_ingredients <= diff:
        print(f"{result['drink_name']} (missing {missing_ingredients} ingredient(s))")
        print(f"\t\t{result['ingredients']}\n")

# Close the MongoDB connection
client.close()
