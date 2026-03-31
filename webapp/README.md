# webapp

## Quickstart

Для запуска приложения необходимо выполнить:
```uvicorn main:app --reload ```

## Backend
<!-- csort-news.ru -->
API доступен по адресу ```http://127.0.0.1:8000```

Документация к API: ```http://127.0.0.1:8000/docs```

## Таблицы

```sieve_table``` - список решет, колонки -  `id(key), id_bitrix, sieve_type, size, price, provider`
```calc_sieve```- таблица с данными решет, колонки -  ` product, sieve_type_letter, clean_type, sieve_type, min, max, count_sieve, form_sieve`
```calc_sieve_index``` - таблица с индексом производительности по продукту, колонки -  `product, index`
```separat_table``` - список сепараторов , колонки -`id_provider, id_bitrix, name, name_print, photo, addit_params, addit_equipment, id_row(key), price`
```calc_sieve_size``` - таблица с размером решет, колонки -  ` sieve_form, size`



```provider_list```
# webapp

## Quickstart

Для запуска приложения необходимо выполнить:
```uvicorn main:app --reload ```

## Backend

API доступен по адресу ```http://127.0.0.1:8000```

Документация к API: ```http://127.0.0.1:8000/docs```

## Таблицы

```sieve_table``` - список решет, колонки -  `id(key), id_bitrix, sieve_type, size, price, provider`
```calc_sieve```- таблица с данными решет, колонки -  ` product, sieve_type_letter, clean_type, sieve_type, min, max, count_sieve, form_sieve`
```calc_sieve_index``` - таблица с индексом производительности по продукту, колонки -  `product, index`
```separat_table``` - список сепараторов , колонки -`id_provider, id_bitrix, name, name_print, photo, addit_params, addit_equipment, id_row(key), price`
```calc_sieve_size``` - таблица с размером решет, колонки -  ` sieve_form, size`



```provider_list```


----------------------------------------------------------------------- TABLES LIST ----------------------------------------------------------------------- 

 Schema |         Name          | Type  | Owner 
--------+-----------------------+-------+-------
 public | additional_parameters | table | sammy
 public | calc_sieve            | table | sammy - таблица с данными решет, колонки -
 public | calc_sieve_index      | table | sammy - таблица с индексом производительности по продукту, колонки -
 public | calc_sieve_size       | table | sammy - таблица с размером решет, колонки -
 public | currency              | table | sammy
 public | delivery_terms        | table | sammy
 public | list_of_created_cp    | table | sammy
 public | payment_method        | table | sammy
 public | provider_list         | table | sammy
 public | separat_table         | table | sammy - список сепараторов , колонки -
 public | sessions              | table | sammy
 public | sieve_table           | table | sammy - список решет, колонки -
 public | struct_created_cp     | table | sammy
 public | user_credentials      | table | sammy
 public | user_info             | table | sammy
 public | user_list             | table | sammy
 public | warranty              | table | sammy

----------------------------------------------------------------------- END TABLES LIST ----------------------------------------------------------------------- 




-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
                                            Table "public.additional_parameters"
       Column        |         Type          | Collation | Nullable |                        Default                        
---------------------+-----------------------+-----------+----------+-------------------------------------------------------
 id_row              | integer               |           | not null | nextval('additional_parameters_id_row_seq'::regclass)
 id                  | character varying(30) |           |          | 
 id_bitrix           | character varying(30) |           |          | 
 parameter_name      | character varying(50) |           |          | 
 value               | character varying(30) |           |          | 
 unit_of_measurement | character varying(20) |           |          | 
Indexes:
    "additional_parameters_id_row_key" UNIQUE CONSTRAINT, btree (id_row)



-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
                         Table "public.calc_sieve"
      Column       |         Type          | Collation | Nullable | Default 
-------------------+-----------------------+-----------+----------+---------
 product           | character varying(25) |           |          | 
 sieve_type_letter | character varying(5)  |           |          | 
 clean_type        | character(40)         |           |          | 
 sieve_type        | character(40)         |           |          | 
 min               | integer               |           |          | 
 max               | integer               |           |          | 
 count_sieve       | integer               |           |          | 
 form_sieve        | character(40)         |           |          | 
 id_provider       | integer               |           |          | 1



