def define_input_parameters():
    """
    Define the input parameters required for multi-industry material flow efficiency scoring.
    
    Returns:
        dict: A dictionary containing the defined input parameters.
    """
    return {
        "industries": [
            {"name": "Manufacturing", "description": "A sector involved in the production of goods."}, 
            {"name": "Construction", "description": "A sector focused on building projects."},
            # Add more industries as needed
        ],
        "materials": [
            {"name": "Plastic", "description": "A synthetic material used for various applications"},
            {"name": "Metal", "description": "A class of chemical elements with metallic properties"},
            # Add more materials as needed
        ],
        "waste_management_options": {
            "diversion": {"definition": "The act of diverting waste from traditional disposal methods.", 
                         "metrics": ["amount_diverted", "diversion_rate"]},
            "valorization": {"definition": "The process of converting waste into a valuable product.",
                            "metrics": ["valorized_waste_amount", "valorization_rate"]},
            "incineration": {"definition": "The process of burning waste to generate energy.", 
                            "metrics": ["energy_generated", "emissions_reduction"]},
            "landfill": {"definition": "The disposal of waste in a landfill site.", 
                        "metrics": ["waste_disposed", "landfill_area"]}
        },
        # Add more parameters as needed
    }