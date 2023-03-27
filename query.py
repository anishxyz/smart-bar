import os
import re
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


# Function to add oz measurements for shots (easier for bartending)
def convert_shots_to_ounces(measure):
    # Use a regular expression to find the numerical value and the word "shot" or "shots"
    pattern = r'(\d+\s*/\s*\d+|\d+(\.\d+)?|\d+)?(\s*\d+\s*/\s*\d+)?\s*(sho?t?s?)'
    match = re.search(pattern, measure, re.IGNORECASE)

    if match:
        # Extract the number from the match
        number1 = match.group(1)
        number2 = match.group(3)
        shot_word = match.group(4)

        total_number = 0.0

        if number1:
            # Convert the number to a float value
            if '/' in number1:
                numerator, denominator = number1.split('/')
                total_number += float(numerator) / float(denominator)
            else:
                total_number += float(number1)

        if number2:
            # Convert the second number to a float value
            if '/' in number2:
                numerator, denominator = number2.split('/')
                total_number += float(numerator) / float(denominator)

        if total_number > 0.0:
            # Convert the number of shots to ounces (assuming 1 shot = 1.5 ounces)
            ounces = total_number * 1.5

            # Update the measure string with the number in ounces and the original measure
            measure = f"{measure} ({ounces:.1f} oz)"
            print(measure)

    return measure

# Initialize an empty list to store the cocktails
cocktails = []

for result in results:
    missing_ingredients = 0
    updated_ingredients = []

    for ingredient in result['ingredients']:
        updated_measure = convert_shots_to_ounces(ingredient['measure'])
        ingredient['measure'] = updated_measure

        if not is_base_ingredient_available(ingredient['name'], ingredients_available):
            missing_ingredients += 1

    if missing_ingredients <= diff:
        result['missing_ingredients'] = missing_ingredients
        cocktails.append(result)

# Sort the cocktails by the number of missing ingredients and then alphabetically by name
sorted_cocktails = sorted(cocktails, key=lambda x: (x['missing_ingredients'], x['drink_name']))

# Print the sorted cocktails
print("Cocktails you can make with the available ingredients and within the diff limit:")
for cocktail in sorted_cocktails:
    print(f"{cocktail['drink_name']} (missing {cocktail['missing_ingredients']} ingredient(s))")
    print(f"\t\t{cocktail['ingredients']}\n")


# Close the MongoDB connection
client.close()
