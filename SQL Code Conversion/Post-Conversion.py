import os

# Specify the folder containing the converted files
CONVERTED_FOLDER = 'converted_output'

# Specify the output file where the merged content will be saved
MERGED_FILE = 'merged_output.sql'

def is_numeric_string(s):
    # Check if a string contains only digits
    return s.isdigit()

def merge_files():
    # Initialize the merged content with comments
    merged_content = []

    # First, add comments to the merged content
    comments_file_path = os.path.join(CONVERTED_FOLDER, 'comments.sql')
    if os.path.exists(comments_file_path):
        with open(comments_file_path, 'r') as comments_file:
            merged_content.extend(comments_file.readlines())
            merged_content.append('\n')  # Add an empty line after comments

    # Get a list of files in the folder
    files = os.listdir(CONVERTED_FOLDER)

    # Extract and sort files by their numeric values (if available)
    sorted_files = sorted(files, key=lambda x: (is_numeric_string(''.join(filter(str.isdigit, x))), x))

    # Merge files in sorted order
    for filename in sorted_files:
        file_path = os.path.join(CONVERTED_FOLDER, filename)
        with open(file_path, 'r') as file:
            merged_content.extend(file.readlines())
            merged_content.append('\n')  # Add an empty line after each file

    # Write the merged content to the output file
    with open(MERGED_FILE, 'w') as output_file:
        output_file.writelines(merged_content)

if __name__ == '__main__':
    merge_files()
