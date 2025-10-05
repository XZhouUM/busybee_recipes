# BusyBee Recipes

Recipe book for people who are crazily busy but still want to eat healthy home-cooked food:
- Simple
- Easy to use
- Short active cooking time, i.e., less time a person actually spends in the kitchen
- Promote use of efficiency tools in the kitchen
- Multicultural and diverse

For tech-savvy users, it can also be interactive with the help of Gemini CLI. All recipes are written in English, but Gemini CLI can translate the recipes to other languages and other unit systems.

## User Guide

### Meal Planning Tool

This repo contains a tool to plan meals based on cooking time constraints. The tool reads from a YAML file containing sorted recipes and generates meal combinations that fit within specified time limits.

To see the available options and usage instructions, run:
```bash
python tools/plan_menu.py --help
```

Example usage:
```bash
python tools/plan_menu.py --days 3 --meals-per-day 2 --active-time 20 --total-time 45
```
This command means that you would like to plan meals for 3 days, with 2 meals per day. Each meal should have a maximum active cooking time of 20 minutes and a maximum total time (including hands-off time) of 45 minutes.

## Developer Guide

### Set up Automation for Recipe Format Checking and Indexing

After cloning the repo, run the following command to set up the pre-push hook for automatic recipe format checking and indexing:
```bash
./post_clone.sh
```

## Advanced Features

### LLM Support through GEMINI CLI for both Users and Developers

This repo contains a GEMINI.md file that configures the Gemini CLI to work more finely with this repo. You need to [install the Gemini CLI](https://github.com/google-gemini/gemini-cli/blob/main/README.md) to use it.

### Add Recipes of Various Languages 

Add a new file in any language and in any format. Then ask Gemini to format the recipe.

### Search, Selection, and Filtering

Search with ingredients, cooking time, and other attributes. Select and filter recipes based on your preferences.

### Menu Planning and Shopping List Generation (Beta)

Plan your menu for the week and generate a shopping list. Specify the amount of time you want to spend on active cooking each day, the total time you can spend in the kitchen, and how many meals you need to plan for each day. Gemini will plan each meal for you. You can further ask for a shopping list based on the menu plan.