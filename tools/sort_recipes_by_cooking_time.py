#!/usr/bin/env python3
"""
Recipe Sorting Script

This script analyzes recipe markdown files in the recipes folder and sorts them
by active cooking time, outputting the results to a YAML file.
"""

import os
import re
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def parse_cooking_time(time_str: str) -> int:
    """
    Parse cooking time string and return minutes as integer.

    Args:
        time_str: String like "10 minutes", "1 hour", "1.5 hours", "2 days", etc.

    Returns:
        Total minutes as integer
    """
    if not time_str:
        return 0

    # Remove extra whitespace and convert to lowercase
    time_str = time_str.strip().lower()

    # Extract numbers (including decimals)
    numbers = re.findall(r'\d+\.?\d*', time_str)
    if not numbers:
        return 0

    total_minutes = 0

    # Handle days
    if 'day' in time_str:
        days = float(numbers[0])
        total_minutes += int(days * 24 * 60)  # Convert days to minutes
        # If there are additional numbers, they might be hours or minutes
        if len(numbers) > 1:
            if 'hour' in time_str:
                total_minutes += int(float(numbers[1]) * 60)
            elif 'min' in time_str:
                total_minutes += int(float(numbers[1]))
    # Handle hours
    elif 'hour' in time_str:
        hours = float(numbers[0])
        total_minutes += int(hours * 60)
        # If there are additional numbers, they might be minutes
        if len(numbers) > 1 and 'min' in time_str:
            total_minutes += int(float(numbers[1]))
    # Handle minutes only
    elif 'min' in time_str:
        total_minutes = int(float(numbers[0]))
    else:
        # Default to minutes if no unit specified
        total_minutes = int(float(numbers[0]))

    return total_minutes


def extract_tags_from_line(line: str) -> List[str]:
    """
    Extract hashtags from a line.
    
    Args:
        line: Line that may contain hashtags like "#Vegetables #Protein"
    
    Returns:
        List of tag names (without the # symbol)
    """
    tags = re.findall(r'#(\w+)', line)
    return tags


def filter_relevant_tags(tags: List[str]) -> List[str]:
    """
    Filter tags to only keep Vegetables, Protein, or Vegetables_Protein tags.

    Args:
        tags: List of tag strings

    Returns:
        List of relevant tags only
    """
    relevant_tags = []
    for tag in tags:
        if tag.lower() in ['vegetables', 'protein', 'vegetables_protein']:
            relevant_tags.append(tag)

    return relevant_tags


