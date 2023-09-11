import os
import json
from flask import Flask, render_template, request, send_from_directory

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'txt', 'sql'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def separate_code(input_text):
    # Split the input text into lines
    lines = input_text.split('\n')

    # Initialize variables to track code segments
    code_segments = []
    current_segment = []
    unknown_batches = []
    comments = []

    is_nested = False  # Variable to track nested code blocks

    for line in lines:
        if line.strip().startswith('--'):
            # Comment line, append to comments
            comments.append(line)
        else:
            # Check if we are inside a nested block
            if not is_nested:
                # Check for start of a known batch
                if any(keyword in line for keyword in ("SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "ALTER", "DROP", "SET")):
                    is_nested = True  # Set to True when a keyword is encountered

            if is_nested:
                # Append the line to the current batch 
                current_segment.append(line)
                
                # Check if this line contains the end of a nested block
                if line.strip().endswith(';'):
                    is_nested = False  # Reset when a semicolon is encountered
                    code_segments.append({'code': current_segment})
                    current_segment = []
            else:
                # Check if the line starts with 'SET'
                if line.strip().startswith('SET'):
                    # Treat 'SET' statements as separate batches/files
                    if current_segment:
                        code_segments.append({'code': current_segment})
                    current_segment = [line]
                else:
                    # Append the line to unknown_batches
                    unknown_batches.append(line)

                    # Check if this line contains the end of a known batch
                    if line.strip().endswith(';'):
                        code_segments.append({'code': current_segment})
                        current_segment = []

    # Append any remaining current_segment
    if current_segment:
        code_segments.append({'code': current_segment})

    # Create a metadata JSON file to store the order and type of batches
    metadata = {
        'order': ['known', 'unknown', 'comments'],
        'types': {
            'known': len(code_segments),
            'unknown': len(unknown_batches),
            'comments': len(comments),
        }
    }

    with open(os.path.join(app.config['OUTPUT_FOLDER'], 'metadata.json'), 'w') as metadata_file:
        json.dump(metadata, metadata_file)

    return code_segments, unknown_batches, comments

def write_code_to_files(code_segments, unknown_batches, comments):
    output_files = {}

    # Process comments
    if comments:
        with open(os.path.join(app.config['OUTPUT_FOLDER'], 'comments.sql'), 'w') as f:
            f.write('\n'.join(comments))
        output_files['comments'] = ['comments.sql']

    # Process known batches
    for i, segment in enumerate(code_segments):
        # Determine the type (known or comment)
        code_type = segment.get('code_type', 'known')

        # Check if the code segment is empty or null
        if not segment['code']:
            continue  # Skip empty/null code segments

        # Create a filename based on type and index
        filename = f"{code_type}_{i + 1}.sql"

        # Write the code segment to the output folder
        with open(os.path.join(app.config['OUTPUT_FOLDER'], filename), 'w') as f:
            f.write('\n'.join(segment['code']))

        output_files[code_type] = output_files.get(code_type, []) + [filename]

    # Process unknown batches
    for i, batch in enumerate(unknown_batches):
        # Check if the batch is empty or null
        if not batch:
            continue  # Skip empty/null batches

        filename = f"unknown_{i + 1}.sql"
        with open(os.path.join(app.config['OUTPUT_FOLDER'], filename), 'w') as f:
            f.write(batch)
        output_files['unknown'] = output_files.get('unknown', []) + [filename]

    return output_files

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part"
    file = request.files['file']

    if file.filename == '':
        return "No selected file"

    if file and allowed_file(file.filename):
        input_text = file.read().decode('utf-8')

        code_segments, unknown_batches, comments = separate_code(input_text)  # Add comments here

        output_files = write_code_to_files(code_segments, unknown_batches, comments)  # Pass comments parameter

        return render_template('result.html', output_files=output_files)
    else:
        return "Invalid file format"

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    app.run(debug=True)
