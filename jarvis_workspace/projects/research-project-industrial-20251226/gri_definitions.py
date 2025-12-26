from carbon_credit_analysis import load_gri_definitions

# Load the GRI definitions from a separate file or database
gri_definitions = load_gri_definitions()

# Print the GRI definitions to the console
for definition in gri_definitions:
    print(f"Definition: {definition['Term']}")
    print(f"Description: {definition['Description']}\n")