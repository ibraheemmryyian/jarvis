import csv

def calculate_carbon_credits():
    """
    Calculate carbon credits for industrial symbiosis.
    
    Returns:
        A list of dictionaries containing the carbon credit data.
    """
    # Sample data (replace with actual data from research)
    projects = [
        {
            "name": "Project A",
            "waste_diverted_kg": 10000,
            "waste_valORIZED_kg": 5000,
            "incineration_tons": 2,
            "landfill_tons": 1
        },
        {
            "name": "Project B",
            "waste_diverted_kg": 15000,
            "waste_valORIZED_kg": 7500,
            "incineration_tons": 3,
            "landfill_tons": 2
        }
    ]
    
    # Calculate carbon credits based on waste diversion and valorization
    carbon_credits = []
    for project in projects:
        diverted_credits = project["waste_diverted_kg"] / 1000
        valorized_credits = project["waste_valORIZED_kg"] / 1000
        incineration_penalty = -project["incineration_tons"] * 1.5
        landfill_penalty = -project["landfill_tons"] * 2
        
        total_credits = diverted_credits + valorized_credits + incineration_penalty + landfill_penalty
        carbon_credits.append({"name": project["name"], "carbon_credits": total_credits})
    
    return carbon_credits

def save_to_csv(data, filename="results/carbon_credits.csv"):
    """
    Save the calculated carbon credit data to a CSV file.
    
    Args:
        data (list): A list of dictionaries containing the carbon credit data.
        filename (str): The path and name of the output CSV file.
    """
    with open(filename, "w", newline="") as csvfile:
        fieldnames = ["name", "carbon_credits"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for item in data:
            writer.writerow(item)

if __name__ == "__main__":
    carbon_credits_data = calculate_carbon_credits()
    save_to_csv(carbon_credits_data)