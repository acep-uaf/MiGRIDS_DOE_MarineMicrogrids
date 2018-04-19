def replaceDefaultDatabase(projectdb):
    from ProjectSQLiteHandler import ProjectSQLiteHandler
    import pandas as pd
    tables = ['environment', 'components', 'projectTree']
    for t in tables:
        h = ProjectSQLiteHandler(projectdb)
        # project data becomes a dataframe
        try:
            projectTable = pd.read_sql_query("select * from " + t, h.connection)
            h.closeDatabase()
            # the _id field is always the index for all tables
            projectTable.set_index(projectTable['_id'])
            projectTable = projectTable.drop('_id', 1)
            projectTable.index.names = ['_id']
            # connect to the active database and overwrite the table
            h = ProjectSQLiteHandler('project_manager')
            projectTable.to_sql(t, h.connection, if_exists='replace')
            h.closeDatabase()
        except:
            h.closeDatabase()