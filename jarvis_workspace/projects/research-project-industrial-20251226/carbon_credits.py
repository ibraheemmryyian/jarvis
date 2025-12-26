def calculate_carbon_credits(emissions):
    """
    Calculate the number of carbon credits based on CO2 emissions.

    Args:
        emissions (float): The total CO2 emissions in metric tons.

    Returns:
        int: The number of carbon credits.
    """
    # Carbon credit equivalency: 1 metric ton of CO2 = 1 carbon credit
    return int(emissions)