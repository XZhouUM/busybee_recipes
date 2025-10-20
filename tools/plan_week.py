#!/usr/bin/env python3
"""
Weekly Meal Planning Tool

This script provides a predefined weekly meal plan with specific time constraints:
- Weekdays (Monday-Friday): 1 meal per day with (20, 40) cooking time
- Weekends (Saturday-Sunday): 2 meals per day with (30, 60) cooking time
- Exception: Saturday dinner has (60, 120) cooking time for a special meal

USAGE AS A LIBRARY:
==================

from pathlib import Path
from tools.plan_week import plan_week

# Plan a week of meals with predefined schedule
recipe_dir = Path(".")
meals = plan_week(recipe_dir=recipe_dir)

# meals will be a list of lists with 9 total meals:
# - 5 weekday meals (Mon-Fri)
# - 4 weekend meals (Sat lunch, Sat dinner, Sun lunch, Sun dinner)

USAGE AS COMMAND LINE TOOL:
===========================

# Basic usage - plan a week with predefined schedule
python tools/plan_week.py

# With reproducible results (same meals each time)
python tools/plan_week.py --seed 42

# Save grocery list to file (grocery list and calendar are always created)
python tools/plan_week.py --save-grocery-list weekly_groceries.txt

# Specify custom recipe directory
python tools/plan_week.py --recipe-dir /path/to/recipes

# Show help and all options
python tools/plan_week.py --help

WEEKLY SCHEDULE:
===============

Weekdays (Monday-Friday):
- 1 meal per day: 20 minutes active, 40 minutes total

Weekends (Saturday-Sunday):
- Lunch: 30 minutes active, 60 minutes total
- Dinner: 30 minutes active, 60 minutes total
- Exception: Saturday dinner: 60 minutes active, 120 minutes total (special meal)

Total meals per week: 9 meals
"""

from pathlib import Path
from typing import List, Optional
import argparse
import random
import sys
import os
from datetime import datetime, timedelta
import re

# Add the parent directory to the Python path to import plan_menu
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.plan_menu import plan_menu
from tools.generate_grocery_list import generate_grocery_list, format_grocery_list


def plan_week(recipe_dir: Path) -> List[List[str]]:
    """
    Plan a week of meals with predefined schedule and time constraints.

    Args:
        recipe_dir (Path): Directory containing all the recipes.

    Returns:
        List[List[str]]: List of meals, where each meal is a list of recipe names.
                        Meals are returned in order: Mon, Tue, Wed, Thu, Fri, Sat lunch, Sat dinner, Sun lunch, Sun dinner.

    Raises:
        ValueError: If no valid meal combinations can be found for any meal.
        FileNotFoundError: If the recipe YAML file cannot be found.
    """

    # Define the weekly meal plan
    meal_plan = {
        "Monday": {1: (20, 40)},  # Weekday meal: 20 min active, 40 min total
        "Tuesday": {1: (20, 40)},  # Weekday meal: 20 min active, 40 min total
        "Wednesday": {1: (20, 40)},  # Weekday meal: 20 min active, 40 min total
        "Thursday": {1: (20, 40)},  # Weekday meal: 20 min active, 40 min total
        "Friday": {1: (20, 40)},  # Weekday meal: 20 min active, 40 min total
        "Saturday": {
            1: (30, 60),  # Weekend lunch: 30 min active, 60 min total
            2: (60, 120),  # Special Saturday dinner: 60 min active, 120 min total
        },
        "Sunday": {
            1: (30, 60),  # Weekend lunch: 30 min active, 60 min total
            2: (30, 60),  # Weekend dinner: 30 min active, 60 min total
        },
    }

    # Use the flexible meal planning function
    return plan_menu(recipe_dir=recipe_dir, meal_plan=meal_plan)


