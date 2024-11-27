from functools import lru_cache
import numpy as np

DICE_MAX = 20
DICE_TYPES = [4, 6, 8, 10, 12, 20]

def generate_combinations():
    combinations = []

    for number_of_dice in range(1, DICE_MAX + 1):
        combinations.extend(generate_combinations_for_number_of_dice(number_of_dice))

    return combinations

@lru_cache(None)
def generate_combinations_for_number_of_dice(remaining_dice, start_index=0):
    if remaining_dice == 0:
        return [[]]

    combinations = []
    for i in range(start_index, len(DICE_TYPES)):
        for number_of_to_add in range(1, remaining_dice + 1):
            for combo in generate_combinations_for_number_of_dice(remaining_dice - number_of_to_add, i + 1):
                combinations.append([DICE_TYPES[i]] * number_of_to_add + combo)

    return combinations

def get_generating_function(dice_combo):
    dice_counts = {dice: dice_combo.count(dice) for dice in set(dice_combo)}
    final_convolution = None

    for dice_type, count in dice_counts.items():
        total_die_type_polynomial_coefficients = [1] * dice_type

        for _ in range(1, count):
            total_die_type_polynomial_coefficients = np.convolve(total_die_type_polynomial_coefficients, [1] * dice_type)

        if final_convolution is None:
            final_convolution = total_die_type_polynomial_coefficients
        else:
            final_convolution = np.convolve(
                final_convolution, total_die_type_polynomial_coefficients
            )

    return final_convolution

def calculate_probability(polynomial_coefficients, target, number_of_dice):
    total_combinations = np.sum(polynomial_coefficients, dtype=np.float64)
    if number_of_dice == 1:
        return (total_combinations - target + 1) / total_combinations

    successful_combinations = np.float64(0)
    for i in range(target - number_of_dice, len(polynomial_coefficients)):
        successful_combinations += polynomial_coefficients[i]

    return successful_combinations / total_combinations

def find_target_roll(polynomial_coefficients, dice_combo, target_probability, valid_combinations):
    max_roll = sum(dice_combo)
    min_roll = len(dice_combo)

    while min_roll <= max_roll:
        current_roll = (min_roll + max_roll) // 2
        probability = calculate_probability(polynomial_coefficients, current_roll, len(dice_combo))

        if probability == target_probability:
            valid_combinations.append({"dice": dice_combo, "target": current_roll})
            break
        elif probability < target_probability:
            max_roll = current_roll - 1
        else:
            min_roll = current_roll + 1

def print_combinations_found(combinations):
    if not combinations:
        print("\nNo combinations found.")
        return

    print(f"\nFound {len(combinations)} dice combinations:")
    for i, result in enumerate(combinations):
        dice_str = " + ".join(f"d{dice}" for dice in result["dice"])
        print(f"{i + 1}.")
        print(f"    Total Dice: {len(result['dice'])}")
        print(f"    Combination: {dice_str}")
        print(f"    Target Number: {result['target']}\n")

def find_dice_probability_combinations(target_probability):
    print("\nStart...\n")
    valid_combinations = []

    all_combos = generate_combinations()
    print(f"{len(all_combos)} combinations generated.\n")

    number_of_dice = 1
    print("Checking combinations with 1 die.")
    for dice_combo in all_combos:
        if valid_combinations and len(dice_combo) > len(valid_combinations[0]["dice"]):
            break
        if len(dice_combo) > number_of_dice:
            number_of_dice = len(dice_combo)
            print(f"Checking combinations with {number_of_dice} dice.")

        polynomial_coefficients = get_generating_function(dice_combo)
        find_target_roll(polynomial_coefficients, dice_combo, target_probability, valid_combinations)

    print_combinations_found(valid_combinations)


find_dice_probability_combinations(2/9)