-----------------------------------------------------------------------------------------------------------------------------------------------------------------------


                   Table "public.calc_sieve_index"
   Column    |         Type          | Collation | Nullable | Default 
-------------+-----------------------+-----------+----------+---------
 product     | character varying(65) |           |          | 
 index       | double precision      |           |          | 
 id_provider | integer               |           |          | 1



-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
                                     Table "public.calc_sieve_size"
   Column   |         Type          | Collation | Nullable |                   Default                   
------------+-----------------------+-----------+----------+---------------------------------------------
 sieve_form | character varying(25) |           |          | 
 size       | double precision      |           |          | 
 id         | integer               |           | not null | nextval('calc_sieve_size_id_seq'::regclass)
Indexes:
    "calc_sieve_size_pkey" PRIMARY KEY, btree (id)

-----------------------------------------------------------------------------------------------------------------------------------------------------------------------

                                           Table "public.currency"
        Column         |         Type          | Collation | Nullable |               Default                
-----------------------+-----------------------+-----------+----------+--------------------------------------
 id                    | integer               |           | not null | nextval('currency_id_seq'::regclass)
 id_supplier           | character varying(30) |           |          | 
 standard_abbreviation | character varying(20) |           |          | 
 common_designation    | character varying(20) |           |          | 
Indexes:
    "currency_pkey" PRIMARY KEY, btree (id)

-----------------------------------------------------------------------------------------------------------------------------------------------------------------------

                                          Table "public.delivery_terms"
       Column       |          Type          | Collation | Nullable |                  Default                   
--------------------+------------------------+-----------+----------+--------------------------------------------
 id                 | integer                |           | not null | nextval('delivery_terms_id_seq'::regclass)
 id_supplier        | character varying(30)  |           |          | 
 delivery_timeframe | character varying(50)  |           |          | 
 discount_value     | numeric(5,2)           |           |          | 
 text               | character varying(200) |           |          | 
Indexes:
    "delivery_terms_pkey" PRIMARY KEY, btree (id)


-----------------------------------------------------------------------------------------------------------------------------------------------------------------------

                                          Table "public.list_of_created_cp"
     Column     |            Type             | Collation | Nullable |                    Default                     
----------------+-----------------------------+-----------+----------+------------------------------------------------
 id             | integer                     |           | not null | nextval('list_of_created_cp_id_seq'::regclass)
 user_id_tg     | character varying(30)       |           | not null | 
 key_cp         | character varying(30)       |           |          | 
 short_title    | character varying(50)       |           |          | 
 creation_date  | timestamp without time zone |           |          | CURRENT_TIMESTAMP
 currency       | character varying(6)        |           |          | 
 payment_method | character varying(30)       |           |          | 
 delivery_term  | character varying(30)       |           |          | 
 warranty       | character varying(50)       |           |          | 
 manager_id_tg  | character varying(30)       |           |          | 
Indexes:
    "list_of_created_cp_pkey" PRIMARY KEY, btree (id)
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------

                                           Table "public.payment_method"
        Column        |          Type          | Collation | Nullable |                  Default                   
----------------------+------------------------+-----------+----------+--------------------------------------------
 id                   | integer                |           | not null | nextval('payment_method_id_seq'::regclass)
 id_supplier          | character varying(30)  |           |          | 
 payment_distribution | character varying(50)  |           |          | 
 discount_value       | character varying(50)  |           |          | 
 text                 | character varying(200) |           |          | 
Indexes:
    "payment_method_pkey" PRIMARY KEY, btree (id)
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------

                             Table "public.provider_list"
         Column         |          Type          | Collation | Nullable |   Default   