def create_meal_calendar(
    meals: List[List[str]],
    grocery_list_text: str,
    start_date: Optional[datetime] = None,
) -> str:
    """
    Create an .ics calendar file content for the weekly meal plan.

    Args:
        meals (List[List[str]]): List of meals from plan_week function
        grocery_list_text (str): Formatted grocery list text
        start_date (datetime, optional): Start date for the week. Defaults to next Monday.

    Returns:
        str: .ics file content
    """
    if start_date is None:
        # Default to next Monday
        today = datetime.now()
        days_ahead = 0 - today.weekday()  # Monday is 0
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7
        start_date = today + timedelta(days=days_ahead)

    # Meal schedule mapping to match plan_week output order
    meal_schedule = [
        ("Monday", "Dinner", 18, 0),  # 6:00 PM
        ("Tuesday", "Dinner", 18, 0),  # 6:00 PM
        ("Wednesday", "Dinner", 18, 0),  # 6:00 PM
        ("Thursday", "Dinner", 18, 0),  # 6:00 PM
        ("Friday", "Dinner", 18, 0),  # 6:00 PM
        ("Saturday", "Lunch", 12, 0),  # 12:00 PM
        ("Saturday", "Dinner", 18, 0),  # 6:00 PM
        ("Sunday", "Lunch", 12, 0),  # 12:00 PM
        ("Sunday", "Dinner", 18, 0),  # 6:00 PM
    ]

    # Start building the .ics content
    ics_content = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Busybee Recipes//Weekly Meal Planner//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
    ]

    # Add meal events
    for i, (day_name, meal_type, hour, minute) in enumerate(meal_schedule):
        meal = meals[i]

        # Calculate the date for this meal
        day_offset = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ].index(day_name)
        meal_date = start_date + timedelta(days=day_offset)
        meal_datetime = meal_date.replace(
            hour=hour, minute=minute, second=0, microsecond=0
        )

        # Format meal name
        if len(meal) == 1:
            meal_name = meal[0]
        else:
            meal_name = " + ".join(meal)

        # Create GitHub links for each recipe
        recipe_links = []
        for recipe in meal:
            # Convert recipe name to GitHub-friendly filename
            github_filename = re.sub(r"[^\w\s-]", "", recipe).strip()
            github_filename = re.sub(r"[-\s]+", "_", github_filename)
            github_link = f"https://github.com/xinzhouwang2000/busybee_recipes/blob/main/recipes/{github_filename}.yaml"
            recipe_links.append(f"• {recipe}: {github_link}")

        # Create event
        event_start = meal_datetime.strftime("%Y%m%dT%H%M%S")
        event_end = (meal_datetime + timedelta(hours=1)).strftime("%Y%m%dT%H%M%S")
        event_uid = f"meal-{day_name.lower()}-{meal_type.lower()}-{meal_datetime.strftime('%Y%m%d')}@busybee-recipes"

        ics_content.extend(
            [
                "BEGIN:VEVENT",
                f"UID:{event_uid}",
                f"DTSTART:{event_start}",
                f"DTEND:{event_end}",
                f"SUMMARY:{day_name} {meal_type}: {meal_name}",
                f"DESCRIPTION:Recipes:\\n{'\\n'.join(recipe_links)}",
                f"LOCATION:Kitchen",
                "END:VEVENT",
            ]
        )

    # Add grocery shopping event (Saturday 10 PM)
    saturday_date = start_date + timedelta(days=5)  # Saturday is 5 days after Monday
    shopping_datetime = saturday_date.replace(
        hour=22, minute=0, second=0, microsecond=0
    )
    shopping_start = shopping_datetime.strftime("%Y%m%dT%H%M%S")
    shopping_end = (shopping_datetime + timedelta(hours=1)).strftime("%Y%m%dT%H%M%S")
    shopping_uid = (
        f"grocery-shopping-{shopping_datetime.strftime('%Y%m%d')}@busybee-recipes"
    )

    # Escape newlines in grocery list for .ics format
    escaped_grocery_list = grocery_list_text.replace("\n", "\\n").replace(",", "\\,")

    ics_content.extend(
        [
            "BEGIN:VEVENT",
            f"UID:{shopping_uid}",
            f"DTSTART:{shopping_start}",
            f"DTEND:{shopping_end}",
            "SUMMARY:Grocery Shopping for Weekly Meals",
            f"DESCRIPTION:{escaped_grocery_list}",
            "LOCATION:Grocery Store",
            "END:VEVENT",
        ]
    )

    ics_content.append("END:VCALENDAR")

    return "\n".join(ics_content)


