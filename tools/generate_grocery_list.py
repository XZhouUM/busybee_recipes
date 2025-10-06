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
#   'Firm tofu': ['1 block'],
#   'Soy sauce': ['1 tablespoon', '2 tablespoons'],
#   'Beef': ['350 grams'],
#   'Egg': ['1 unit'],
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
3. Preserves all quantity specifications for manual consolidation
4. Handles ingredients without specified quantities
5. Provides a clean, organized shopping list

REQUIREMENTS:
=============

- recipes/sorted_recipes_by_cooking_time.yaml file must exist
- Recipe markdown files must exist in their specified paths
- Python packages: pathlib, typing, re, argparse, yaml
"""

from typing import List, Dict, Tuple, Optional
from pathlib import Path
import re
import argparse
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
    line = line.strip().lstrip('- ').strip()
    
    # Skip empty lines or non-ingredient lines
    if not line or line.startswith('#') or line.startswith('##'):
        return None
    
    # Pattern to match: ingredient_name [quantity] (optional_notes)
    # Examples: "Firm tofu [1 block]", "Hot pepper sauce", "Garlic [1 clove] (optional)"
    pattern = r'^([^[\(]+?)(?:\s*\[([^\]]+)\])?(?:\s*\([^)]+\))?(?:\s*\[optional\])?$'
    match = re.match(pattern, line, re.IGNORECASE)
    
    if match:
        ingredient_name = match.group(1).strip()
        quantity = match.group(2).strip() if match.group(2) else "as needed"
        return (ingredient_name, quantity)
    
    return None


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
        with open(recipe_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the ingredients section
        lines = content.split('\n')
        in_ingredients_section = False
        
        for line in lines:
            # Check if we're entering the ingredients section
            if line.strip().lower() == '## ingredients':
                in_ingredients_section = True
                continue
            
            # Check if we're leaving the ingredients section (next ## section)
            if in_ingredients_section and line.strip().startswith('## ') and line.strip().lower() != '## ingredients':
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
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)
        
        recipe_paths = {}
        for recipe in data['sorted_recipes_by_active_cooking_time']:
            recipe_paths[recipe['name']] = recipe['file_path']
        
        return recipe_paths
    
    except FileNotFoundError:
        raise FileNotFoundError(f"Recipe database not found: {yaml_file}")
    except Exception as e:
        raise Exception(f"Error loading recipe database: {e}")


def generate_grocery_list(recipe_dir: Path, recipe_names: List[str]) -> Dict[str, List[str]]:
    """
    Generate a consolidated grocery shopping list from recipe names.
    
    Args:
        recipe_dir (Path): Directory containing the recipes
        recipe_names (List[str]): List of recipe names to include
        
    Returns:
        Dict[str, List[str]]: Consolidated grocery list with ingredient names and quantities
    """
    # Load recipe name to file path mapping
    recipe_paths = load_recipe_paths(recipe_dir)
    
    # Consolidated grocery list
    grocery_list = {}
    
    # Process each recipe
    for recipe_name in recipe_names:
        if recipe_name not in recipe_paths:
            print(f"Warning: Recipe '{recipe_name}' not found in database")
            continue
        
        recipe_file_path = recipe_dir / recipe_paths[recipe_name]
        recipe_ingredients = extract_ingredients_from_recipe(recipe_file_path)
        
        # Merge ingredients into grocery list
        for ingredient_name, quantities in recipe_ingredients.items():
            if ingredient_name not in grocery_list:
                grocery_list[ingredient_name] = []
            grocery_list[ingredient_name].extend(quantities)
    
    return grocery_list


def format_grocery_list(grocery_list: Dict[str, List[str]]) -> str:
    """
    Format the grocery list for display or saving.
    
    Args:
        grocery_list (Dict[str, List[str]]): Consolidated grocery list
        
    Returns:
        str: Formatted grocery list as a string
    """
    if not grocery_list:
        return "No ingredients found."
    
    output_lines = ["GROCERY SHOPPING LIST", "=" * 50, ""]
    
    # Sort ingredients alphabetically
    for ingredient_name in sorted(grocery_list.keys()):
        quantities = grocery_list[ingredient_name]
        
        # Remove duplicates while preserving order
        unique_quantities = []
        for qty in quantities:
            if qty not in unique_quantities:
                unique_quantities.append(qty)
        
        if len(unique_quantities) == 1:
            output_lines.append(f"• {ingredient_name}: {unique_quantities[0]}")
        else:
            output_lines.append(f"• {ingredient_name}:")
            for qty in unique_quantities:
                output_lines.append(f"  - {qty}")
    
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
        description='Generate a consolidated grocery shopping list from recipe names',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "Firm Tofu" "Fried Beef" "Egg Drop Soup"
  %(prog)s "Curry Rice" "Chinese Salad" --output grocery_list.txt
  %(prog)s "Tomato Hot Pot" --recipe-dir /path/to/recipes
        """
    )

    # Define command line arguments
    parser.add_argument('recipe_names', nargs='+',
                        help='Names of recipes to include in the grocery list')
    parser.add_argument('--recipe-dir', type=str, default='.',
                        help='Directory containing the recipes (default: current directory)')
    parser.add_argument('--output', type=str, default=None,
                        help='Output file path to save the grocery list (optional)')

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
            with open(output_path, 'w', encoding='utf-8') as f:
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
