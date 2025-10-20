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

# Plan meals with flexible time constraints per meal
recipe_dir = Path(".")
meal_plan = {
    "Monday": {
        1: (20, 45),    # Meal 1: 20 min active, 45 min total
        2: (15, 30),    # Meal 2: 15 min active, 30 min total
        3: (25, 60)     # Meal 3: 25 min active, 60 min total
    },
    "Tuesday": {
        1: (10, 25),    # Meal 1: 10 min active, 25 min total
        2: (30, 50)     # Meal 2: 30 min active, 50 min total
    }
}

meals = plan_menu(
    recipe_dir=recipe_dir,
    meal_plan=meal_plan
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

from typing import List, Dict, Tuple
from pathlib import Path
import yaml
import random
import argparse


def plan_menu(recipe_dir: Path,
        meal_plan: Dict[str, Dict[int, Tuple[int, int]]],
        ensure_variety: bool = True
    ) -> List[List[str]]:
    """
    Plan the menu for the specified period.

    Args:
        recipe_dir (Path): Directory containing all the recipes.
        meal_plan (Dict[str, Dict[int, Tuple[int, int]]]): Dictionary mapping day names to meals
            with their time constraints. Format: {day: {meal_number: (active_time, total_time)}}
            Example: {"Monday": {1: (20, 45), 2: (15, 30)}, "Tuesday": {1: (25, 50)}}
        ensure_variety (bool): If True, tries to avoid duplicate recipes across all meals.
            If False, allows duplicate recipes. Default: True.

    Returns:
        List[List[str]]: List of meals, where each meal is a list of recipe names.
                        Meals are returned in the order: Day 1 Meal 1, Day 1 Meal 2, ..., Day 2 Meal 1, etc.

    Raises:
        ValueError: If any active_cooking_time constraint is outside the available recipe range.
        ValueError: If no valid meal combinations can be found for any meal.
    """
    # Load the sorted recipes YAML file
    yaml_file = recipe_dir / "recipes" / "sorted_recipes_by_cooking_time.yaml"
    with open(yaml_file, 'r') as f:
        data = yaml.safe_load(f)

    recipes = data['sorted_recipes_by_active_cooking_time']
    time_range = data['summary']['active_cooking_time_range']

    # Validate all active_cooking_time constraints are within range
    for day, meals in meal_plan.items():
        for meal_num, (active_time, total_time) in meals.items():
            if not (time_range['min_minutes'] <= active_time <= time_range['max_minutes']):
                raise ValueError(
                    f"active_cooking_time for {day} meal {meal_num} ({active_time}) must be between "
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

    def get_valid_meals_for_constraints(active_time_limit: int, total_time_limit: int) -> List[List[str]]:
        """Get all valid meal combinations for specific time constraints."""
        valid_meals = []

        # 1. Find Vegetables_Protein recipes within time limits (single recipe meals)
        for recipe in vegetables_protein_recipes:
            if (recipe['active_cooking_time_minutes'] <= active_time_limit and
                recipe['total_cooking_time_minutes'] <= total_time_limit):
                valid_meals.append([recipe['name']])

        # 2. Find Protein + Vegetables combinations
        for protein_recipe in protein_recipes:
            if protein_recipe['active_cooking_time_minutes'] <= active_time_limit:
                # Calculate remaining time after protein recipe
                remaining_active_time = active_time_limit - protein_recipe['active_cooking_time_minutes']
                remaining_total_time = total_time_limit - protein_recipe['total_cooking_time_minutes']

                # Find vegetables recipes that fit in the remaining time
                for veg_recipe in vegetables_recipes:
                    if (veg_recipe['active_cooking_time_minutes'] <= remaining_active_time and
                        veg_recipe['total_cooking_time_minutes'] <= remaining_total_time):
                        valid_meals.append([protein_recipe['name'], veg_recipe['name']])

        return valid_meals

    # Generate meals for each day and meal in order
    selected_meals = []
    used_recipes = set()  # Track used recipes for variety

    # Process days in sorted order to ensure consistent output
    for day in sorted(meal_plan.keys()):
        meals_for_day = meal_plan[day]

        # Process meals in numerical order
        for meal_num in sorted(meals_for_day.keys()):
            active_time_limit, total_time_limit = meals_for_day[meal_num]

            # Get valid meal options for this specific time constraint
            valid_meals = get_valid_meals_for_constraints(active_time_limit, total_time_limit)

            if len(valid_meals) == 0:
                raise ValueError(
                    f"No valid meal combinations found for {day} meal {meal_num} "
                    f"with constraints: {active_time_limit} min active, {total_time_limit} min total"
                )

            # Select meal with variety consideration
            if ensure_variety:
                # Filter out meals that use already-used recipes
                unused_meals = []
                for meal in valid_meals:
                    if not any(recipe in used_recipes for recipe in meal):
                        unused_meals.append(meal)

                # If we have unused meals, prefer them; otherwise fall back to any valid meal
                if unused_meals:
                    selected_meal = random.choice(unused_meals)
                else:
                    selected_meal = random.choice(valid_meals)
            else:
                # No variety constraint - randomly select any valid meal
                selected_meal = random.choice(valid_meals)

            # Add selected recipes to used set
            if ensure_variety:
                for recipe in selected_meal:
                    used_recipes.add(recipe)

            selected_meals.append(selected_meal)

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

        # Create meal_plan dictionary from command line arguments
        meal_plan_dict = {}
        for day_num in range(args.days):
            day_name = f"Day {day_num + 1}"
            meal_plan_dict[day_name] = {}
            for meal_num in range(1, args.meals_per_day + 1):
                meal_plan_dict[day_name][meal_num] = (args.active_time, args.total_time)

        # Generate meal plan using the core planning function
        meals = plan_menu(
            recipe_dir=recipe_dir,
            meal_plan=meal_plan_dict
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
