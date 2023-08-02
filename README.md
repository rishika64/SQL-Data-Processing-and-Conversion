# SQL Code Conversion 

The SQL Code Conversion project is a web application built with Python and Flask that facilitates the conversion of SQL code while preserving comments in it's original form. The primary objective of this project is to allow users to upload SQL files, have the codebase converted according to specific rules, and then obtain the converted SQL file with the original comments reattached.

## Project Components
### app.py
app.py is the main Python file that contains the Flask application, routing, and logic for SQL code conversion and comment extraction.

```mermaid
graph TD;
    A[Start] --> B[Receive HTTP Request]
    B --> C{Request Method is POST?}
    C -- Yes --> D[Upload .sql File]
    D --> E[Perform Codebase Conversion]
    E --> F[Extract Comments]
    F --> G[Generate Converted .sql File]
    G --> H[Insert File and Comments into Database]
    H --> I[Provide Converted .sql File for Download]
    C -- No --> I[Render Upload Form]
    I --> J[End]
```

Dependencies: 
- Flask handles the web application functionality
- sqlparse is used for parsing SQL code and extracting comments

### database.py

<img width="694" alt="image" src="https://github.com/rishika64/Tech-Mahindra/assets/96427808/e20f3ef6-1080-4026-a4a4-fd6aab0d3071">


database.py contains functions related to the SQLite database used to store information about the uploaded SQL files.

```mermaid
graph LR;
    A[Start] --> B[Initialize Database]
    B --> C{Database Exists?}
    C -- No --> D[Create Database and Table]
    C -- Yes --> E[Continue]
    D --> E[Finish]
    E --> F[End]
```

### upload.html

upload.html is the HTML template used to display the web page for uploading SQL files.


![image](https://github.com/rishika64/Tech-Mahindra/assets/96427808/eba72903-64eb-4364-8400-cf256b7fe3e1)

Basic Framework for code conversion with comment extraction

![image](https://github.com/rishika64/Tech-Mahindra/assets/96427808/a37342e5-4024-4390-88e1-a66408a787ae)

‘Converted’ file added in the code path after successful uploading

