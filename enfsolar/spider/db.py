import sqlite3


class Factory:
    def __init__(self):
        self.db_file = 'doc/company.db'
        self.conn = ''
        self.init_table_sql = '''
            CREATE TABLE IF NOT EXISTS `company_info`(
            `id`  INTEGER PRIMARY KEY AUTOINCREMENT ,
            `company_id`  int,
            `url`  varchar(512) DEFAULT '',
            `name`  varchar(255) DEFAULT '' ,
            `region`  varchar(64) DEFAULT '' ,
            `site`  varchar(128) DEFAULT '' ,
            `tel`  varchar(64) DEFAULT '' ,
            `email`  varchar(128) DEFAULT '' ,
            `email_sign`  varchar(512) DEFAULT '' ,
            `category`  varchar(255) DEFAULT '' 
            )
        '''

    def init_table(self):
        self.execute(self.init_table_sql)
        print('Table created successfully')

    def get_connection(self):
        if not self.conn:
            self.conn = sqlite3.connect(self.db_file)
        return self.conn

    def get_cursor(self):
        return self.get_connection().cursor()

    def execute(self, sql, auto_commit=True):
        c = self.get_cursor()
        result = c.execute(sql)
        if auto_commit:
            self.commit()
        return result

    def fetch_data(self, sql):
        c = self.get_cursor()
        c.execute(sql)
        return c.fetchall()

    def commit(self):
        self.get_connection().commit()
        self.get_connection().close()
        self.conn = ''
