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
    batch_order = []  # Maintain the order of batches

    is_nested = False  # Variable to track nested code blocks
    in_multiline_comment = False  # Variable to track multi-line comments
    known_count = 0  # Count for known batches
    unknown_count = 0  # Count for unknown batches

    for line in lines:
        if in_multiline_comment:
            # Check if this line contains the end of a multi-line comment
            if '*/' in line:
                in_multiline_comment = False
                comments.append(line)
                batch_order.append(('comments', len(comments)))
            else:
                # Append the line to the current comment batch
                comments[-1] += '\n' + line
            continue  # Skip the line as it's part of a multi-line comment
        elif line.strip().startswith('/*'):
            # Multi-line comment start, set the flag and add the line to comments
            in_multiline_comment = True
            comments.append(line)
            batch_order.append(('comments', len(comments)))
        elif line.strip().startswith('--'):
            # Single-line comment, append to comments
            comments.append(line)
            batch_order.append(('comments', len(comments)))
        else:
            # Check if we are inside a nested block
            if not is_nested:
                # Check for start of a known batch
                if any(keyword in line for keyword in ("SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "ALTER", "DROP", "SET")):
                    is_nested = True  # Set to True when a keyword is encountered
                    code_type = 'known'  # Default to 'known' for nested batches
                else:
                    code_type = 'unknown'  # Default to 'unknown' for other lines

            if is_nested:
                # Append the line to the current batch 
                current_segment.append(line)
                
                # Check if this line contains the end of a nested block
                if line.strip().endswith(';'):
                    is_nested = False  # Reset when a semicolon is encountered
                    
                    # Check for nested comments within this known/unknown batch
                    nested_comments, nested_comment_batch_order = separate_comments('\n'.join(current_segment))
                    comments.extend(nested_comments)
                    batch_order.extend(nested_comment_batch_order)

                    if code_type == 'known':
                        known_count += 1
                        batch_order.append(('known', known_count))
                    elif code_type == 'unknown':
                        unknown_count += 1
                        batch_order.append(('unknown', unknown_count))

                    code_segments.append({'code': current_segment, 'code_type': code_type})
                    current_segment = []
            else:
                # Check if the line starts with a keyword
                if any(keyword in line.strip().upper() for keyword in ("SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "ALTER", "DROP", "SET")):
                    # Treat keyword statements as separate batches/files
                    if current_segment:
                        code_segments.append({'code': current_segment, 'code_type': code_type})
                        if code_type == 'known':
                            known_count += 1
                            batch_order.append(('known', known_count))
                        elif code_type == 'unknown':
                            unknown_count += 1
                            batch_order.append(('unknown', unknown_count))
                    current_segment = [line]
                    code_type = 'known'  # Default to 'known' for keyword statement
                else:
                    # Append the line to unknown_batches
                    unknown_batches.append(line)
                    code_type = 'unknown'  # Default to 'unknown' for other lines
                    
                    # Check if this line contains the end of a known batch
                    if line.strip().endswith(';'):
                        # Check for nested comments within this known/unknown batch
                        nested_comments, nested_comment_batch_order = separate_comments(line)
                        comments.extend(nested_comments)
                        batch_order.extend(nested_comment_batch_order)
                        
                        if code_type == 'known':
                            known_count += 1
                            batch_order.append(('known', known_count))
                        elif code_type == 'unknown':
                            unknown_count += 1
                            batch_order.append(('unknown', unknown_count))
                            
                        code_segments.append({'code': current_segment, 'code_type': code_type})
                        current_segment = []

    # Append any remaining current_segment
    if current_segment:
        code_segments.append({'code': current_segment, 'code_type': code_type})
        if code_type == 'known':
            known_count += 1
            batch_order.append(('known', known_count))
        elif code_type == 'unknown':
            unknown_count += 1
            batch_order.append(('unknown', unknown_count))

    # Create a metadata JSON file to store the order and type of batches
    metadata = {
        'order': batch_order,
        'types': {
            'known': known_count,
            'unknown': unknown_count,
            'comments': len(comments),
        }
    }

    with open(os.path.join(app.config['OUTPUT_FOLDER'], 'metadata.json'), 'w') as metadata_file:
        json.dump(metadata, metadata_file)

    return code_segments, unknown_batches, comments

def separate_comments(input_text):
    # Split the input text into lines
    lines = input_text.split('\n')

    # Initialize variables to track comments
    comments = []
    batch_order = []

    in_multiline_comment = False  # Variable to track multi-line comments

    for line in lines:
        if in_multiline_comment:
            # Check if this line contains the end of a multi-line comment
            if '*/' in line:
                in_multiline_comment = False
                comments.append(line)
                batch_order.append(('comments', len(comments)))
            else:
                # Append the line to the current comment batch
                comments[-1] += '\n' + line
            continue  # Skip the line as it's part of a multi-line comment
        elif line.strip().startswith('/*'):
            # Multi-line comment start, set the flag and add the line to comments
            in_multiline_comment = True
            comments.append(line)
            batch_order.append(('comments', len(comments)))

    return comments, batch_order

def write_code_to_files(code_segments, unknown_batches, comments, batch_order):
    output_files = {}
    code_type_count = {'known': 0, 'unknown': 0, 'comments': 0}
    
    for code_type, batch_number in batch_order:
        if code_type == 'comments':
            code_type_count['comments'] += 1
            filename = f"comment_{code_type_count['comments']}.sql"
            content = comments[batch_number - 1]
            if content.strip():  # Check if the content is not empty
                with open(os.path.join(app.config['OUTPUT_FOLDER'], filename), 'w') as f:
                    f.write(content)
                output_files['comments'] = output_files.get('comments', []) + [filename]

    # Process comments
    for i, comments in enumerate(comments):
        code_type_count['comments'] += 1
        filename = f"comments_{code_type_count['comments']}.sql"
        if comments.strip():  # Check if the content is not empty
            with open(os.path.join(app.config['OUTPUT_FOLDER'], filename), 'w') as f:
                f.write(comments)
            output_files['comments'] = output_files.get('comments', []) + [filename]


    # Process known batches
    for i, segment in enumerate(code_segments):
        if segment['code_type'] == 'known':
            code_type_count['known'] += 1
            filename = f"known_{code_type_count['known']}.sql"
            content = '\n'.join(segment['code'])
            if content.strip():  # Check if the content is not empty
                with open(os.path.join(app.config['OUTPUT_FOLDER'], filename), 'w') as f:
                    f.write(content)
                output_files['known'] = output_files.get('known', []) + [filename]

    # Process unknown batches
    for i, batch in enumerate(unknown_batches):
        # Check if the batch is empty or null
        if batch.strip():  # Check if the content is not empty
            code_type_count['unknown'] += 1
            filename = f"unknown_{code_type_count['unknown']}.sql"
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

        code_segments, unknown_batches, comments = separate_code(input_text)
        batch_order = []  # Initialize batch_order
        output_files = write_code_to_files(code_segments, unknown_batches, comments, batch_order)

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
