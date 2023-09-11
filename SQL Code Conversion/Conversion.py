import os
import re

# Define the rules for known file conversion (find and replace)
def convert_known_file(input_path, output_path):
    # Read the content of the input file
    with open(input_path, 'r') as input_file:
        content = input_file.read()

    # Apply find and replace for standalone word
    content = re.sub(r'\bAS\b', '::', content)

    # Write the modified content to the output file
    with open(output_path, 'w') as output_file:
        output_file.write(content)


# Define the rules for unknown file and comments conversion (pass through)
def convert_unknown_file(input_path, output_path):
    # Simply copy the content of the input file to the output file
    with open(input_path, 'r') as input_file, open(output_path, 'w') as output_file:
        output_file.write(input_file.read())

def main():
    input_folder = 'output'  # Change to the path where Pre-Conversion.py saved the files
    output_folder = 'converted_output'

    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)

        if filename.startswith('known'):
            # Apply rules for known files
            convert_known_file(input_path, output_path)
        elif filename.startswith('unknown') or filename.startswith('comments'):
            # Apply rules for unknown files and comments
            convert_unknown_file(input_path, output_path)
        else:
            # Handle any other files if needed
            pass

if __name__ == '__main__':
    main()