def main():
    """
    Main function to run the weekly meal planner from command line.

    Command line arguments:
    - --recipe-dir: Path to directory containing recipe files (default: current directory)
    - --seed: Random seed for reproducible results (optional)
    - --save-grocery-list: Save grocery list to specified file path

    Examples:
    python tools/plan_week.py
    python tools/plan_week.py --seed 42
    python tools/plan_week.py --save-grocery-list weekly_groceries.txt
    python tools/plan_week.py --recipe-dir /path/to/recipes

    Note: Grocery list and calendar file (weekly_meal_plan.ics) are automatically generated.
    """
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(
        description="Plan a week of meals with predefined schedule and time constraints",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Weekly Schedule:
  Weekdays (Mon-Fri): 1 meal per day (20 min active, 40 min total)
  Weekends (Sat-Sun): 2 meals per day (30 min active, 60 min total)
  Special: Saturday dinner (60 min active, 120 min total)

Examples:
  %(prog)s
  %(prog)s --seed 42
  %(prog)s --save-grocery-list weekly_groceries.txt
  %(prog)s --recipe-dir /path/to/recipes

Note: Grocery list and calendar file are automatically generated.
        """,
    )

    # Define command line arguments
    parser.add_argument(
        "--recipe-dir",
        type=str,
        default=".",
        help="Directory containing the recipes (default: current directory)",
    )
    parser.add_argument(
        "--seed", type=int, default=None, help="Random seed for reproducible results"
    )
    parser.add_argument(
        "--save-grocery-list",
        type=str,
        default=None,
        help="Save grocery list to specified file path",
    )

    # Parse command line arguments
    args = parser.parse_args()

    # Set random seed if provided for reproducible results
    if args.seed is not None:
        random.seed(args.seed)
        print(f"Using random seed: {args.seed} (results will be reproducible)")

    try:
        # Convert recipe directory to Path object
        recipe_dir = Path(args.recipe_dir)

        # Generate weekly meal plan
        meals = plan_week(recipe_dir=recipe_dir)

        # Display the generated meal plan in a user-friendly format
        print("Generated weekly meal plan:")
        print("=" * 60)

        # Define the meal schedule for display
        meal_schedule = [
            ("Monday", "Dinner", (20, 40)),
            ("Tuesday", "Dinner", (20, 40)),
            ("Wednesday", "Dinner", (20, 40)),
            ("Thursday", "Dinner", (20, 40)),
            ("Friday", "Dinner", (20, 40)),
            ("Saturday", "Lunch", (30, 60)),
            ("Saturday", "Dinner", (60, 120)),
            ("Sunday", "Lunch", (30, 60)),
            ("Sunday", "Dinner", (30, 60)),
        ]

        # Display meals with their constraints
        for i, (day, meal_type, (active_time, total_time)) in enumerate(meal_schedule):
            meal = meals[i]

            # Format output differently for single vs. multiple recipe meals
            if len(meal) == 1:
                meal_str = meal[0]
            else:
                meal_str = " + ".join(meal)

            print(f"{day} {meal_type}: {meal_str}")

        # Extract all recipe names from the planned meals
        recipe_names = []
        for meal in meals:
            recipe_names.extend(meal)

        # Generate grocery list
        formatted_grocery_list = format_grocery_list(
            generate_grocery_list(recipe_dir, recipe_names)
        )

        # Always display grocery list
        print("\n" + formatted_grocery_list)

        # Save grocery list to file if requested
        if args.save_grocery_list:
            output_path = Path(args.save_grocery_list)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(formatted_grocery_list)
            print(f"\nGrocery list saved to: {output_path}")

        # Create calendar file automatically
        calendar_filename = "weekly_meal_plan.ics"
        print(f"\nCreating calendar file: {calendar_filename}")
        calendar_content = create_meal_calendar(meals, formatted_grocery_list)
        calendar_path = Path(calendar_filename)
        with open(calendar_path, "w", encoding="utf-8") as f:
            f.write(calendar_content)
        print(f"Calendar file created: {calendar_path}")
        print(
            "Import this file into your calendar app to see meal events and grocery shopping reminder."
        )

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
