# Gemini Configuration File

## Project Overview

This project is a collection of recipes in Markdown format. The goal is to create a simple, easy-to-use, and interactive recipe book for people who are crazily busy but still want to eat healthy home-cooked food.

## Recipe Format

The recipes in this project start with the section Cooking Time, which feature short active cooking time (i.e., the time a person is actively involved in the cooking process). Sometimes the total cooking time can be much longer than the active cooking time, but the rest of the cooking time is fully hands-off and without any supervision. Tools needed to create the fully hands-off cooking time is also provided in the Efficiency Tools section of each recipe.

Notice that some recipes contain an Extension section. This section contains tips on how this same method can be applied to other ingredients too.

## User Goals

The user wants to be able to easily search, select, and filter recipes based on their preferences. They also want to be able to easily obtain the details of a recipe, including the ingredients, instructions, and cooking time.

## Language Support

The user may also want to converse using their native languages. The returned recipe should then be translated into their language of choice. A unit conversion should also be provided to match the preferred unit system for countries that use that language. For example, Chinese and Turkish users use the metric system, while English users will default to the imperial system unless specified otherwise.

## Special Search Instructions

### Unavailable Ingradients

If an ingradient is not found. Try first to search for a general recipe. For example, Chinese Salad, where in the ingradient list, one item is "Any vegetables or protein". Recipes like this can be a recommendation for any vegetable or protein ingradient.

Secondly, look for recipes with Extension section. Some recipes can also be easily modified to use other ingradients, a recipe can even change from a protein dish to a vegetable dish, or vice versa. For example, Braised Eggplant recipe can be used for other braised dishes such as braised mushrooms or braised tofu. Therefore, when a user searches for a recipe using mushrooms or tofu, the Braised Eggplant recipe should also be mentioned as a possible match. Explain in the response that the recipe can be modified to use other ingradients, and thus is a possible match for this search.

## Important Files

The recipes are designed intentionally to be multi-cultural so that more diversity is provided. All receipes are contained in folders based on their origin.

Example:
- `Chinese/`: This directory contains Chinese recipes.
- `Turkish/`: This directory contains Turkish recipes.

## Sample Questions

- "Find me a recipe that can be finished in 30 minutes."
- "Find me a recipe that uses ground beef."
- "Find me a recipe that uses ground beef and can be finished in 30 minutes."
- "Find me a recipe that doesn't use air fryer."
- "What ingredients do I need for Mushroom Chicken Soup?"
- "What tools do I need for Mushroom Chicken Soup?"
- "Please recommend a recipe for salad."