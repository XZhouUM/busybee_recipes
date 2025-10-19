#!/usr/bin/env python3
"""
Grocery Shopping List Generator

This script generates a consolidated grocery shopping list from a list of recipe names.
It parses through the ingredients of each recipe and consolidates them with quantities.

USAGE AS A LIBRARY:
==================

from pathlib import Path
from tools.generate_grocery_list import generate_grocery_list

# Generate grocery list from recipe names
recipe_dir = Path(".")
recipe_names = ["Firm Tofu", "Fried Beef", "Egg Drop Soup"]
grocery_list = generate_grocery_list(recipe_dir, recipe_names)

# grocery_list will be a dictionary like:
# {
#   'Firm tofu': (1.0, 'block'),
#   'Soy sauce': (3.0, 'tablespoon'),
#   'Beef': (350.0, 'gram'),
#   'Egg': (1.0, 'unit'),
#   ...
# }

USAGE AS COMMAND LINE TOOL:
===========================

# Generate grocery list from specific recipes
python tools/generate_grocery_list.py "Firm Tofu" "Fried Beef" "Egg Drop Soup"

# Generate grocery list and save to file
python tools/generate_grocery_list.py "Firm Tofu" "Fried Beef" --output grocery_list.txt

# Show help
python tools/generate_grocery_list.py --help

INGREDIENT PARSING:
==================

The script parses ingredients from markdown recipe files in the format:
- Ingredient name [quantity] (optional notes)

Examples:
- Firm tofu [1 block]
- Soy sauce [2 tablespoons]
- Garlic [1 clove]
- Hot pepper sauce (no quantity specified)

CONSOLIDATION LOGIC:
===================

1. Extracts ingredients from each recipe file
2. Groups identical ingredient names together
3. Automatically combines quantities with the same units (e.g., "1 tablespoon" + "2 tablespoons" = "3 tablespoons")
4. Handles ingredients without specified quantities
5. Returns consolidated quantities as (value, unit) tuples
6. Filters out unwanted ingredients (e.g., water)
7. Sorts ingredients by priority: numerical quantities first, "as needed" second, small amounts last
8. Provides a clean, organized shopping list

REQUIREMENTS:
=============

- recipes/sorted_recipes_by_cooking_time.yaml file must exist
- Recipe markdown files must exist in their specified paths
- Python packages: pathlib, typing, re, argparse, yaml
"""

import argparse
import re
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml


def parse_ingredient_line(line: str) -> Optional[Tuple[str, str]]:
    """
    Parse a single ingredient line to extract ingredient name and quantity.

    Args:
        line (str): Raw ingredient line from markdown file

    Returns:
        Optional[Tuple[str, str]]: (ingredient_name, quantity) or None if not an ingredient
    """
    # Remove leading/trailing whitespace and markdown list markers
    line = line.strip().lstrip("- ").strip()

    # Skip empty lines or non-ingredient lines
    if not line or line.startswith("#") or line.startswith("##"):
        return None

    # Pattern to match: ingredient_name [quantity] (optional_notes)
    # Examples: "Firm tofu [1 block]", "Hot pepper sauce", "Garlic [1 clove] (optional)"
    pattern = r"^([^[\(]+?)(?:\s*\[([^\]]+)\])?(?:\s*\([^)]+\))?(?:\s*\[optional\])?$"
    match = re.match(pattern, line, re.IGNORECASE)

    if match:
        ingredient_name = match.group(1).strip()
        quantity = match.group(2).strip() if match.group(2) else "as needed"
        return (ingredient_name, quantity)

    return None


