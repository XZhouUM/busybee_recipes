# Gemini Configuration File

## Project Overview

This project is a collection of recipes in Markdown format. The goal is to create a simple, easy-to-use, and interactive recipe book for people who are crazily busy but still want to eat healthy home-cooked food.

### Recipe Format

Each recipe in this project follows a structured format designed for busy home cooks:
```
# Title

#Tag_1 #Tag_2 #Tag_3

## Cooking Time

- Active Cooking Time: [number] minutes
- Total Cooking Time: [number] minutes

## Efficiency Tools

- [tool name]

## Ingredients

- Ingredient name 1 [quantity unit]
- Ingredient name 2 [quantity unit]
- Ingredient name 3 [quantity unit]
...
- Ingredient name

## Instructions

1. Step 1
2. Step 2
3. Step 3

## Extension (optional)

- Tip 1
- Tip 2

## Fast Hack (optional)

1. Tip 1
2. Tip 2
```

#### Explanation of Each Section

- Title (First line of the recipe, first level heading)

The title should be the same as the file name. For example, `fried_yellow_croaker.md` should have the title `Fried Yellow Croaker`.

- Tags (Second line of the recipe; starting with `#`; optional)

Tags are used to help users search for recipes. Right now, the following tags are used:

`#Treat_Day`: Recipes whose active cook time is longer than 30 minutes. These recipes are not suitable for busy days, but are great for treat days when you have more time.

`#Full_Meal`: Recipes that are suitable for full meals, such as breakfast, lunch, and dinner.

- Cooking Time (Second level heading)

    - Active Cooking Time: The time you need to be actively involved in the cooking process
    - Total Cooking Time: May be longer than active time, but includes hands-off periods that require no or minimal supervision

- Efficiency Tools (Second level heading; optional)

- Tools and equipment in each recipe to help achieve the hands-off cooking periods

- Ingredients (Second level heading)

    - List of ingredients required for the recipe
    - Ingredients are written in the format. The bracket that contains quantity and unit is optional for ingredients that are very little.
```
- Ingredient name [quantity unit]
```

- Instructions (Second level heading)

    - Step-by-step instructions for preparing the dish
    - The steps are numbered for easy reference

- Extension (Second level heading; optional)

    - Tips for adapting the recipe method to other ingredients

- Fast Hack (Second level heading; optional)

    - Tips for making the recipe faster

### Folder Structure

The recipes are designed intentionally to be multi-cultural so that more diversity is provided. All receipes are contained in folders based on their origin.

Example:
- `Chinese/`: This directory contains Chinese recipes.
- `Turkish/`: This directory contains Turkish recipes.

## User Support

The user wants to be able to easily search, select, and filter recipes based on their preferences. They also want to be able to easily obtain the details of a recipe, including the ingredients, instructions, and cooking time.

### Sample Questions

- "Find me a recipe that can be finished in 30 minutes."
- "Find me a recipe that uses ground beef."
- "Find me a recipe that uses ground beef and can be finished in 30 minutes."
- "Find me a recipe that doesn't use air fryer."
- "What ingredients do I need for Mushroom Chicken Soup?"
- "What tools do I need for Mushroom Chicken Soup?"
- "Please recommend a recipe for salad."

### Language Support for Users

The user may also want to converse using their native languages. The returned recipe should then be translated into their language of choice. A unit conversion should also be provided to match the preferred unit system for countries that use that language. For example, Chinese and Turkish users use the metric system, while English users will default to the imperial system unless specified otherwise.

### Search Instructions

#### Unavailable Ingradients

If an ingradient is not found. Try first to search for a general recipe. For example, Chinese Salad, where in the ingradient list, one item is "Any vegetables or protein". Recipes like this can be a recommendation for any vegetable or protein ingradient.

Secondly, look for recipes with Extension section. Some recipes can also be easily modified to use other ingradients, a recipe can even change from a protein dish to a vegetable dish, or vice versa. For example, Braised Eggplant recipe can be used for other braised dishes such as braised mushrooms or braised tofu. Therefore, when a user searches for a recipe using mushrooms or tofu, the Braised Eggplant recipe should also be mentioned as a possible match. Explain in the response that the recipe can be modified to use other ingradients, and thus is a possible match for this search.

## Developer Support

### Convert New Recipes to English and the Correct Format

A developer can add new recipes to the repo by creating a new markdown file in the appropriate folder based on the recipe's origin, and writing down the recipe in any language and in any format. The Gemini CLI will automatically translate the recipe to English and convert the recipe to the correct format. The format is given in the section [Recipe Format](#recipe-format) above.

Usually the list of ingredients is already given in a recipe. When the ingredient list is not available, the CLI can deduce the ingredient list from the instructions.

Order the list of ingredients in the way that the ones with quantity and unit come first, followed by the ones without quantity and unit.

At last, polish the wording in the instruction section for better readability. There is no need to add special formatting.