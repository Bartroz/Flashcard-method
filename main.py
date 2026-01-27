from sql_conn import checkIfTableExist, createTables

if not checkIfTableExist():
    createTables()