from typing import List
from pathlib import Path

def plan_meal(recipe_dir: Path, active_cooking_time: int, total_time: int) -> List[str]:
    """
    Plan a meal with the given constraints.

    Args:
        recipe_dir (Path): Directory containing all the recipes.
        active_cooking_time (int): Maximum active cooking time.
        total_time (int): Maximum total time (including hands-off time).

    Returns:
        List[str]: List of recipes for the meal.
    """
    pass


def plan_menu(recipe_dir: Path,
        number_of_days: int,
        number_of_meals_per_day: int,
        active_cooking_time_per_day: int,
        total_time_per_day: int = 120) -> List[List[str]]:
    """
    Plan the menu for the week.

    Args:
        number_of_days (int): Number of days to plan the menu for.
        number_of_meals_per_day (int): Number of meals to plan per day.
        active_cooking_time_per_day (int): Maximum active cooking time per day.
        total_time_per_day (int): Maximum total time (including hands-off time) per day.

    Returns:
        List[List[str]]: List of meals for each day.
    """
    pass
