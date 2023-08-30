import json
import csv

def read_file_and_extract_content(file_path: str):
    with open(file_path, "r") as file:
        if file_path.endswith(".json"):
            content = json.load(file)
        elif file_path.endswith(".csv"):
            content = read_csv(file)
        elif file_path.endswith(".txt"):
            content = read_txt(file)
        else:
            content = read_txt(file)
            #raise ValueError("Unsupported file format")

    return content

def read_csv(file):
    data_list = []
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
            data_list.append(row)
    return data_list

def read_txt(file):
    content = [line.strip() for line in file.readlines()]
    return content
