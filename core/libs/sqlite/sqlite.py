import sqlite3


class Sql():
    def __init__(self, path="database", debug=False):
        if not path.endswith(".db"):
            path = path + ".db"
        self.path = path
        self.conn = sqlite3.connect(self.path)
        self.c = self.conn.cursor()
        self.debug = debug

    def close(self):
        self.c.close()
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.c.close()
        self.conn.close()
        

    def execute(self, table, *args):
        if self.debug: print(args)

        columns = [col["name"] for col in self.columns(table)]

        return [
            dict(
                zip(
                    columns, 
                    [
                        elem[1:-1] if type(elem)==str and elem.startswith("'") else elem 
                        for elem in row
                    ]
                )
            )
            for row in self.c.execute(*args)
        ]



    def read(self, table=None):
        """
        Чтение таблицы
        """

        args = (f'SELECT * FROM {table}',)

        return self.execute(table, *args)
        

    def search(self, table=None, data=None):
        """
        Поиск по таблице

        search("TABLE_NAME", {"COLUMN_NAME": "CONTENT", ...})
        """

        args = (
            f"SELECT * FROM {table} WHERE " + " and ".join(
                [((key + " is null") if value is None else (key + " = ?")) for key, value in data.items()]
            ), 
            [v for v in data.values() if v is not None]
        )

        return self.execute(table, *args)


    def search_like(self, table=None, data=None):
        """
        Поиск по не полному совпадению 

        search_like("TABLE_NAME", {"COLUMN_NAME": "CONTENT", ...})
        """

        args = (f"SELECT * FROM {table} WHERE " + " and ".join([key + " like ?" for key in data]), list(data.values()))

        return self.execute(table, *args)


    def search_max(self, table, column):
        """
        Поиск максимального значения в столбце

        search_max("TABLE_NAME", "COLUMN_NAME")
        """

        args = (f"SELECT * FROM {table} WHERE {column} = (SELECT max({column}) FROM {table})")

        return self.execute(table, args)


    def search_min(self, table, column):
        """
        Поиск минимального значения в таблице

        search_min("TABLE_NAME", "COLUMN_NAME")
        """

        args = (f"SELECT * FROM {table} WHERE {column} = (SELECT min({column}) FROM {table})")

        return self.execute(table, args)



    def add(self, table=None, data=None, autosave=True):
        """
        Добавление записи в таблицу

        add("TABLE_NAME", {"COLUMN_NAME": "CONTENT", ...})
        """

        args = (
            'INSERT INTO {} ({}) VALUES ({})'.format(
                table,
                ", ".join(list(data)),
                ", ".join(["?"]*len(data))
            ),
            list(data.values())
        )

        self.execute(table, *args)
        if autosave: self.conn.commit()

        return


    def delete(self, table=None, data=None, autosave=True):
        """
        Удаление записи из таблицы по совпадению ключей в столбцах

        delete("TABLE_NAME", {})
        """

        args = (
            f"DELETE FROM {table} WHERE " + " and ".join(
                [((key + " is null") if value is None else (key + " = ?")) for key, value in data.items()]
            ), 
            [v for v in data.values() if v is not None]
        )

        self.execute(table, *args)
        if autosave: self.conn.commit()

        return


    def delete_all(self, table):
        args = (f"DELETE FROM {table}", )

        self.execute(table, *args)
        self.conn.commit()

        return


    def update(self, table=None, old_data=None, new_data=None, autosave=True):
        """
        Обновить запись в таблице по совпадению ключей в столбцах

        update("TABLE_NAME", {}, {})
        """
        
        args = (
            'UPDATE {} SET {} WHERE {}'.format(
                table,
                ", ".join([((key + " = null") if value is None else (key + " = ?")) for key, value in new_data.items()]),
                " and ".join([((key + " is null") if value is None else (key + " = ?")) for key, value in old_data.items()])
            ),
            [v for v in new_data.values() if v is not None] + [v for v in old_data.values() if v is not None]
        )
        
        self.execute(table, *args)
        if autosave: self.conn.commit()

        return True


    def create(self, table=None, columns=None):
        """
        Создать таблицу

        create("TABLE_NAME", {"COLUMN_NAME_1": str, "COLUMN_NAME_2": int, ...})
        """

        types = {
            int: "INTEGER",
            "int": "INTEGER",
            "integer": "INTEGER",
            "INTEGER": "INTEGER",
            str: "TEXT",
            "str": "TEXT",
            "string": "TEXT",
            "STRING": "TEXT",
            "text": "TEXT",
            "TEXT": "TEXT"
        }

        args = (
            'CREATE TABLE `{}` ({})'.format(
                table,
                ", ".join([f"`{key}` " + types[val] for key, val in columns.items()])
            ),
        )

        self.execute(table, *args)
        self.conn.commit()
        return True



    def tables(self):
        """
        Список таблиц
        """

        self.c.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        return [k[0] for k in self.c.fetchall()]


    def columns(self, table=None):
        """
        Список столбцов с таблице
        """

        self.c.execute(f"PRAGMA table_info({table})")
        return [dict(zip(["id", "name", "type"], [k[0], k[1], {"INTEGER": int, "TEXT": str}[k[2]]])) for k in self.c.fetchall()]


    def check_table_existence(self, table):
        """
        Проверка существования таблицы
        """
        
        args = (f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")

        return bool(self.execute(table, args))


    def save(self):
        self.conn.commit()