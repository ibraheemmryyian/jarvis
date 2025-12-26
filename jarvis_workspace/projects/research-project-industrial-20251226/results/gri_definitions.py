# Extracted definitions from Global Reporting Initiative (GRI) Standards for Waste Management (GRI 306)
gri_definitions = {
    'Diversion': "The reduction of waste going to landfill or incineration by diverting it to other forms of recovery.",
    'Valorization': "The conversion of waste into products or energy with economic value.",
    'Incineration': "The controlled combustion of waste at high temperatures, which can generate electricity and recover metals.",
    'Landfill': "The disposal of waste in a designated area that has been engineered and operated to isolate the waste from the surrounding environment."
}

def save_gri_definitions_to_csv(data, file_path):
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for key, value in data.items():
            writer.writerow([key, value])

save_gri_definitions_to_csv(gri_definitions, 'results/gri_definitions.csv')