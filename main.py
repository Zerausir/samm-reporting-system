import pyodbc

DRIVER_NAME = 'ODBC Driver 11 for SQL Server'
SERVER_NAME = '172.20.1.220\SQL2014'
DATABASE_NAME = '8_CZO2'
TABLE = 'dbo.Script_ResultMetric_TEMS_Service_KPIs_HTTP'

try:
    # Establish a connection to the database
    connection_string = f'DRIVER={DRIVER_NAME};SERVER={SERVER_NAME};DATABASE={DATABASE_NAME};Trusted_Connection=yes;'
    conn = pyodbc.connect(connection_string)

    # define the SQL query
    query = f'SELECT TOP 100 * FROM {TABLE}'

    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()

    # Execute a sample query
    cursor.execute(query)
    # Fetch the query results
    data = cursor.fetchall()
    # get the column names (header)
    header = [column[0] for column in cursor.description]

    # Output the results to the console
    print(header)
    for row in data:
        print(row)

    # Close the connection and cursor objects
    cursor.close()
    conn.close()

except Exception as e:
    print('Database connection failed.')
