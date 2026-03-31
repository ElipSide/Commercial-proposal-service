from db.db_ext import Database
from datetime import datetime, timedelta
import json
import re
class UserRepository:
    def __init__(self, db: Database):
        self.db = db

    #GEN QUERY ------------------------------------------------------------------------------------------------------------------------------------------------------
    def generate_insert_query(self, table_name, data):
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        values = list(data.values())
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        return query, values

    def generate_select_query(self, table_name, columns='*', where_conditions=None):
        query = f"SELECT {columns} FROM {table_name}"
        params = []

        if where_conditions:
            if isinstance(where_conditions, dict):
                conditions = ' AND '.join(f"{key} = %s" for key in where_conditions.keys())
                query += f" WHERE {conditions}"
                params = tuple(where_conditions.values())
        return query, params

    def generate_update_query(self, table_name, primary_key_column, new_data):
        update_columns = ', '.join(f"{key} = %s" for key in new_data if key != primary_key_column)
        values = [new_data[key] for key in new_data if key != primary_key_column]
        values.append(new_data[primary_key_column])
        query = f"UPDATE {table_name} SET {update_columns} WHERE {primary_key_column} = %s"
        return query, values
    def generate_bulk_update_query(self, table_name, primary_key_column, data_rows):
        
        if not data_rows:
            raise ValueError("No data provided for bulk update")
        
        sample_row = data_rows[0]
        update_columns = [key for key in sample_row if key != primary_key_column]
        
        if not update_columns:
            raise ValueError("No columns to update (only primary key provided)")
        
        query_parts = [f"UPDATE {table_name} SET"]
        case_statements = []
        values = []
        for column in update_columns:
            case_parts = [f"{column} = CASE {primary_key_column}"]
            
            for row in data_rows:
                if primary_key_column not in row:
                    raise ValueError(f"Primary key '{primary_key_column}' missing in one of the rows")
                
                case_parts.append(f"WHEN %s THEN %s")
                values.append(row[primary_key_column])
                values.append(row.get(column))
                
            case_parts.append(f"ELSE {column} END") 
            case_statements.append(" ".join(case_parts))
        
        query_parts.append(", ".join(case_statements))
        
        # Добавляем WHERE для всех ID которые мы обновляем
        primary_key_values = [row[primary_key_column] for row in data_rows]
        placeholders = ", ".join(["%s"] * len(primary_key_values))
        query_parts.append(f"WHERE {primary_key_column} IN ({placeholders})")
        values.extend(primary_key_values)
        
        query = " ".join(query_parts)
        return query, values
    def generate_update_query_mult(self, table_name, new_data, condition_columns):
        update_columns = ', '.join(f"{key} = %s" for key in new_data)
        values = list(new_data.values())
        conditions = [f"{col} IN (%s)" for col in condition_columns]
        condition_values = [new_data[col] for col in condition_columns]
        values.extend(condition_values)
        where_clause = ' AND '.join(conditions)
        query = f"UPDATE {table_name} SET {update_columns} WHERE {where_clause}"

        return query, values
    def generate_delete_query(self, table_name, primary_key, data):
        query = f"DELETE FROM {table_name} WHERE {primary_key} = %s"
        return query, [data]
    def generate_arr_delete_query(self, table_name, primary_key, data_list):
    
        if not data_list:
            raise ValueError("Список данных для удаления не может быть пустым")
        
        placeholders = ', '.join(['%s'] * len(data_list))
        query = f"DELETE FROM {table_name} WHERE {primary_key} IN ({placeholders})"
        return query, data_list
    # GEN QUERY ------------------------------------------------------------------------------------------------------------------------------------------------------

    async def insert_row(self, table_name, data):
        try:
            query, values = self.generate_insert_query(table_name, data)
            await self.db.execute_statement(query, values)
        except Exception as e:
            print(f"Error inserting data: {e}")

    async def update_row(self, table_name, primary_key, data):
        try:
            query, values = self.generate_update_query(table_name, primary_key, data)
            await self.db.execute_statement(query, values)
        except Exception as e:
            print(f"{e}")

    async def update_rows(self, table_name, primary_key_column, data_rows):
        if not data_rows:
            return
        try:
            query, all_values = self.generate_bulk_update_query(table_name, primary_key_column, data_rows)
            await self.db.execute_statement(query, all_values)
        except Exception as e:
            print(f"{e}")

    async def update_row_mult_cond(self, table_name, condition_columns, data):
        try:
            query, values = self.generate_update_query_mult(table_name, data, condition_columns)
            await self.db.execute_statement(query, values)
        except Exception as e:
            print(f"{e}")


    async def select_row(self, table_name, columns_to_get='*', conditions=None):
        try:
            query, values = self.generate_select_query(table_name, columns_to_get, conditions)
            result = await self.db.execute_select_statement(query, values)
            return  result

        except Exception as e:
            print(f"{e}")

    async def execute_func(self, params):
        result = await self.db.execute_func(params)
        return  result
    
    async def delete_row(self, table_name, primary_key, data):
        try:
            query, values = self.generate_delete_query(table_name, primary_key, data)
            await self.db.execute_statement(query, values)
        except Exception as e:
            print(f"{e}")
    async def delete_row_arr(self, table_name, primary_key, data):
        try:
            query, values = self.generate_arr_delete_query(table_name, primary_key, data)
            await self.db.execute_statement(query, values)
        except Exception as e:
            print(f"{e}")
            
    #INSERT ------------------------------------------------------------------------------------------------------------------------------------------------------

    async def update_user_info(self, data):
        try:
            query, values = self.generate_update_query('user_info', 'id_tg', data)
            await self.db.execute_statement(query, values)
        except Exception as e:
            print(f"{e}")

    async def insert_data(self, data):
        key_value = data.get('key')
        id_tg_value = data.get('id_tg')
        data_json_value = json.dumps(data.get('data_json'))
        len_photo_value = data.get('len_photo')
        product = data.get('product')

        insert_query = "INSERT INTO analytic_sieve (key, id_tg, data_json, len_photo, product) VALUES (%s, %s, %s, %s, %s);"
        await self.db.execute_statement(insert_query, (key_value, id_tg_value, data_json_value, len_photo_value, product))

    #SELECT ------------------------------------------------------------------------------------------------------------------------------------------------------
    async def get_user_by_telegram_id_access_level(self, id_tg_value: str):
        query = "SELECT access_level FROM user_info WHERE id_tg = %s;"
        result = await self.db.execute_select_statement(query, (id_tg_value,))
        if result:
            access_level = result[0]
            return access_level[0]
        return None
    async def get_user_by_telegram_id_language_code(self, id_tg_value: str):
        query = "SELECT language FROM user_info WHERE id_tg = %s;"
        result = await self.db.execute_select_statement(query, (id_tg_value,))
        if result:
            access_level = result[0]
            return access_level[0]
        return None
    
    async def get_user_by_telegram_id(self, table: str, id_tg_value: str):
        allowed_tables = ['user_info', 'user_list']

        if table not in allowed_tables:
            raise ValueError("Invalid table name")

        query = f"SELECT * FROM {table} WHERE id_tg = %s;"
        result = await self.db.execute_select_statement(query, (id_tg_value,))
        if result:
            return result[0]
        return None

    async def get_user_by_key_from_list_of_created_cp(self, key: str):
        query = "SELECT user_id_tg FROM list_of_created_cp WHERE key_cp = %s;"
        result = await self.db.execute_select_statement(query, (key,))
        if result:
            id_user = result[0]
            return id_user[0]
        return None

    async def get_struct_created_cp_by_cp_key(self, cp_key: str):
        query = "SELECT * FROM struct_created_cp WHERE cp_key = %s;"
        result = await self.db.execute_select_statement(query, (cp_key,))
        return result

    async def get_list_of_created_cp_by_cp_key(self, cp_key: str):
        query = "SELECT * FROM list_of_created_cp WHERE key_cp = %s;"
        result = await self.db.execute_select_statement(query, (cp_key,))
        return result

    async def get_data_an_sieve_by_key(self, key: str):
        query = "SELECT * FROM analytic_sieve WHERE key = %s;"
        result = await self.db.execute_select_statement(query, (key,))
        return result


    async def find_rows_by_days_and_supplier(self, days_period:int, company: str):
        current_date = datetime.now().date()
        new_date = current_date - timedelta(days=days_period)

        current_date_str = current_date.strftime('%Y-%m-%d')
        new_date_str = new_date.strftime('%Y-%m-%d')
        print(current_date_str)
        print(new_date_str)

        query = f"""
            SELECT id_row, service, document, supplier, buyer, supplier_id, sum, 
                   creation_date, key, fio_manager
            FROM statistics_of_generated_documents 
            WHERE creation_date BETWEEN '{new_date_str}' AND '{current_date_str}' 
            AND supplier = '{company}';
            """
        result = await self.db.execute_select_statement(query)
        print(result)
        return result
    

    async def get_alllink_stat(self, id_tg: str):
        query = "SELECT * FROM transition_statistics WHERE id_tg = %s;"
        result = await self.db.execute_select_statement(query, (id_tg,))
        return result