def parse_quantity(quantity_str: str) -> Tuple[float, str]:
    """
    Parse a quantity string to extract numeric value and unit.

    Args:
        quantity_str (str): Quantity string like "1 block", "2 tablespoons", "0.5 cup"

    Returns:
        Tuple[float, str]: (numeric_value, unit) or (0.0, quantity_str) if parsing fails
    """
    if not quantity_str or quantity_str.strip().lower() == "as needed":
        return (0.0, "as needed")

    # Handle complex quantities like "1 tablespoon + 1 teaspoon"
    if "+" in quantity_str:
        parts = quantity_str.split("+")
        total_value = 0.0
        main_unit = ""

        for part in parts:
            part = part.strip()
            value, unit = parse_quantity(part)
            if main_unit == "":
                main_unit = unit
            # Convert to main unit if possible (basic conversions)
            if unit == "teaspoon" and main_unit == "tablespoon":
                value = value / 3  # 3 teaspoons = 1 tablespoon
            elif unit == "tablespoon" and main_unit == "teaspoon":
                main_unit = "tablespoon"
                total_value = (
                    total_value / 3
                )  # Convert previous teaspoons to tablespoons

            total_value += value

        return (total_value, main_unit)

    # Regular expression to match number and unit
    # Handles: "1 block", "2.5 cups", "0.5 tablespoon", "350 grams"
    pattern = r"^(\d*\.?\d+(?:/\d+)?)\s*(.*)$"
    match = re.match(pattern, quantity_str.strip())

    if match:
        value_str = match.group(1)
        unit = match.group(2).strip()

        # Handle fractions like "1/2"
        if "/" in value_str:
            try:
                value = float(Fraction(value_str))
            except:
                value = 0.0
        else:
            try:
                value = float(value_str)
            except:
                value = 0.0

        # Normalize units (convert plural to singular)
        unit = normalize_unit(unit)

        return (value, unit)

    # If parsing fails, return the original string as unit with 0 value
    return (0.0, quantity_str.strip())


def normalize_unit(unit: str) -> str:
    """
    Normalize unit names to singular form for consistent aggregation.

    Args:
        unit (str): Unit name like "tablespoons", "grams", "units"

    Returns:
        str: Normalized unit name
    """
    unit = unit.lower().strip()

    # Basic normalization by removing trailing 's' if exists.
    if unit.endswith("s"):
        unit = unit[:-1]

    return unit


def combine_quantities(quantities: List[str]) -> Tuple[float, str]:
    """
    Combine a list of quantity strings with the same ingredient.

    Args:
        quantities (List[str]): List of quantity strings for the same ingredient

    Returns:
        Tuple[float, str]: Combined (total_value, unit) or (0.0, "mixed units") if units differ
    """
    if not quantities:
        return (0.0, "as needed")

    # Parse all quantities
    parsed_quantities = [parse_quantity(q) for q in quantities]

    # Group by unit
    unit_groups = {}
    for value, unit in parsed_quantities:
        if unit not in unit_groups:
            unit_groups[unit] = []
        unit_groups[unit].append(value)

    # If all quantities have the same unit, sum them
    if len(unit_groups) == 1:
        unit = list(unit_groups.keys())[0]
        total_value = sum(unit_groups[unit])
        return (total_value, unit)

    # If there are multiple units, try to find the most common one
    # or return the first non-zero unit with total
    main_unit = ""
    main_total = 0.0

    for unit, values in unit_groups.items():
        total = sum(values)
        if unit != "as needed" and (main_unit == "" or total > main_total):
            main_unit = unit
            main_total = total

    if main_unit:
        return (main_total, main_unit)

    # Fallback: return "mixed units" if we can't consolidate
    return (0.0, "mixed units")


def filter_ingredients(
    grocery_list: Dict[str, Tuple[float, str]],
) -> Dict[str, Tuple[float, str]]:
    """
    Remove unwanted ingredients from the grocery list.

    Args:
        grocery_list (Dict[str, Tuple[float, str]]): Original grocery list

    Returns:
        Dict[str, Tuple[float, str]]: Filtered grocery list with unwanted ingredients removed
    """
    # List of ingredients to filter out (case-insensitive)
    ingredients_to_remove = {"water", "drinking water"}

    filtered_list = {}
    for ingredient_name, quantity_tuple in grocery_list.items():
        if ingredient_name.lower() not in ingredients_to_remove:
            filtered_list[ingredient_name] = quantity_tuple

    return filtered_list


