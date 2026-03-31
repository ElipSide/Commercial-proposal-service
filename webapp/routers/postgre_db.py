import psycopg2
from psycopg2 import sql
from psycopg2 import OperationalError
import json

class Postgre_db():

    def __init__(self, db_user, db_password, db_host, db_port, db_name):
        self.db_user = db_user
        self.db_password = db_password
        self.db_host = db_host
        self.db_port = db_port
        self.db_name = db_name
        #self.connection = self.set_connection()

    #---------------------------------------------------------------------------------------------
    def close_connection(self):
        self.connection.close()

    def set_connection(self):
        try:
            connection = psycopg2.connect(
                database=self.db_name,
                user=self.db_user,
                password=self.db_password,
                host=self.db_host,
                port=self.db_port,
            )
            self.connection = connection
            # print("------------------------------------------------------------")
            # print(f"ПОДКЛЮЧЕНО К {self.db_name}")
            # print("------------------------------------------------------------")
            return connection
        except OperationalError as e:
            print(f"Ошибка '{e}' при подключении к {self.db_name}")
            return 'error'
    #-------------------------------------------------------------------
    def is_safe_table_name(self, table_name):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            allowed_table_names = [row[0] for row in cursor.fetchall()]
            cursor.close()
        except OperationalError as e:
            print("------------------------------------------------------------")
            print(f"Ошибка '{e}' при подключении к базе данных")
            print("------------------------------------------------------------")
            return False
        
        return table_name in allowed_table_names
    #-------------------------------------------------------------------
    def is_safe_column_name(self, column_name):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_schema = 'public'")
            allowed_column_names = [row[0] for row in cursor.fetchall()]
            cursor.close()
            return column_name in allowed_column_names
        except OperationalError as e:
            print("------------------------------------------------------------")
            print(f"Ошибка '{e}' при подключении к базе данных")
            print("------------------------------------------------------------")
            return False
    #---------------------------------------------------------------------------------------------


    #--------------------------------------------------------------------------------------------- CHECK INFO FUNCTIONALITY
    def get_all_db_info(self, table_name):
        if not self.is_safe_table_name(table_name):
            print("------------------------------------------------------------")
            print(f"ИМЯ ТАБЛИЦЫ '{table_name}' НЕ ЯВЛЯЕТСЯ БЕЗОПАСНЫМ ДЛЯ ИСПОЛЬЗОВАНИЯ.")
            print("------------------------------------------------------------")
            return

        try:
            with self.connection.cursor() as cursor:
                query = f"SELECT * FROM {table_name};"
                cursor.execute(query)
                #records = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]

                # print("------------------------------------------------------------")
                print(f"КОЛОНКИ В ТАБЛИЦЕ '{table_name.upper()}': {', '.join(columns)}")
                # print("------------------------------------------------------------")
                # print(f"СОДЕРЖИМОЕ ТАБЛИЦЫ '{table_name}':")
                return columns#records
        except psycopg2.Error as e:
            # print("------------------------------------------------------------")
            print(f"ОШИБКА ПРИ ПОЛУЧЕНИИ ДАННЫХ: {e}")
            # print("------------------------------------------------------------")
    #--------------------------------------------------------------------------------------------- END CHECK INFO FUNCTIONALITY


    #--------------------------------------------------------------------------------------------- FUNCTIONAL

    def insert_row(self, table_name, data,connection):
        if self.is_safe_table_name(table_name):
            unsafe_columns = [key for key in data if not self.is_safe_column_name(key)]
            if not unsafe_columns:
                columns = ', '.join(data.keys())
                placeholders = ', '.join(['%s'] * len(data))
                try:
                    values = [self.convert_data(value) for value in data.values()]
                    cursor = self.connection.cursor()
                    query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                    cursor.execute(query, values)
                    self.connection.commit()
                    cursor.close()
                    # print("------------------------------------------------------------")
                    # print(f"Запись добавлена в таблицу '{table_name}'.")
                    # print("------------------------------------------------------------")
                except Exception as e:
                    print("------------------------------------------------------------")
                    print(f"Ошибка при выполнении запроса: {e}")
                    print("------------------------------------------------------------")
            else:
                print("------------------------------------------------------------")
                print(f"Столбцы не безопасны: {', '.join(unsafe_columns)}.")
                print("------------------------------------------------------------")
        else:
            print("------------------------------------------------------------")
            print("Имя таблицы не является безопасным.")
            print("------------------------------------------------------------")

    def convert_data(self, value):
        if isinstance(value, list):
            return ', '.join(value)
        elif isinstance(value, dict):
            return json.dumps(value)
        return value

    #-------------------------------------------------------------------
    def find_rows_by_column_value(self, table_name, column_name, value):
        if self.is_safe_table_name(table_name) and self.is_safe_column_name(column_name):
            cursor = self.connection.cursor()
            query = f"SELECT * FROM {table_name} WHERE {column_name} = %s"
            cursor.execute(query, (value,))
            rows = cursor.fetchall()
            cursor.close()
            if rows:
                # print("------------------------------------------------------------")
                # print(f"НАЙДЕНЫ СТРОКИ В КОЛОНКЕ {column_name.upper()}:", rows)
                # print("------------------------------------------------------------")
                return rows
            else:
                # print("------------------------------------------------------------")
                print(f"СТРОКИ С {column_name.upper()} =", value, "НЕ НАЙДЕНЫ.")
                # print("------------------------------------------------------------")
                return None
        else:
            # print("------------------------------------------------------------")
            # print(f"ИМЯ ТАБЛИЦЫ '{table_name}' ИЛИ ИМЯ КОЛОНКИ '{column_name}' НЕ ЯВЛЯЮТСЯ БЕЗОПАСНЫМИ ДЛЯ ИСПОЛЬЗОВАНИЯ.")
            # print("------------------------------------------------------------")
            return None
    #-------------------------------------------------------------------
    def delete_row_by_column(self, table_name, column_name, value):
        if self.is_safe_table_name(table_name) and self.is_safe_column_name(column_name):
            cursor = self.connection.cursor()
            query = f"DELETE FROM {table_name} WHERE {column_name} = %s"
            cursor.execute(query, (value,))
            self.connection.commit()
            affected_rows = cursor.rowcount
            cursor.close()

            if affected_rows > 0:
                # print("------------------------------------------------------------")
                print(f"УДАЛЕНО СТРОК: {affected_rows}.")
                # print("------------------------------------------------------------")
            else:
                # print("------------------------------------------------------------")
                print("НЕТ СТРОК ДЛЯ УДАЛЕНИЯ.")
                # print("------------------------------------------------------------")
        # else:
            # print("------------------------------------------------------------")
            # print(f"ИМЯ ТАБЛИЦЫ '{table_name}' ИЛИ ИМЯ КОЛОНКИ '{column_name}' НЕ ЯВЛЯЮТСЯ БЕЗОПАСНЫМИ ДЛЯ ИСПОЛЬЗОВАНИЯ.")
            # print("------------------------------------------------------------")
    #-------------------------------------------------------------------
    def find_duplicates_by_column_value(self, table_name, column_name, value):
        if self.is_safe_table_name(table_name) and self.is_safe_column_name(column_name):
            cursor = self.connection.cursor()
            query = f"""
            SELECT {table_name}.*, COUNT({table_name}.{column_name}) OVER (PARTITION BY {table_name}.{column_name}) as cnt
            FROM {table_name}
            WHERE {table_name}.{column_name} = %s
            """
            cursor.execute(query, (value,))
            results = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            cursor.close()
            duplicates = [dict(zip(columns, row)) for row in results if row[columns.index('cnt')] > 1]
            if duplicates:
                # print("------------------------------------------------------------")
                # print(f"НАЙДЕНЫ ДУБЛИКАТЫ ЗНАЧЕНИЯ '{value}' В КОЛОНКЕ {column_name.upper()}:")
                # for duplicate in duplicates:
                #     print(duplicate)

                # print("------------------------------------------------------------")
                return duplicates
            else:
                # print("------------------------------------------------------------")
                # print(f"ДУБЛИКАТЫ ЗНАЧЕНИЯ '{value}' В КОЛОНКЕ {column_name.upper()} НЕ НАЙДЕНЫ.")
                # print("------------------------------------------------------------")
                return None
        else:
            # print("------------------------------------------------------------")
            # print(f"ИМЯ ТАБЛИЦЫ '{table_name}' ИЛИ ИМЯ КОЛОНКИ '{column_name}' НЕ ЯВЛЯЮТСЯ БЕЗОПАСНЫМИ ДЛЯ ИСПОЛЬЗОВАНИЯ.")
            # print("------------------------------------------------------------")
            return None
        #-----------------------------------------------------------------

    def get_max_id(self, id_column, table_name):
        query = f"SELECT MAX({id_column}) FROM {table_name};"
        cursor = self.connection.cursor()
        cursor.execute(query)
        index = cursor.fetchone()[0]
        if index == None: index = 0
        return index
    #-------------------------------------------------------------------
    def update_row(self, table_name, primary_key_column, new_data):
        if self.is_safe_table_name(table_name) and self.is_safe_column_name(primary_key_column):
            cursor = self.connection.cursor()

            update_columns = ', '.join(f"{key} = %s" for key in new_data if key != primary_key_column)
            values = [self.convert_data(new_data[key]) for key in new_data if key != primary_key_column]
            values.append(self.convert_data(new_data[primary_key_column]))

            try:
                query = f"UPDATE {table_name} SET {update_columns} WHERE {primary_key_column} = %s"
                cursor.execute(query, values)

                self.connection.commit()
                print("------------------------------------------------------------")
                print("Данные успешно обновлены.")
                print("------------------------------------------------------------")
                return True
            except Exception as e:
                print(f"Ошибка при выполнении запроса: {e}")
                return False
            finally:
                cursor.close()
        else:
            print("------------------------------------------------------------")
            print(
                f"ИМЯ ТАБЛИЦЫ '{table_name}' ИЛИ ИМЯ КОЛОНКИ '{primary_key_column}' НЕ ЯВЛЯЮТСЯ БЕЗОПАСНЫМИ ДЛЯ ИСПОЛЬЗОВАНИЯ.")
            print("------------------------------------------------------------")
            return False

    #-------------------------------------------------------------------
    def update_specific_column(self, table_name, primary_key_column, primary_key_value, column_name, new_value):
        if self.is_safe_table_name(table_name) and self.is_safe_column_name(column_name):
            cursor = self.connection.cursor()

            query = f"UPDATE {table_name} SET {column_name} = %s WHERE {primary_key_column} = %s"
            cursor.execute(query, (new_value, primary_key_value))

            self.connection.commit()
            cursor.close()
            # print("------------------------------------------------------------")
            print(f"Колонка '{column_name}' успешно обновлена.")
            # print("------------------------------------------------------------")
            return True
        else:
            print("------------------------------------------------------------")
            print(f"ИМЯ ТАБЛИЦЫ '{table_name}' ИЛИ ИМЯ КОЛОНКИ '{column_name}' НЕ ЯВЛЯЮТСЯ БЕЗОПАСНЫМИ ДЛЯ ИСПОЛЬЗОВАНИЯ.")
            print("------------------------------------------------------------")
            return False
    #---------------------------------------------------------------------------------------------
    def clear_table_and_reset_id(self, table_name):
        if self.is_safe_table_name(table_name):
            cursor = self.connection.cursor()

            query_truncate_table = f"TRUNCATE TABLE {table_name} RESTART IDENTITY"
            cursor.execute(query_truncate_table)

            self.connection.commit()
            cursor.close()

            print("------------------------------------------------------------")
            print(f"ТАБЛИЦА '{table_name}' СБРОШЕНА.")
            print("------------------------------------------------------------")
            return True
        else:
            print("------------------------------------------------------------")
            print(f"ИМЯ ТАБЛИЦЫ '{table_name}' НЕ ЯВЛЯЮТСЯ БЕЗОПАСНЫМИ ДЛЯ ИСПОЛЬЗОВАНИЯ.")
            print("------------------------------------------------------------")
            return False
    #---------------------------------------------------------------------------------------------

    def find_specific_rows_by_column_value(self, table_name, column_name, value, *attributes):
        if self.is_safe_table_name(table_name) and self.is_safe_column_name(column_name):
            cursor = self.connection.cursor()
            columns = ', '.join(attributes) if attributes else '*'
            query = f"SELECT {columns} FROM {table_name} WHERE {column_name} = %s"
            cursor.execute(query, (value,))
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            cursor.close()
            if rows:
                all_rows = []
                for row in rows:
                    json_row = {}
                    for i,col in enumerate(row):
                        json_row[columns[i]] = col
                    all_rows.append(json_row)
                # print(all_rows)
                return all_rows
            else:
                print("------------------------------------------------------------")
                print(f"Строки с {column_name.upper()} = {value} не найдены.")
                print("------------------------------------------------------------")
                return []
        else:
            print("------------------------------------------------------------")
            print("Некорректное имя таблицы или столбца.")
            print("------------------------------------------------------------")
            return []

    #---------------------------------------------------------------------------------------------

    def find_specific_rows_by_column_values(self, table_name, columns_to_select, **kwargs):
        if self.is_safe_table_name(table_name):
            if all(self.is_safe_column_name(col) for col in kwargs.keys()):
                cursor = self.connection.cursor()
                columns = ', '.join(columns_to_select) if columns_to_select else '*'

                where_clauses = []
                values = []
                for col, val in kwargs.items():
                    if self.is_safe_column_name(col):
                        where_clauses.append(f"{col} = %s")
                        values.append(val)
                    else:
                        print("------------------------------------------------------------")
                        print(f"Некорректное имя столбца: {col}")
                        print("------------------------------------------------------------")
                        return []

                where_statement = " AND ".join(where_clauses)
                query = f"SELECT {columns} FROM {table_name}"
                if where_statement:
                    query += f" WHERE {where_statement}"

                cursor.execute(query, values)
                rows = cursor.fetchall()
                print(rows)
                cursor.close()

                if rows:
                    all_rows = []
                    for row in rows:
                        all_rows.extend(row)
                    return rows#all_rows
                else:
                    print("------------------------------------------------------------")
                    print(f"Строки с условиями {kwargs} не найдены.")
                    print("------------------------------------------------------------")
                    return []
            else:
                print("------------------------------------------------------------")
                print("Некорректное имя столбца.")
                print("------------------------------------------------------------")
                return []
        else:
            print("------------------------------------------------------------")
            print("Некорректное имя таблицы.")
            print("------------------------------------------------------------")
            return []

    #---------------------------------------------------------------------------------------------

    def create_table(self, table_name, columns):
        try:
            cursor = self.connection.cursor()

            column_defs = [
                sql.SQL("{} {}").format(
                    sql.Identifier(col_name),
                    sql.SQL(data_type)
                ) for col_name, data_type in columns.items()
            ]

            query = sql.SQL("CREATE TABLE IF NOT EXISTS {} ({})").format(
                sql.Identifier(table_name),
                sql.SQL(', ').join(column_defs)
            )

            cursor.execute(query)
            self.connection.commit()

            print("------------------------------------------------------------")
            print(f"ТАБЛИЦА СОЗДАНА '{table_name}'")
            print("------------------------------------------------------------")

        except psycopg2.Error as e:
            print("------------------------------------------------------------")
            print(f"ОШБКА СОЗДАНИЯ ТАБЛИНЦЫ '{table_name}': {e}")
            print("------------------------------------------------------------")


    #---------------------------------------------------------------------------------------------
    def add_column_to_table(self, tb_name, col_name, col_type, def_value=None):
        try:
            cursor = self.connection.cursor()

            query = sql.SQL("ALTER TABLE {} ADD COLUMN {} {}").format(
                sql.Identifier(tb_name),
                sql.Identifier(col_name),
                sql.SQL(col_type)
            )

            if def_value is not None:
                query = query + sql.SQL(" DEFAULT {}").format(
                    sql.Literal(def_value)
                )

            cursor.execute(query)
            self.connection.commit()

            print("------------------------------------------------------------")
            print(f"КОЛОНКА '{col_name}' ДОБАВЛНА '{tb_name}'")
            print("------------------------------------------------------------")

        except psycopg2.Error as e:
            print(f"{e}")


    #---------------------------------------------------------------------------------------------

    def drop_column_from_table(self, table_name, column_name):
        try:
            cursor = self.connection.cursor()

            query = sql.SQL("ALTER TABLE {} DROP COLUMN {}").format(
                    sql.Identifier(table_name),
                    sql.Identifier(column_name)
            )
            cursor.execute(query)
            self.connection.commit()

            print("------------------------------------------------------------")
            print(f"КОЛОНКА '{column_name}'УДАЛЕНА ИЗ'{table_name}'")
            print("------------------------------------------------------------")

        except psycopg2.Error as e:
            print(f"{e}")

    #---------------------------------------------------------------------------------------------
    def drop_table(self, table_name):
        try:
            cursor = self.connection.cursor()

            query = sql.SQL("DROP TABLE {}").format(
                sql.Identifier(table_name)
            )

            cursor.execute(query)
            self.connection.commit()

            print("------------------------------------------------------------")
            print(f"'{table_name}' DEL")
            print("------------------------------------------------------------")

        except psycopg2.Error as e:
            print(f"{e}")


    #---------------------------------------------------------------------------------------------
    def update_all_column_values(self,table_name, column_name, new_value):
        try:
            query = sql.SQL("UPDATE {} SET {} = {}").format(
                sql.Identifier(table_name),
                sql.Identifier(column_name),
                sql.Literal(new_value)
            )

            cursor.execute(query)
            self.connection.commit()
        except psycopg2.Error as e:
            print(f"{e}")

    #--------------------------------------------------------------------------------------------- END FUNCTIONAL


        