#-----------------------------------------------------------------------------------------
    async def get_all_service_info(self, lang):
        query = "SELECT * FROM service WHERE language = %s;"
        result = await self.db.execute_select_statement(query, (lang,))
        return result
    async def get_all_group_names_info(self, lang):
        query = "SELECT * FROM group_names WHERE language = %s;"
        result = await self.db.execute_select_statement(query, (lang,))
        return result

    async def get_all_attendance_info(self, lang):
        query = "SELECT * FROM attendance WHERE language = %s;"
        result = await self.db.execute_select_statement(query, (lang,))
        return result
    async def get_all_provider_list_info(self):
        query = "SELECT * FROM provider_list WHERE id IN (3, 4);"
        result = await self.db.execute_select_statement(query)
        return result

    async def get_all_warranty_info(self, lang):
        query = "SELECT * FROM warranty WHERE language = %s;"
        result = await self.db.execute_select_statement(query, (lang,))
        return result

    async def get_all_delivery_terms_info(self, lang):
        query = "SELECT * FROM delivery_terms WHERE language = %s;"
        result = await self.db.execute_select_statement(query, (lang,))
        return result

    async def get_all_payment_method_info(self, lang):
        query = "SELECT * FROM payment_method WHERE language = %s;"
        result = await self.db.execute_select_statement(query, (lang,))
        return result

    async def get_all_additional_parameters_info(self, lang):
        query = "SELECT * FROM additional_parameters WHERE language = %s;"
        result = await self.db.execute_select_statement(query, (lang,))
        return result

    async def get_all_contractor_info(self):
        query = "SELECT * FROM contractor;"
        result = await self.db.execute_select_statement(query)
        return result

    async def get_all_calc_sieve_info(self, lang):
        query = "SELECT * FROM calc_sieve WHERE language = %s;"
        result = await self.db.execute_select_statement(query, (lang,))
        return result
    
    async def get_column_translations(self):
        query = "SELECT * FROM column_translations;"
        result = await self.db.execute_select_statement(query)
        return result
    async def get_all_calc_sieve_index_info(self, lang):
        query = "SELECT * FROM calc_sieve_index WHERE language = %s;"
        result = await self.db.execute_select_statement(query, (lang,))
        return result

    async def get_all_sieve_table_info(self, lang):
        query = "SELECT * FROM sieve_table WHERE language = %s AND id_provider IN (3, 4);"
        result = await self.db.execute_select_statement(query, (lang,))
        return result

    async def get_all_separat_table_info(self, lang):
        query = "SELECT * FROM separat_table WHERE language = %s AND id_provider IN (3, 4);"
        result = await self.db.execute_select_statement(query, (lang,))
        return result

    async def get_all_sieve_size_info(self):
        query = "SELECT * FROM sieve_size;"
        result = await self.db.execute_select_statement(query)
        return result

    async def get_all_photo_separators_info(self, lang):
        query = "SELECT * FROM photo_separators WHERE language = %s AND id_provider IN (3, 4);"
        result = await self.db.execute_select_statement(query, (lang,))
        return result
    async def get_all_elevator_info(self, lang):
        query = "SELECT * FROM elevator WHERE language = %s;"
        result = await self.db.execute_select_statement(query, (lang,))
        return result
    async def get_all_compressors_info(self, lang):
        query = "SELECT * FROM compressors WHERE language = %s;"
        result = await self.db.execute_select_statement(query, (lang,))
        return result

    async def get_all_extra_equipment_info(self, lang):
        query = "SELECT * FROM extra_equipment WHERE language = %s;"
        result = await self.db.execute_select_statement(query, (lang,))
        return result
    
    async def get_all_pneumatic_feed(self, lang):
        query = "SELECT * FROM pneumatic_feed WHERE language = %s;"
        result = await self.db.execute_select_statement(query, (lang,))
        return result
    async def get_all_laboratory_equipment_info(self, lang):
        query = "SELECT * FROM laboratory_equipment WHERE language = %s;"
        result = await self.db.execute_select_statement(query,(lang,))
        return result
    
    async def get_perfom_config_photoseparators_info(self, lang):
        query = "SELECT * FROM perfom_config_photoseparators WHERE language = %s;"
        result = await self.db.execute_select_statement(query, (lang,))
        return result
    
    async def get_compressor_perfomance_info(self):
        query = "SELECT * FROM compressor_perfomance;"
        result = await self.db.execute_select_statement(query)
        return result

    async def get_Gost_info(self):
        query = "SELECT * FROM colorsorter_gost;"
        result = await self.db.execute_select_statement(query)
        return result


