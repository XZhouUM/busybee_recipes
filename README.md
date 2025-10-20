# BusyBee Recipes

Interactive recipe book for people who are crazily busy but still want to eat healthy home-cooked food.

Most of the recipes contained in this repo is designed to be:
- Simple
- Easy to use
- Short active cooking time, i.e., less time a person actually spends in the kitchen
- Promote use of efficiency tools in the kitchen
- Multicultural and diverse

There are still a small portion of the recipes that are designed to be used for treat days. These recipes are usually longer in active cooking time and are for the days when you have more time and want to treat the family with something special.

The interactive feature of the cookbook is supported by both the python scripts developed for this repo and the Gemini CLI. You need to [install the Gemini CLI](https://github.com/google-gemini/gemini-cli/blob/main/README.md) to use it.

## User Guide

### Post Clone Set-up

After cloning the repo, run the following command to set up the repo. This command will:
1. Install the pre-push hook that is used to format the tooling scripts and index the recipe database.
2. Install the python dependencies needed to run the tooling scripts.
3. Prompt you to install the Gemini CLI that is required to use the interactive features.

```bash
./post_clone.sh
```

### Add a New Recipe

1. Manually add a new file in any language and in any format.
2. Ask Gemini to format the recipe file. Gemini will automatically translate the recipe to English and convert it to the correct format specified in the GEMINI.md file.
3. The pre-push hook will automatically update the index file before the changes are pushed to the repo.

Alternatively,
1. Ask Gemini to search for a recipe on the internet and add it to the repo. Gemini will automatically translate the recipe to English and convert it to the correct format specified in the GEMINI.md file.
2. The pre-push hook will automatically update the index file before the changes are pushed to the repo.

### Search, Selection, and Filtering

You can search for recipes using the Gemini CLI. You can also use the CLI to select and filter recipes based on your preferences.

### Plan a Week of Meals

You can use the `plan_week.py` script to plan a week of meals. The script will automatically generate a calendar file for the week. The calendar file can be imported into your calendar app to see meal events, grocery shopping reminder, and preparation time reminder.

Example usage:
```bash
python tools/plan_week.py
```

If you want to specify the meal plan, you can do so by providing a JSON-like string as an argument. For example:
```bash
python tools/plan_week.py --meal-plan '{Monday: {1: [20, 40]}, Tuesday: {1: [30, 60]}}'
```

If you are ok with the default meal plan, you can download the latest weekly meal plan from GitHub Action artifacts.

### Meal Planning Tool

This repo contains a script to plan meals based on cooking time constraints. The tool reads from `sorted_recipes_by_cooking_time.yaml` file containing sorted recipes and generates meal combinations that fit within specified time limits.

To see the available options and usage instructions, run:
```bash
python tools/plan_menu.py --help
```

Example usage:
```bash
python tools/plan_menu.py --days 3 --meals-per-day 2 --active-time 20 --total-time 45
```
This command means that you would like to plan meals for 3 days, with 2 meals per day. Each meal should have a maximum active cooking time of 20 minutes and a maximum total time (including hands-off time) of 45 minutes.

```BETA: This function can also be achieved using Gemini CLI.```

### Grocery List Generator

You can use the `generate_grocery_list.py` script to generate a grocery list from a list of recipe names. The script will automatically consolidate the ingredients and quantities for you.

Example usage:
```bash
python tools/generate_grocery_list.py "Firm Tofu" "Fried Beef" "Egg Drop Soup"
```
