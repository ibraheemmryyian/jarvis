# Novel concept in industrial symbiosis: Regional collaboration
regional_collaboration = {
    'Objective': "To maximize resource efficiency and minimize waste through regional cooperation.",
    'Strategy': [
        "Identify synergies between industries within a region",
        "Establish material exchange programs",
        "Implement shared infrastructure for waste processing"
    ],
    'Expected Outcomes': [
        "Reduced waste generation",
        "Increased recycling and reuse rates",
        "Economic benefits through resource optimization"
    ]
}

def save_novel_concept_to_csv(data, file_path):
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for key, value in data.items():
            if isinstance(value, list):
                writer.writerow([key])
                for item in value:
                    writer.writerow(['  -', item])
            else:
                writer.writerow([key, value])

save_novel_concept_to_csv(regional_collaboration, 'results/regional_collaboration.csv')