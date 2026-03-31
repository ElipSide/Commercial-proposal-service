import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def google_read(name: str) -> str | None:
    crend_path = os.path.join("Front", "static", "json", "crend.json")
    credentials = ServiceAccountCredentials.from_json_keyfile_name(crend_path)
    client = gspread.authorize(credentials)

    spreadsheetId = '1MbyqiWsMyBxDKX3SIeZHIclWqubsXrcYTjkBAEKNvwo'
    worksheet = client.open_by_key(spreadsheetId).worksheet("main")
    tableName = worksheet.col_values(2)[1:]
    tableUrl = worksheet.col_values(3)[1:]
    try:
        if "СмартСорт" in name:
            name = name.replace('(Extra light)', '')
            name = name.split()
            name_spec = name[2].split(".")[0]
            name = ' '.join([name[0], name[1], name_spec, name[3]])
            if name in tableName:
                return tableUrl[tableName.index(name)]
        elif "Конвейер" in name:
            for i, item in enumerate(tableName):
                if name in item:
                    return tableUrl[i]
        else:
            return None
    except Exception as e:
        print(f"Нет такой модели {e}")
    return None
