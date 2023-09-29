import os
import json
import re

# Define the paths to the input files (output from Pre-Conversion.py) and the output file
OUTPUT_FOLDER = 'output'
CONVERSION_OUTPUT_FOLDER = 'conversion_output'
METADATA_FILE = 'metadata.json'
METADATA_PATH = os.path.join(OUTPUT_FOLDER, METADATA_FILE)

# Create a directory for the conversion output if it doesn't exist
os.makedirs(CONVERSION_OUTPUT_FOLDER, exist_ok=True)

# Load the metadata
with open(METADATA_PATH, 'r') as metadata_file:
    metadata = json.load(metadata_file)

# Define find and replace rules using regular expressions
find_replace_rules = {
    r'\bTINYINT\b': 'INT64',  
    r'\bSMALLINT\b': 'INT64',
    r'\bMEDIUMINT\b': 'INT64',
    r'\bINT\b': 'INT64',
    r'\bINTEGER\b': 'INT64',
    r'\bBIGINT\b': 'INT64',
    r'\bDECIMAL\b': 'NUMERIC',
    r'\bNUMERIC(p,s)\b': 'NUMERIC',
    r'\bREAL\b': 'FLOAT64',
    r'\bDOUBLE PRECISION\b': 'FLOAT64',
    r'\bBOOLEAN\b': 'BOOL',
    r'\bCHAR(n)\b': 'STRING',
    r'\bCHARACTER(n)\b': 'STRING',
    r'\bVARCHAR(n)\b': 'STRING',
    r'\bBYTEA\b': 'BYTES',
    r'\bTINYTEXT\b': 'STRING',
    r'\bTEXT\b': 'STRING',
    r'\bMEDIUMTEXT\b': 'STRING',
    r'\bLONGTEXT\b': 'STRING',
    r'\bTIMESTAMP\b': 'DATETIME',
    r'\bFUNCTION\b': 'PROCEDURE',
    r'\bRETURNS int4\b': ' ',
    r'\bLANGUAGE plpgsql\b': ' ',
    r'\bVOLATILE\b': ' ',
    r'\bAS $$\b': ' ',
    r'\b$$\b': ' ',
}

# Function to apply find and replace using regular expressions
def apply_find_replace_rules(content, rules):
    for find, replace in rules.items():
        content = re.sub(find, replace, content)
    return content

# Loop through the metadata to process batches in the specified order
for batch_type, batch_count in metadata['order']:
    if batch_type == 'known':
        # Process known batches (perform find and replace)
        # Load the known batch content
        batch_filename = f"known_{batch_count}.sql"
        with open(os.path.join(OUTPUT_FOLDER, batch_filename), 'r') as batch_file:
            batch_content = batch_file.read()

        # Apply find and replace rules
        converted_content = apply_find_replace_rules(batch_content, find_replace_rules)

        # Save the converted batch
        converted_batch_filename = f"known_{batch_count}.sql"
        with open(os.path.join(CONVERSION_OUTPUT_FOLDER, converted_batch_filename), 'w') as converted_batch_file:
            converted_batch_file.write(converted_content)
    
    elif batch_type == 'unknown':
        # Process unknown batches (add a single-line comment)
        # Load the unknown batch content
        batch_filename = f"unknown_{batch_count}.sql"
        with open(os.path.join(OUTPUT_FOLDER, batch_filename), 'r') as batch_file:
            batch_content = batch_file.read()

        # Add a comment line at the beginning of the batch
        modified_content = f"-- MODIFICATION NEEDED\n{batch_content}"

        # Save the converted batch
        converted_batch_filename = f"unknown_{batch_count}.sql"
        with open(os.path.join(CONVERSION_OUTPUT_FOLDER, converted_batch_filename), 'w') as converted_batch_file:
            converted_batch_file.write(modified_content)

# Copy comment batches as is
for i in range(1, metadata['types']['comments'] + 1):
    comment_filename = f"comments_{i}.sql"
    with open(os.path.join(OUTPUT_FOLDER, comment_filename), 'r') as comment_file:
        comment_content = comment_file.read()
    
    converted_comment_filename = f"comments_{i}.sql"
    with open(os.path.join(CONVERSION_OUTPUT_FOLDER, converted_comment_filename), 'w') as converted_comment_file:
        converted_comment_file.write(comment_content)

print("Conversion completed. Converted files are saved in the 'conversion_output' folder.")
