import numpy as np

def predict_economic_viability(input_data):
    """
    Predicts the economic viability of a waste-to-resource conversion project.
    
    Parameters:
        input_data (dict): Dictionary containing input features for the model.
        
    Returns:
        float: Economic viability score between 0 and 1.
    """
    
    # Input features
    waste_volume = input_data['waste_volume']
    resource_value = input_data['resource_value'] 
    conversion_cost = input_data['conversion_cost']
    market_price = input_data['market_price']
    
    # Calculate economic indicators
    revenue = resource_value * waste_volume
    cost = conversion_cost + (0.1 * conversion_cost)  # Include contingency
    
    # Predict viability
    if cost < revenue:
        viability = 1.0
    else:
        viability = 0.0
    
    return viability