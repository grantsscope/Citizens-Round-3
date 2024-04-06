import openai
import json
import csv

openai.api_key = ''

def long_description(description):
    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
          {"role": "system", "content": "You are a helpful assistant."},
          {"role": "user", "content": f"Summarize the problem and the impact created by project in 200 words: {description}"}
      ],
      max_tokens=800  # Adjust tokens according to your needs
    )
    return response.choices[0].message['content'].strip()

def short_description(description):
    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
          {"role": "system", "content": "You are a helpful assistant."},
          {"role": "user", "content": f"Summarize the project in a phrase less than 20 words: {description}"}
      ],
      max_tokens=800  # Adjust tokens according to your needs
    )
    return response.choices[0].message['content'].strip()


def process_file_to_csv(input_file, output_file):
    with open(input_file, 'r') as file:
        data = json.load(file)

    columns = set()
    for entry in data:
        for key in entry.keys():
            columns.add(key)
    columns.add('Short Project Desc')  # Ensure the new column is added

    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        
        for entry in data:
            if 'Project Desc' in entry:
                entry['Project Desc'] = long_description(entry['Project Desc'])
                entry['Short Project Desc'] = short_description(entry['Project Desc'])
            writer.writerow(entry)

# Replace 'GreenPill.json' with the path to your JSON file
# and 'Summarized_GreenPill.csv' with the path for the new file
process_file_to_csv('cr3_projects.json', 'summarized_cr3_projects.csv')
