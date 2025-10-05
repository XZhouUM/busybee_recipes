#!/usr/bin/env python3
"""
Menu Planning Tool

This script provides functionality to automatically plan meals based on cooking time constraints
and recipe availability. It reads from a YAML file containing sorted recipes and generates
meal combinations that fit within specified time limits.

USAGE AS A LIBRARY:
==================

from pathlib import Path
from tools.plan_menu import plan_menu

# Plan meals for 3 days, 2 meals per day, with time constraints
recipe_dir = Path(".")
meals = plan_menu(
    recipe_dir=recipe_dir,
    number_of_days=3,
    number_of_meals_per_day=2,
    active_cooking_time_per_meal=20,  # max 20 minutes active cooking
    total_time_per_meal=45            # max 45 minutes total time
)

# meals will be a list of lists, e.g.:
# [
#   ['Egg Drop Soup'],                    # Single recipe meal
#   ['Fried Beef', 'Fried Vegetables'],   # Protein + Vegetable combination
#   ['Curry Rice'],                       # Single recipe meal
#   ...
# ]

USAGE AS COMMAND LINE TOOL:
===========================

# Basic usage - plan 3 days with 2 meals per day
python tools/plan_menu.py --days 3 --meals-per-day 2 --active-time 20 --total-time 45

# With reproducible results (same meals each time)
python tools/plan_menu.py --days 3 --meals-per-day 2 --active-time 20 --total-time 45 --seed 42

# Specify custom recipe directory
python tools/plan_menu.py --recipe-dir /path/to/recipes --days 2 --meals-per-day 3 --active-time 15 --total-time 30

# Show help and all options
python tools/plan_menu.py --help

MEAL GENERATION LOGIC:
=====================

1. Validates that active_cooking_time_per_meal is within the available recipe range
2. Creates two types of meals:
   - Single-recipe meals: Uses recipes tagged with 'Vegetables_Protein'
   - Two-recipe meals: Combines 'Protein' recipes with 'Vegetables' recipes
3. Ensures all meal combinations respect both active cooking time and total time limits
4. Randomly selects from valid combinations to create the requested number of meals

REQUIREMENTS:
=============

- recipes/sorted_recipes_by_cooking_time.yaml file must exist in the recipe directory
- YAML file must contain recipe data with timing information and tags
- Python packages: yaml, pathlib, typing, random, argparse

ERROR HANDLING:
===============

- ValueError: If cooking time constraints are outside available recipe range
- ValueError: If no valid meal combinations can be found
- FileNotFoundError: If the recipe YAML file cannot be found
"""

from typing import List
from pathlib import Path
import yaml
import random
import argparse


def plan_menu(recipe_dir: Path,
        number_of_days: int,
        number_of_meals_per_day: int,
        active_cooking_time_per_meal: int,
        total_time_per_meal: int
    ) -> List[List[str]]:
    """
    Plan the menu for the specified period.

    Args:
        recipe_dir (Path): Directory containing all the recipes.
        number_of_days (int): Number of days to plan the menu for.
        number_of_meals_per_day (int): Number of meals to plan per day.
        active_cooking_time_per_meal (int): Maximum active cooking time per meal.
        total_time_per_meal (int): Maximum total time (including hands-off time) per meal.

    Returns:
        List[List[str]]: List of meals, where each meal is a list of recipe names.

    Raises:
        ValueError: If active_cooking_time_per_meal is outside the available recipe range.
    """
    # Load the sorted recipes YAML file
    yaml_file = recipe_dir / "recipes" / "sorted_recipes_by_cooking_time.yaml"
    with open(yaml_file, 'r') as f:
        data = yaml.safe_load(f)

    recipes = data['sorted_recipes_by_active_cooking_time']
    time_range = data['summary']['active_cooking_time_range']

    # Validate active_cooking_time_per_meal is within range
    if not (time_range['min_minutes'] <= active_cooking_time_per_meal <= time_range['max_minutes']):
        raise ValueError(
            f"active_cooking_time_per_meal ({active_cooking_time_per_meal}) must be between "
            f"{time_range['min_minutes']} and {time_range['max_minutes']} minutes"
        )

    # Separate recipes by tags
    vegetables_protein_recipes = []
    protein_recipes = []
    vegetables_recipes = []

    for recipe in recipes:
        tags = recipe['tags']
        if 'Vegetables_Protein' in tags:
            vegetables_protein_recipes.append(recipe)
        elif 'Protein' in tags:
            protein_recipes.append(recipe)
        elif 'Vegetables' in tags:
            vegetables_recipes.append(recipe)

    # Result set to store all valid meal combinations
    result_set = []

    # 1. Find Vegetables_Protein recipes within time limits (single recipe meals)
    for recipe in vegetables_protein_recipes:
        if (recipe['active_cooking_time_minutes'] <= active_cooking_time_per_meal and
            recipe['total_cooking_time_minutes'] <= total_time_per_meal):
            result_set.append([recipe['name']])

    # 2. Find Protein + Vegetables combinations
    for protein_recipe in protein_recipes:
        if protein_recipe['active_cooking_time_minutes'] <= active_cooking_time_per_meal:
            # Calculate remaining time after protein recipe
            remaining_active_time = active_cooking_time_per_meal - protein_recipe['active_cooking_time_minutes']
            remaining_total_time = total_time_per_meal - protein_recipe['total_cooking_time_minutes']

            # Find vegetables recipes that fit in the remaining time
            for veg_recipe in vegetables_recipes:
                if (veg_recipe['active_cooking_time_minutes'] <= remaining_active_time and
                    veg_recipe['total_cooking_time_minutes'] <= remaining_total_time):
                    result_set.append([protein_recipe['name'], veg_recipe['name']])

    # Calculate total number of meals needed
    total_meals_needed = number_of_days * number_of_meals_per_day

    # Randomly draw from result set
    if len(result_set) == 0:
        raise ValueError("No valid meal combinations found with the given time constraints")

    # Random selection with replacement
    selected_meals = []
    for _ in range(total_meals_needed):
        selected_meals.append(random.choice(result_set))

    return selected_meals


