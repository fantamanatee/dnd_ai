import psycopg2

if __name__ == '__main__':
    '''
    Main function to test database connection.
    '''
    # Define your connection parameters
    dbname = 'dnd_ai'
    user = 'dnd_ai'  # Replace with your PostgreSQL username
    password = 'drowssap1'   # Replace with your PostgreSQL password if any
    host = 'localhost'           # Replace with your PostgreSQL server hostname or IP
    port = '5432'                # Replace with your PostgreSQL port

    # Establish a connection to the database
    try:
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        print('Connected to the database!')
        
        # Create a cursor object using the connection
        cursor = conn.cursor()
        # Define the SQL statement for insertion
        sql = """
            INSERT INTO dummy_table (name, age, created_at)
            VALUES (%s, %s, %s);
        """
        # Example data for insertion
        data = ('value1', '123', '2024-06-28 23:50:53.467172')
        # Execute the SQL statement
        cursor.execute(sql, data)
        
        # Example query
        cursor.execute('SELECT * FROM dummy_table;')

        
        # Fetch and print results
        rows = cursor.fetchall()
        for row in rows:
            print(row)
        
        # Close cursor and connection
        cursor.close()
        conn.close()

    except psycopg2.Error as e:
        print('Error connecting to PostgreSQL:', e)