def convert_postgres_to_bigquery(query):
    # Implement the logic to convert PostgreSQL syntax to BigQuery syntax
    converted_query = query.replace("SELECT", "CON_SELECT").replace("FROM", "CON_FROM").replace("WHERE", "CON_WHERE")
    converted_query = converted_query.replace("TO_DATE", "DATE")
    
    return converted_query

def attach_comments_to_top(batch, comments):
    # Attach comments to the top of the batch
    return '\n'.join(comments) + '\n' + batch 