def parse_recipe_file(file_path: Path) -> Optional[Dict]:
    """
    Parse a single recipe markdown file.
    
    Args:
        file_path: Path to the recipe file
    
    Returns:
        Dictionary with recipe information or None if parsing fails
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # Extract recipe name from first line (assuming it's a markdown header)
        recipe_name = ""
        tags = []
        active_time = 0
        total_time = 0
        
        for line in lines:
            line = line.strip()
            
            # Extract recipe name from first header
            if line.startswith('# ') and not recipe_name:
                recipe_name = line[2:].strip()
            
            # Extract tags (lines starting with #)
            elif line.startswith('#') and not line.startswith('# ') and not line.startswith('## '):
                tags.extend(extract_tags_from_line(line))
            
            # Extract cooking times
            elif 'active cooking time:' in line.lower():
                time_match = re.search(r'active cooking time:\s*(.+)', line, re.IGNORECASE)
                if time_match:
                    active_time = parse_cooking_time(time_match.group(1))
            
            elif ('total cooking time:' in line.lower() or 
                  'ready in:' in line.lower()):
                # Handle both "Total Cooking Time:" and "Ready in:" formats
                time_match = re.search(r'(?:total cooking time|ready in):\s*(.+)', line, re.IGNORECASE)
                if time_match:
                    time_str = time_match.group(1)
                    # Remove parenthetical information like "(plus overnight marination)"
                    time_str = re.sub(r'\s*\([^)]+\)', '', time_str)
                    total_time = parse_cooking_time(time_str)
        
        if not recipe_name:
            recipe_name = file_path.stem.replace('_', ' ').title()

        # Filter tags to only keep relevant ones
        relevant_tags = filter_relevant_tags(tags)

        return {
            'name': recipe_name,
            'active_cooking_time_minutes': active_time,
            'total_cooking_time_minutes': total_time,
            'tags': relevant_tags,
            'file_path': str(file_path)
        }
    
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return None


def find_recipe_files(recipes_dir: Path) -> List[Path]:
    """
    Find all markdown recipe files in the recipes directory.
    
    Args:
        recipes_dir: Path to the recipes directory
    
    Returns:
        List of paths to recipe files
    """
    recipe_files = []
    
    for root, _, files in os.walk(recipes_dir):
        for file in files:
            if file.endswith('.md'):
                recipe_files.append(Path(root) / file)
    
    return recipe_files


def main(verbose: int = 1):
    """Main function to process recipes and generate sorted YAML output.

    Args:
        verbose: Verbosity level (0=quiet, 1=normal, 2=verbose)
    """
    
    # Search all recipes in the recipes folder
    recipes_dir = Path('recipes')
    output_file = recipes_dir / 'sorted_recipes_by_cooking_time.yaml'
    
    if not recipes_dir.exists():
        print(f"Error: Recipes directory '{recipes_dir}' not found!")
        return

    recipe_files = find_recipe_files(recipes_dir)
    if verbose >= 1:
        print(f"Found {len(recipe_files)} recipe files")

    # Parse all recipes for cooking times
    recipes = []
    for file_path in recipe_files:
        recipe_data = parse_recipe_file(file_path)
        if recipe_data:
            recipes.append(recipe_data)
            if verbose >= 2:
                print(f"Parsed: {recipe_data['name']} - Active: {recipe_data['active_cooking_time_minutes']}min")
    
    # Sort recipes by active cooking time, then by total cooking time
    recipes.sort(key=lambda x: (x['active_cooking_time_minutes'], x['total_cooking_time_minutes']))
    
    output_data = {
        'sorted_recipes_by_active_cooking_time': recipes,
        'summary': {
            'total_recipes': len(recipes),
            'active_cooking_time_range': {
                'min_minutes': min(r['active_cooking_time_minutes'] for r in recipes) if recipes else 0,
                'max_minutes': max(r['active_cooking_time_minutes'] for r in recipes) if recipes else 0
            }
        }
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("sorted_recipes_by_active_cooking_time:\n")
        # Summarize each recipe in a YAML list
        for recipe in recipes:
            f.write(f"  - name: \"{recipe['name']}\"\n")
            f.write(f"    active_cooking_time_minutes: {recipe['active_cooking_time_minutes']}\n")
            f.write(f"    total_cooking_time_minutes: {recipe['total_cooking_time_minutes']}\n")
            f.write(f"    tags: {recipe['tags']}\n")
            f.write(f"    file_path: \"{recipe['file_path']}\"\n")

        f.write("\nsummary:\n")
        f.write(f"  total_recipes: {output_data['summary']['total_recipes']}\n")
        f.write("  active_cooking_time_range:\n")
        f.write(f"    min_minutes: {output_data['summary']['active_cooking_time_range']['min_minutes']}\n")
        f.write(f"    max_minutes: {output_data['summary']['active_cooking_time_range']['max_minutes']}\n")
    
    if verbose >= 1:
        print(f"\nSorted recipes saved to: {output_file}")
        print(f"Total recipes processed: {len(recipes)}")
        print(f"Active cooking time range: {output_data['summary']['active_cooking_time_range']['min_minutes']}-{output_data['summary']['active_cooking_time_range']['max_minutes']} minutes")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Sort recipes by active cooking time and generate YAML output",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Verbosity levels:
  0 - Quiet mode (no output except errors)
  1 - Normal mode (default, shows summary)
  2 - Verbose mode (shows each recipe being parsed)
        """
    )
    parser.add_argument(
        '-v', '--verbose',
        type=int,
        choices=[0, 1, 2],
        default=1,
        help='Set verbosity level (0=quiet, 1=normal, 2=verbose)'
    )

    args = parser.parse_args()
    main(verbose=args.verbose)
