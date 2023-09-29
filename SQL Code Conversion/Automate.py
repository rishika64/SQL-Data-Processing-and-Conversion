import os
import json
from flask import Flask, request, jsonify, send_from_directory
from Pre_Conversion import separate_code, separate_comments
from Conversion import apply_find_replace_rules
from Post_Conversion import merge_batches 

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
CONVERSION_OUTPUT_FOLDER = 'conversion_output'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['CONVERSION_OUTPUT_FOLDER'] = CONVERSION_OUTPUT_FOLDER

# Define allowed file extensions
ALLOWED_EXTENSIONS = {'txt', 'sql'}

# Function to check if a file has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Create a route to handle file uploads and trigger the entire process
@app.route('/process_file', methods=['POST'])
def process_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file and allowed_file(file.filename):
        input_text = file.read().decode('utf-8')

        # Call functions from other scripts
        code_segments, unknown_batches, comments, batch_order = separate_code(input_text)
        find_replace_rules = {}  # Define your find and replace rules here
        converted_batches = []

        for segment in code_segments:
            # Apply find and replace rules
            converted_content = apply_find_replace_rules('\n'.join(segment['code']), find_replace_rules)
            converted_batches.append(converted_content)

        # Merge batches
        merged_output = merge_batches({
            'order': batch_order,
            'types': {
                'known': len(converted_batches),
                'unknown': len(unknown_batches),
                'comments': len(comments),
            },
        })

        # Save the merged output to a file
        merged_output_path = os.path.join(app.config['CONVERSION_OUTPUT_FOLDER'], 'merged_output.sql')
        with open(merged_output_path, 'w') as merged_file:
            merged_file.write(merged_output)

        # Provide a link to download the merged output file
        merged_output_link = '/download/merged_output.sql'

        return jsonify({'message': 'Conversion completed.', 'download_link': merged_output_link})
    else:
        return jsonify({'error': 'Invalid file format'})

# Define a route to download the merged output file
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['CONVERSION_OUTPUT_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    os.makedirs(app.config['CONVERSION_OUTPUT_FOLDER'], exist_ok=True)
    app.run(debug=True)