------------------------+------------------------+-----------+----------+-------------
 id                     | bigint                 |           | not null | 
 organization_fullname  | character varying(200) |           |          | 
 organization_shortname | character varying(50)  |           |          | 
 country                | character varying(30)  |           |          | 
 city                   | character varying(30)  |           |          | 
 inn                    | character varying(20)  |           |          | 
 ogrn                   | bigint                 |           |          | 
 kpp                    | bigint                 |           |          | 
 address                | character varying(200) |           |          | 
 index                  | bigint                 |           |          | 
 phone_number           | character varying(20)  |           |          | 
 email                  | character varying(50)  |           |          | 
 bic                    | character varying(20)  |           |          | 
 bank_info              | character varying(200) |           |          | 
 checking_account       | character varying(20)  |           |          | 
 corporate_account      | character varying(20)  |           |          | 
 first_name             | character varying(50)  |           |          | 
 second_name            | character varying(50)  |           |          | 
 surname                | character varying(50)  |           |          | 
 position_user          | character varying(50)  |           |          | 
 acts_basis             | character varying(50)  |           |          | 
 number_proxy           | character varying(100) |           |          | 
 seal_photo             | character varying(30)  |           |          | 
 signature_photo        | character varying(30)  |           |          | 
 equipment              | jsonb                  |           | not null | '{}'::jsonb
Indexes:
    "provider_list_pkey" PRIMARY KEY, btree (id)
    "provider_list_organization_fullname_key" UNIQUE CONSTRAINT, btree (organization_fullname)
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------

                                          Table "public.separat_table"
     Column      |         Type          | Collation | Nullable |                    Default                    
-----------------+-----------------------+-----------+----------+-----------------------------------------------
 id_provider     | bigint                |           | not null | 
 id_bitrix       | bigint                |           |          | 
 name            | character varying(50) |           |          | 
 name_print      | character varying(50) |           |          | 
 photo           | character varying(50) |           |          | 
 addit_params    | boolean               |           |          | 
 addit_equipment | boolean               |           |          | 
 id_row          | integer               |           | not null | nextval('separat_table_id_row_seq'::regclass)
 price           | integer               |           |          | 
Indexes:
    "separat_table_pkey" PRIMARY KEY, btree (id_row)
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------

                                              Table "public.sessions"
       Column       |            Type             | Collation | Nullable |                 Default                  
--------------------+-----------------------------+-----------+----------+------------------------------------------
 id                 | integer                     |           | not null | nextval('sessions_id_seq'::regclass)
 id_tg              | character varying(25)       |           |          | 
 refresh_token      | character varying(25)       |           |          | '000'::character varying
 access_token       | character varying(25)       |           |          | '000'::character varying
 refresh_token_time | timestamp without time zone |           |          | '-infinity'::timestamp without time zone
 access_token_time  | timestamp without time zone |           |          | '-infinity'::timestamp without time zone
 refresh_token_hash | character varying(100)      |           |          | '000'::character varying
 access_token_hash  | character varying(100)      |           |          | '000'::character varying
 salt               | character varying(60)       |           |          | '000'::character varying
 id_device          | character varying(60)       |           |          | '000'::character varying
Indexes:
    "sessions_pkey" PRIMARY KEY, btree (id)
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------

                      Table "public.sieve_table"
   Column   |          Type          | Collation | Nullable | Default 
------------+------------------------+-----------+----------+---------
 id         | bigint                 |           | not null | 
 id_bitrix  | bigint                 |           |          | 
 sieve_type | character varying(100) |           |          | 
 size       | double precision       |           |          | 
 price      | bigint                 |           |          | 
 provider   | bigint                 |           |          | 
Indexes:
    "sieve_table_pkey" PRIMARY KEY, btree (id)
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------

                                     Table "public.struct_created_cp"
   Column   |       Type        | Collation | Nullable |                      Default                      
------------+-------------------+-----------+----------+---------------------------------------------------
 cp_key     | character varying |           | not null | nextval('struct_created_cp_cp_key_seq'::regclass)
 price      | integer           |           |          | 
 group_info | json              |           |          | 
Indexes:
    "struct_created_cp_pkey" PRIMARY KEY, btree (cp_key)

                  Table "public.user_credentials"
  Column   |         Type          | Collation | Nullable | Default 
