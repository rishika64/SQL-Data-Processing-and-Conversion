#app.py

# Import necessary modules
from flask import Flask, render_template, request, send_file
import sqlparse
from database import initialize_database, insert_file, get_all_files

# Create a Flask application instance
app = Flask(__name__)

# Initialize the database on application startup
initialize_database()

# Function to extract comments from SQL code
def extract_comments(sql):
    # Parse the SQL code using sqlparse library
    parsed = sqlparse.parse(sql)
    comments = []

    # Loop through parsed tokens to find comments
    for stmt in parsed:
        for token in stmt.tokens:
            # If the token is a comment, add it to the 'comments' list
            if isinstance(token, sqlparse.sql.Comment):
                comments.append((token.lineno, token.stmt_position, token.value))

    return comments

# Function to perform codebase conversion on SQL code
def perform_codebase_conversion(sql):
    # Replace 'FUNCTION' with 'PROCEDURE' in the SQL code
    converted_sql = sql.replace('FUNCTION', 'PROCEDURE')

    return converted_sql

# Define the route for the web application
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if the user uploaded a file and if it has a .sql extension
        file = request.files['file']
        if file and file.filename.endswith('.sql'):
            # Read the contents of the uploaded SQL file
            original_sql = file.read().decode('utf-8')

            # Perform the codebase conversion on the original SQL code
            converted_sql = perform_codebase_conversion(original_sql)

            # Extract comments from the original SQL code
            comments = extract_comments(original_sql)

            # Format comments to be prefixed with '--'
            formatted_comments = '\n'.join([f'-- {comment}' for _, _, comment in comments])

            # Combine the converted SQL code and comments
            updated_sql = f"{formatted_comments}\n\n{converted_sql}"

            # Generate a new .sql file containing the converted code with original comments
            converted_file = f"converted_{file.filename}"
            with open(converted_file, 'w') as f:
                f.write(updated_sql)

            # Insert the file and its comments into the database
            insert_file(file.filename, converted_file, formatted_comments)

            # Provide the converted .sql file for download
            return send_file(converted_file, as_attachment=True)

    # Render the HTML template for the upload form
    return render_template('upload.html')

# Start the Flask application only if this script is executed directly
if __name__ == '__main__':
    app.run(debug=True)
