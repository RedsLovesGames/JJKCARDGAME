import os
import pandas as pd
import numpy as np

# Define balance thresholds and energy scaling
BALANCE_THRESHOLD = 2.0
ENERGY_SCALING = {
    1: 150,
    2: 200,
    3: 300,
    4: 450,
    5: 650,
    6: 900
}

def calculate_card_strength(row):
    """Estimate a card's strength based on ATK, DEF, Cost and effects."""
    cost = row.get('Cost', 1)
    atk = row.get('ATK', 0)
    defense = row.get('DEF', 0)

    # Base strength calculation with weighted defense
    base_strength = atk + (defense * 0.6)
    expected_strength = ENERGY_SCALING.get(cost, 150)

    # Adjust for cost efficiency
    cost_modifier = 1 + (cost - 1) * 0.2

    # Effect strength calculation
    effect_modifier = 1.0
    effect = row.get('Effect', '')
    if isinstance(effect, str):
        effect_lower = effect.lower()
        if 'destroy' in effect_lower or 'negate' in effect_lower:
            effect_modifier *= 1.5
        if 'summon' in effect_lower:
            effect_modifier *= 1.4
        if 'heal' in effect_lower or 'restore' in effect_lower:
            effect_modifier *= 1.3
        if 'draw' in effect_lower:
            effect_modifier *= 1.35

    # Calculate final power ratio
    power_ratio = (base_strength * effect_modifier * cost_modifier) / expected_strength

    return power_ratio

def balance_card(row):
    """Apply balanced adjustments to card stats."""
    cost = row['Cost']
    power_ratio = row['Power Ratio']
    expected_total = ENERGY_SCALING.get(cost, 150)

    if power_ratio > BALANCE_THRESHOLD:
        reduction = 0.85 + (0.05 * cost)
        row['ATK'] = max(50, int(row['ATK'] * reduction))
        row['DEF'] = max(50, int(row['DEF'] * reduction))
    elif power_ratio < (1 / BALANCE_THRESHOLD):
        boost = 1.15 - (0.05 * cost)
        atk_def_ratio = row['ATK'] / (row['ATK'] + row['DEF']) if (row['ATK'] + row['DEF']) > 0 else 0.5
        total_stats = expected_total * boost
        row['ATK'] = int(total_stats * atk_def_ratio)
        row['DEF'] = int(total_stats * (1 - atk_def_ratio))

    min_stat = 50 * cost
    row['ATK'] = max(min_stat, row['ATK'])
    row['DEF'] = max(min_stat, row['DEF'])
    return row

def run_balance_analysis(file_path="characters.csv"):
    """Run balance analysis on the card data."""
    while True:  # Loop to keep the menu active
        print("\nJJK Card Game Balance Simulator")
        print("=" * 37)
        print("1. Balance Original Cards (characters.csv)")
        print("2. Re-balance Existing Balance (balanced_chars.csv)")
        print("3. View Current Balance Summary")
        print("4. Exit")

        choice = input("Enter your choice (1-4): ")
        
        if choice == '1':
            print("Loading original characters from characters.csv")
            # Call the function to balance original cards
            balance_original_cards(file_path)  # Replace with actual function call
        elif choice == '2':
            print("Re-balancing existing balance...")
            # Call the function to re-balance existing balance
            rebalance_existing_balance()  # Replace with actual function call
        elif choice == '3':
            print("Viewing current balance summary...")
            # Call the function to view current balance summary
            view_balance_summary()  # Replace with actual function call
        elif choice == '4':
            print("Exiting the program.")
            break  # Exit the loop
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")

def balance_original_cards(file_path):
    # Placeholder for the logic to balance original cards
    print(f"Balancing original cards from {file_path}...")
    # Add your balancing logic here

def rebalance_existing_balance():
    # Placeholder for the logic to re-balance existing balance
    print("Re-balancing existing balance...")
    # Add your re-balancing logic here

def view_balance_summary():
    # Placeholder for the logic to view current balance summary
    print("Current balance summary:")
    # Add your summary logic here

def main():
    print("\nJJK Card Game Balance Analyzer")
    print("=" * 30)
    
    while True:
        print("\n1. Analyze Original Cards")
        print("2. Analyze Balanced Cards")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ")
        
        if choice == "1":
            while True:
                try:
                    num_iterations = int(input("\nEnter number of iterations (minimum 1): "))
                    if num_iterations < 1:
                        print("Please enter a number greater than 0")
                        continue
                        
                    battles_per_iteration = int(input("Enter battles per iteration (minimum 5): "))
                    if battles_per_iteration < 5:
                        print("Please enter a number greater than 4")
                        continue
                        
                    break
                except ValueError:
                    print("Please enter valid numbers")
                    
            run_balance_analysis("characters.csv")
            
        elif choice == "2":
            if os.path.exists("balanced_chars.csv"):
                while True:
                    try:
                        num_iterations = int(input("\nEnter number of iterations (minimum 1): "))
                        if num_iterations < 1:
                            print("Please enter a number greater than 0")
                            continue
                            
                        battles_per_iteration = int(input("Enter battles per iteration (minimum 5): "))
                        if battles_per_iteration < 5:
                            print("Please enter a number greater than 4")
                            continue
                            
                        break
                    except ValueError:
                        print("Please enter valid numbers")
                        
                run_balance_analysis("balanced_chars.csv")
            else:
                print("\nError: balanced_chars.csv not found. Please analyze original cards first.")
        elif choice == "3":
            print("\nExiting...")
            break
        else:
            print("\nInvalid choice. Please enter a number between 1 and 3.")

if __name__ == "__main__":
    main()