def run_simulation(previous_data, current_params):
    # Initialize results dictionary
    results = {
        'incineration': 0,
        'landfill': 0,
        'valorization': 0
    }

    # Loop through each waste management option
    for option in previous_data:
        tonnes = previous_data[option][0]
        cost_per_tonne = current_params[f'{option}_cost_per_tonne']

        # Calculate the net benefit of the waste management option 
        net_benefit = (tonnes * current_params['waste_diversion_rate'] *
                       current_params['recycling_efficiency'] -
                       tonnes * cost_per_tonne)

        # Update results with the net benefit for this option
        results[option] += net_benefit

    return results