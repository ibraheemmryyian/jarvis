import csv

def save_to_csv(data, file_path):
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for row in data:
            writer.writerow(row)

# Example multi-industry material flow efficiency scoring data
multi_industry_data = [
    ['Industry', 'Material', 'Inbound Flow (tons)', 'Outbound Flow (tons)'],
    ['Chemical Manufacturing', 'Oil', 10000, 5000],
    ['Electronics Manufacturing', 'Plastic', 8000, 4000],
    ['Automotive Manufacturing', 'Steel', 15000, 12000],
    ['Construction', 'Concrete', 20000, 18000]
]

save_to_csv(multi_industry_data, 'results/multi_industry_material_flow_efficiency_scoring.csv')