#-----------------------------------------------------------------------------------------
    async def save_changed_price_List(self ,data):
        query = """
        INSERT INTO change_price_cp (cp_key, change_price)
        VALUES (%s, %s)
        """
        changed_price_List = json.dumps(data['changed_price_List'])

        params = (
            data['cp_key'],
            changed_price_List
        )
        await self.db.execute_statement(query, params)

    async def update_changed_price_List(self, data):
        query = """
        UPDATE change_price_cp
        SET change_price = %s
        WHERE cp_key = %s
        """
        changed_price_List = json.dumps(data['changed_price_List'])
        params = (
            changed_price_List,
            data['cp_key']
        )
        await self.db.execute_statement(query, params)

    async def save_changed_sale_List(self ,data):
        query = """
        INSERT INTO change_sale_cp (cp_key, change_sale)
        VALUES (%s, %s)
        """
        changed_sale_List = json.dumps(data['changed_sale_List'])

        params = (
            data['cp_key'],
            changed_sale_List
        )
        await self.db.execute_statement(query, params)

    async def update_changed_sale_List(self, data):
        query = """
        UPDATE change_sale_cp
        SET change_sale = %s
        WHERE cp_key = %s
        """
        changed_sale_List = json.dumps(data['changed_sale_List'])
        params = (
            changed_sale_List,
            data['cp_key']
        )
        await self.db.execute_statement(query, params)


    # admin
    async def get_all_name_tables(self):
        query = "SELECT * FROM name_tables"
        result = await self.db.execute_select_statement(query)
        return result
    
    async def get_all_info_tables(self, name_tables: str) -> list:
        query = """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = %s
            ORDER BY ordinal_position
        """
        result = await self.db.execute_select_statement(query, (name_tables,))
        print(result)
        return [row[0] for row in result]

    async def get_data_choice_table(self, name_tables: str) -> dict:

        # Проверка имени таблицы (только буквы, цифры и _)
        if not re.match(r'^[a-zA-Z0-9_]+$', name_tables):
            raise ValueError("Invalid table name")

        query = """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = %s
            ORDER BY ordinal_position
        """
        cursor = await self.db.execute_select_statement(query, (name_tables,))
        columns = [row[0] for row in cursor]

        data_query = f'SELECT * FROM "{name_tables}"'
        req = await self.db.execute_select_statement(data_query)

        data_res = [
            dict(zip(columns, item))
            for item in req
        ]

        return {"columns": columns, "data": data_res}


    
    
    