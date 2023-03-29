import pyodbc

DRIVER_NAME = 'SQL Server Native Client 10.0'
SERVER_NAME = '172.20.1.220\SQL2014'
DATABASE_NAME = '8_CZO2'

try:
    # Establish a connection to the database
    conn = pyodbc.connect(f'DRIVER={DRIVER_NAME};SERVER={SERVER_NAME};DATABASE={DATABASE_NAME};Trusted_Connection=yes;')
    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()

    # Execute a sample query
    cursor.execute('SELECT TOP (100)* FROM dbo.Script_ResultMetric_TEMS_Service_KPIs_HTTP')
    # Fetch the query results
    rows = cursor.fetchall()

    # Output the results to the console
    for row in rows:
        print(row)

    # Close the connection and cursor objects
    cursor.close()
    conn.close()

except Exception as e:
    print('Database connection failed.')
