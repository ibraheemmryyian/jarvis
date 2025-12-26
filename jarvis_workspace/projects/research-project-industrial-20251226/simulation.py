import numpy as np
from scipy.optimize import minimize_scalar

def predict_economic_viability(costs, benefits):
    """
    Predict the economic viability of an industrial symbiosis project.

    Args:
        costs (list): List of costs associated with the project.
        benefits (list): List of benefits associated with the project.

    Returns:
        dict: Dictionary containing the results of the economic viability prediction,
            including the break-even point and net present value.
    """
    total_costs = sum(costs)
    total_benefits = sum(benefits)

    def objective_function(scale):
        costs_with_discounting = [c * scale for c in costs]
        discounted_total_costs = sum(costs_with_discounting)
        
        return -1 * (total_benefits - discounted_total_costs)

    result = minimize_scalar(
        objective_function,
        bounds=(0, 1),
        method='bounded'
    )

    break_even_point = result.x
    net_present_value = total_benefits / (1 + break_even_point) ** len(costs)

    return {
        'break_even_point': break_even_point,
        'net_present_value': net_present_value
    }