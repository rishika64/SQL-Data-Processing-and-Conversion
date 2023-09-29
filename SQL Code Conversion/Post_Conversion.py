import os
import json

# Define the paths to the input files (metadata) and the output file
CONVERSION_OUTPUT_FOLDER = 'conversion_output'
MERGED_OUTPUT_FILE = 'merged_output.sql'
METADATA_FILE = 'output\metadata.json'

# Load the metadata
with open(METADATA_FILE, 'r') as metadata_file:
    metadata = json.load(metadata_file)

# Create a list to store the content of each batch in order
merged_content = []

# Loop through the metadata to process batches in the specified order
for batch_type, batch_count in metadata['order']:
    if batch_type in ('known', 'unknown', 'comments'):
        # Load the content of the batch
        batch_filename = f"{batch_type}_{batch_count}.sql"
        with open(os.path.join(CONVERSION_OUTPUT_FOLDER, batch_filename), 'r') as batch_file:
            batch_content = batch_file.read()

        # Append the content to the merged list
        merged_content.append(batch_content)

# Join the contents of all batches into a single string
merged_output = '\n'.join(merged_content)

# Save the merged output to a file
with open(MERGED_OUTPUT_FILE, 'w') as merged_file:
    merged_file.write(merged_output)

print("Post-Conversion completed. Merged output is saved in 'merged_output.sql'.")