def main():
    """
    Main function to run the menu planner from command line.

    Command line arguments:
    - --recipe-dir: Path to directory containing recipe files (default: current directory)
    - --days: Number of days to plan (required)
    - --meals-per-day: Number of meals per day (required)
    - --active-time: Max active cooking time per meal in minutes (required)
    - --total-time: Max total time per meal in minutes (required)
    - --seed: Random seed for reproducible results (optional)

    Examples:
    python tools/plan_menu.py --days 7 --meals-per-day 3 --active-time 30 --total-time 60
    python tools/plan_menu.py --days 3 --meals-per-day 2 --active-time 15 --total-time 30 --seed 123
    """
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(
        description='Plan meals based on cooking time constraints',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --days 3 --meals-per-day 2 --active-time 20 --total-time 45
  %(prog)s --days 7 --meals-per-day 3 --active-time 15 --total-time 30 --seed 42
  %(prog)s --recipe-dir /path/to/recipes --days 2 --meals-per-day 1 --active-time 10 --total-time 25
        """
    )

    # Define command line arguments
    parser.add_argument('--recipe-dir', type=str, default='.',
                        help='Directory containing the recipes (default: current directory)')
    parser.add_argument('--days', type=int, required=True,
                        help='Number of days to plan meals for')
    parser.add_argument('--meals-per-day', type=int, required=True,
                        help='Number of meals per day')
    parser.add_argument('--active-time', type=int, required=True,
                        help='Maximum active cooking time per meal (minutes)')
    parser.add_argument('--total-time', type=int, required=True,
                        help='Maximum total time per meal (minutes)')
    parser.add_argument('--seed', type=int, default=None,
                        help='Random seed for reproducible results')

    # Parse command line arguments
    args = parser.parse_args()

    # Set random seed if provided for reproducible results
    if args.seed is not None:
        random.seed(args.seed)
        print(f"Using random seed: {args.seed} (results will be reproducible)")

    try:
        # Convert recipe directory to Path object
        recipe_dir = Path(args.recipe_dir)

        # Generate meal plan using the core planning function
        meals = plan_menu(
            recipe_dir=recipe_dir,
            number_of_days=args.days,
            number_of_meals_per_day=args.meals_per_day,
            active_cooking_time_per_meal=args.active_time,
            total_time_per_meal=args.total_time
        )

        # Display the generated meal plan in a user-friendly format
        print(f"Generated meal plan for {args.days} days with {args.meals_per_day} meals per day:")
        print(f"Constraints: {args.active_time} min active time, {args.total_time} min total time")
        print("-" * 60)

        # Organize and display meals by day
        meal_count = 0
        for day in range(args.days):
            print(f"\nDay {day + 1}:")
            for meal_num in range(args.meals_per_day):
                meal = meals[meal_count]
                meal_count += 1
                # Format output differently for single vs. multiple recipe meals
                if len(meal) == 1:
                    print(f"  Meal {meal_num + 1}: {meal[0]}")
                else:
                    print(f"  Meal {meal_num + 1}: {' + '.join(meal)}")

        print(f"\nTotal meals planned: {len(meals)}")
        print("\nNote: Single recipes are complete meals (Vegetables_Protein).")
        print("      Combined recipes are Protein + Vegetables combinations.")

    except ValueError as e:
        print(f"Error: {e}")
        return 1
    except FileNotFoundError as e:
        print(f"Error: Could not find recipe file - {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
