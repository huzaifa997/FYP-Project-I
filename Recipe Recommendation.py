from flask import Flask, request, jsonify
import pandas as pd
from fuzzywuzzy import fuzz
app = Flask(__name__)
df = pd.read_excel('C:/Users/Huzafa Husan/Desktop/New folder/newone.xlsx')

def calculate_match_score(row, user_ingredients):
    recipe_ingredients = [ingredient.lower().strip() for ingredient in row['Ingredients'].split(',')]
    match_score = sum([fuzz.token_set_ratio(user_ingredient, recipe_ingredient) 
                                            for user_ingredient in user_ingredients for recipe_ingredient in recipe_ingredients])
    return match_score

def adjust_match_score_based_on_bmi(row, user_bmi):

    if user_bmi < 18.5:  
        return row['Match Score'] - 5
    elif 18.5 <= user_bmi < 25:  
        return row['Match Score'] + 10
    elif 25 <= user_bmi < 30:  
        return row['Match Score'] + 5
    else:  
        return row['Match Score']  

@app.route('/recommend', methods=['POST'])

def recommend_recipe():
    
    user_ingredients = request.json['ingredients']
    user_bmi = request.json.get('bmi', None)  
    user_ingredients = [ingredient.lower().strip() for ingredient in user_ingredients]
    local_df = df.copy()
    local_df['Match Score'] = local_df[pd.notna(local_df['Ingredients'])].apply(calculate_match_score,args=(user_ingredients,), axis=1)
    if user_bmi is not None:
        local_df['Adjusted Match Score'] = local_df.apply(adjust_match_score_based_on_bmi, args=(user_bmi,), axis=1)
    else:
        local_df['Adjusted Match Score'] = local_df['Match Score']
    local_df = local_df.sort_values(by=['Adjusted Match Score'], ascending=False)
    recommended_recipes = []
    for index, row in local_df.head(3).iterrows():
        recipe = {
            'name': row['Recipe Name'],
            'ingredients': row['Ingredients'],
            'details': row['Details'],
            'match_score': row['Match Score']  }
        if 'Recipe PDF' in row:
            recipe['recipe_pdf'] = row['Recipe PDF']
        if 'YouTube Video' in row:
            recipe['youtube_video'] = row['YouTube Video']
        recommended_recipes.append(recipe)
        
    return jsonify({'recommended_recipes': recommended_recipes})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
