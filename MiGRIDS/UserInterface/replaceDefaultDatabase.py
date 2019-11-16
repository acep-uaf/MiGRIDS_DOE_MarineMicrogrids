def replaceDefaultDatabase(projectdb):
    from MiGRIDS.Controller.ProjectSQLiteHandler import ProjectSQLiteHandler
    import pandas as pd
    tables = ['project','component_files','component','set_components','input_files','optimize_input','set_','pretty_names','run','run_attributes','setup']
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
            #data gets appended into empty tables created in default database
            projectTable.to_sql(t, h.connection, if_exists='append')
            h.closeDatabase()
        except Exception as e:
            print(e)
            h.closeDatabase()