def sort_grocery_list(
    grocery_list: Dict[str, Tuple[float, str]],
) -> Dict[str, Tuple[float, str]]:
    """
    Sort the grocery list by priority: numerical quantities first, "as needed" second, small amounts last.

    Args:
        grocery_list (Dict[str, Tuple[float, str]]): Unsorted grocery list

    Returns:
        Dict[str, Tuple[float, str]]: Sorted grocery list
    """

    def get_sort_priority(item):
        ingredient_name, (value, unit) = item

        # Priority 1: Items with numerical quantities (value > 0 and not special units)
        if value > 0 and unit not in ["as needed"] and not is_small_amount_unit(unit):
            return (1, ingredient_name.lower())

        # Priority 2: Items marked as "as needed"
        elif unit == "as needed":
            return (2, ingredient_name.lower())

        # Priority 3: Small amounts (pinch, hint, handful, etc.)
        else:
            return (3, ingredient_name.lower())

    # Sort items by priority, then alphabetically within each priority
    sorted_items = sorted(grocery_list.items(), key=get_sort_priority)

    # Convert back to dictionary (preserving order in Python 3.7+)
    return dict(sorted_items)


def is_small_amount_unit(unit: str) -> bool:
    """
    Check if a unit represents a small/imprecise amount.

    Args:
        unit (str): Unit name to check

    Returns:
        bool: True if the unit represents a small/imprecise amount
    """
    small_amount_units = {
        "pinch",
        "hint",
        "handful",
        "a handful",
        "a pinch",
        "a hint",
        "dash",
        "splash",
        "sprinkle",
        "to taste",
    }
    return unit.lower() in small_amount_units


