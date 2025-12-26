# Input Parameters for Carbon Credit Calculation Framework

class CarbonCreditCalculationInputParams:
    def __init__(self):
        self.emissions_data = "path/to/emissions_data.csv"  # CSV file containing emissions data
        self.carbon_price = 50.0  # Price of carbon in USD per metric tonne
        self.project_lifetime_years = 10  # Lifetime of the project in years
        self.inflation_rate = 2.5  # Annual inflation rate for discounting future costs
        self.discount_rate = 5  # Discount rate for present value calculations
        self.energy_mix_data = "path/to/energy_mix_data.csv"  # CSV file containing energy mix data
        self.industrial_processes_data = "path/to/industrial_processes_data.json"  # JSON file containing industrial processes and their emissions factors
        self.waste_management_options = {
            'diversion': 'path/to/diversion_data.csv', 
            'valorization': 'path/to/valorization_data.csv',
            'incineration': 'path/to/incineration_data.csv',
            'landfill': 'path/to/landfill_data.csv'
        }  # Data files for different waste management options