-----------+-----------------------+-----------+----------+---------
 id_tg     | character varying(25) |           | not null | 
 login     | character varying(50) |           |          | 
 password  | bytea                 |           |          | 
 id_device | character varying(60) |           |          | 
Indexes:
    "user_credentials_pkey" PRIMARY KEY, btree (id_tg)
    "unique_login" UNIQUE CONSTRAINT, btree (login)

-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
                        Table "public.user_info"
    Column    |          Type          | Collation | Nullable | Default 
--------------+------------------------+-----------+----------+---------
 id_tg        | character varying(25)  |           | not null | 
 surname      | character varying(40)  |           |          | 
 name         | character varying(40)  |           |          | 
 middle_name  | character varying(40)  |           |          | 
 phone_number | character varying(20)  |           |          | 
 mail         | character varying(40)  |           |          | 
 language     | character varying(15)  |           |          | 
 data_reg     | date                   |           |          | 
 access_level | character varying(40)  |           |          | 
 photo        | character varying(255) |           |          | 
 company      | character varying(50)  |           |          | 
 login        | character varying(25)  |           |          | 
Indexes:
    "user_info_pkey" PRIMARY KEY, btree (id_tg)
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------

                                      Table "public.user_list"
         Column         |            Type             | Collation | Nullable |        Default        
------------------------+-----------------------------+-----------+----------+-----------------------
 id_tg                  | character varying(15)       |           |          | 
 analysis_link          | character varying(40)       |           |          | ''::character varying
 analytics_photo        | character varying(40)       |           |          | ''::character varying
 pdf_kp                 | boolean                     |           |          | false
 agreement_kp           | boolean                     |           |          | false
 invoice_kp             | character varying(40)       |           |          | ''::character varying
 organization           | character varying(40)       |           |          | ''::character varying
 inn                    | character varying(30)       |           |          | ''::character varying
 adress                 | character varying(40)       |           |          | ''::character varying
 phone_number           | character varying(30)       |           |          | ''::character varying
 email                  | character varying(50)       |           |          | ''::character varying
 bic                    | character varying(20)       |           |          | ''::character varying
 checking_account       | character varying(25)       |           |          | ''::character varying
 first_name             | character varying(30)       |           |          | ''::character varying
 second_name            | character varying(30)       |           |          | ''::character varying
 surname                | character varying(30)       |           |          | ''::character varying
 position_user          | character varying(50)       |           |          | ''::character varying
 acts_basis             | character varying(50)       |           |          | ''::character varying
 number_proxy           | character varying(100)      |           |          | ''::character varying
 contract_ready         | boolean                     |           |          | false
 agreement_signed       | boolean                     |           |          | false
 invoice_sent           | boolean                     |           |          | false
 lastmanager_invoice    | timestamp without time zone |           |          | 
 height                 | integer                     |           |          | 0
 city                   | character varying(30)       |           |          | ''::character varying
 organization_shortname | character varying(30)       |           |          | ''::character varying
 organization_fullname  | character varying(40)       |           |          | ''::character varying
 ogrn                   | character varying(40)       |           |          | ''::character varying
 kpp                    | character varying(40)       |           |          | ''::character varying
 bank_info              | character varying(40)       |           |          | ''::character varying
 corporate_account      | character varying(40)       |           |          | ''::character varying
Indexes:
    "user_list_id_tg_key" UNIQUE CONSTRAINT, btree (id_tg)
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
                                        Table "public.warranty"
     Column      |          Type          | Collation | Nullable |               Default                
-----------------+------------------------+-----------+----------+--------------------------------------
 id              | integer                |           | not null | nextval('warranty_id_seq'::regclass)
 id_supplier     | character varying(30)  |           |          | 
 warranty_period | character varying(50)  |           |          | 
 discount_value  | numeric(5,2)           |           |          | 
 text            | character varying(200) |           |          | 
Indexes:
    "warranty_pkey" PRIMARY KEY, btree (id)