def extract_ingredients_from_recipe(recipe_file_path: Path) -> Dict[str, List[str]]:
    """
    Extract ingredients from a single recipe markdown file.

    Args:
        recipe_file_path (Path): Path to the recipe markdown file

    Returns:
        Dict[str, List[str]]: Dictionary mapping ingredient names to list of quantities
    """
    ingredients = {}

    try:
        with open(recipe_file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Find the ingredients section
        lines = content.split("\n")
        in_ingredients_section = False

        for line in lines:
            # Check if we're entering the ingredients section
            if line.strip().lower() == "## ingredients":
                in_ingredients_section = True
                continue

            # Check if we're leaving the ingredients section (next ## section)
            if (
                in_ingredients_section
                and line.strip().startswith("## ")
                and line.strip().lower() != "## ingredients"
            ):
                break

            # Parse ingredient lines
            if in_ingredients_section:
                parsed = parse_ingredient_line(line)
                if parsed:
                    ingredient_name, quantity = parsed
                    # Normalize ingredient name (title case)
                    ingredient_name = ingredient_name.title()

                    if ingredient_name not in ingredients:
                        ingredients[ingredient_name] = []
                    ingredients[ingredient_name].append(quantity)

    except FileNotFoundError:
        print(f"Warning: Recipe file not found: {recipe_file_path}")
    except Exception as e:
        print(f"Warning: Error reading recipe file {recipe_file_path}: {e}")

    return ingredients


def load_recipe_paths(recipe_dir: Path) -> Dict[str, str]:
    """
    Load recipe name to file path mapping from the YAML file.

    Args:
        recipe_dir (Path): Directory containing the recipes

    Returns:
        Dict[str, str]: Mapping of recipe names to file paths
    """
    yaml_file = recipe_dir / "recipes" / "sorted_recipes_by_cooking_time.yaml"

    try:
        with open(yaml_file, "r") as f:
            data = yaml.safe_load(f)

        recipe_paths = {}
        for recipe in data["sorted_recipes_by_active_cooking_time"]:
            recipe_paths[recipe["name"]] = recipe["file_path"]

        return recipe_paths

    except FileNotFoundError:
        raise FileNotFoundError(f"Recipe database not found: {yaml_file}")
    except Exception as e:
        raise Exception(f"Error loading recipe database: {e}")


def generate_grocery_list(
    recipe_dir: Path, recipe_names: List[str]
) -> Dict[str, Tuple[float, str]]:
    """
    Generate a consolidated grocery shopping list from recipe names.

    Args:
        recipe_dir (Path): Directory containing the recipes
        recipe_names (List[str]): List of recipe names to include

    Returns:
        Dict[str, Tuple[float, str]]: Consolidated grocery list with ingredient names and combined quantities as (value, unit) tuples
    """
    # Load recipe name to file path mapping
    recipe_paths = load_recipe_paths(recipe_dir)

    # Consolidated grocery list (temporarily store as lists, then combine)
    temp_grocery_list = {}

    # Process each recipe
    for recipe_name in recipe_names:
        if recipe_name not in recipe_paths:
            print(f"Warning: Recipe '{recipe_name}' not found in database")
            continue

        recipe_file_path = recipe_dir / recipe_paths[recipe_name]
        recipe_ingredients = extract_ingredients_from_recipe(recipe_file_path)

        # Merge ingredients into temporary grocery list
        for ingredient_name, quantities in recipe_ingredients.items():
            if ingredient_name not in temp_grocery_list:
                temp_grocery_list[ingredient_name] = []
            temp_grocery_list[ingredient_name].extend(quantities)

    # Convert to final format with combined quantities
    grocery_list = {}
    for ingredient_name, quantities in temp_grocery_list.items():
        combined_value, combined_unit = combine_quantities(quantities)
        grocery_list[ingredient_name] = (combined_value, combined_unit)

    # Filter out unwanted ingredients
    grocery_list = filter_ingredients(grocery_list)

    # Sort the grocery list by priority
    grocery_list = sort_grocery_list(grocery_list)

    return grocery_list


def format_grocery_list(grocery_list: Dict[str, Tuple[float, str]]) -> str:
    """
    Format the grocery list for display or saving.

    Args:
        grocery_list (Dict[str, Tuple[float, str]]): Consolidated grocery list with combined quantities

    Returns:
        str: Formatted grocery list as a string
    """
    if not grocery_list:
        return "No ingredients found."

    output_lines = ["GROCERY SHOPPING LIST", "=" * 50, ""]

    # Sort ingredients alphabetically
    for ingredient_name in grocery_list.keys():
        value, unit = grocery_list[ingredient_name]

        # Format the quantity display
        if unit == "as needed":
            output_lines.append(f"• {ingredient_name}: as needed")
        elif unit == "mixed units":
            output_lines.append(f"• {ingredient_name}: mixed units (check recipes)")
        elif value == 0.0:
            output_lines.append(f"• {ingredient_name}: {unit}")
        else:
            # Format the number nicely (remove .0 for whole numbers)
            if value == int(value):
                formatted_value = str(int(value))
            else:
                formatted_value = str(value)

            output_lines.append(f"• {ingredient_name}: {formatted_value} {unit}")

    output_lines.extend(["", f"Total ingredients: {len(grocery_list)}"])

    return "\n".join(output_lines)


def main():
    """
    Main function to run the grocery list generator from command line.

    Command line arguments:
    - recipe_names: List of recipe names to include (positional arguments)
    - --recipe-dir: Path to directory containing recipe files (default: current directory)
    - --output: Output file path to save the grocery list (optional)

    Examples:
    python tools/generate_grocery_list.py "Firm Tofu" "Fried Beef" "Egg Drop Soup"
    python tools/generate_grocery_list.py "Curry Rice" --output my_grocery_list.txt
    """
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(
        description="Generate a consolidated grocery shopping list from recipe names",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "Firm Tofu" "Fried Beef" "Egg Drop Soup"
  %(prog)s "Curry Rice" "Chinese Salad" --output grocery_list.txt
  %(prog)s "Tomato Hot Pot" --recipe-dir /path/to/recipes
        """,
    )

    # Define command line arguments
    parser.add_argument(
        "recipe_names",
        nargs="+",
        help="Names of recipes to include in the grocery list",
    )
    parser.add_argument(
        "--recipe-dir",
        type=str,
        default=".",
        help="Directory containing the recipes (default: current directory)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path to save the grocery list (optional)",
    )

    # Parse command line arguments
    args = parser.parse_args()

    try:
        # Convert recipe directory to Path object
        recipe_dir = Path(args.recipe_dir)

        # Generate grocery list
        print(f"Generating grocery list for {len(args.recipe_names)} recipes...")
        grocery_list = generate_grocery_list(recipe_dir, args.recipe_names)

        # Format the grocery list
        formatted_list = format_grocery_list(grocery_list)

        # Output the grocery list
        if args.output:
            # Save to file
            output_path = Path(args.output)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(formatted_list)
            print(f"Grocery list saved to: {output_path}")
            print(f"Found {len(grocery_list)} unique ingredients")
        else:
            # Print to console
            print("\n" + formatted_list)

        # Show recipe summary
        print(f"\nRecipes processed:")
        for recipe_name in args.recipe_names:
            print(f"  • {recipe_name}")

    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
