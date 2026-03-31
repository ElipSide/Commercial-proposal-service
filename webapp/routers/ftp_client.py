from ftplib import FTP
import os

class FTPClient:
    def __init__(self, server, username, password):
        self.server = server
        self.username = username
        self.password = password
        self.ftp = FTP(self.server)
        self.ftp.login(user=self.username, passwd=self.password)


    def create_directory(self, parent_directory, new_directory_name):
        full_path = f"{parent_directory}/{new_directory_name}"
        if not self.directory_exists(full_path):
            self.ftp.mkd(full_path)
        return full_path

    def directory_exists(self, directory):
        try:
            current_dir = self.ftp.pwd()  # Получаем текущую директорию
            self.ftp.cwd(directory)  # Пытаемся перейти в директорию
            self.ftp.cwd(current_dir)  # Возвращаемся обратно
            return True
        except ftplib.error_perm as e:
            # print(f"Permission error: {str(e)}")
            return False
        except Exception as e:
            # print(f"Error checking directory {directory}: {str(e)}")
            return False

    def delete_directory(self, directory):
        if self.directory_exists(directory):
            self._delete_directory_contents(directory)
            self.ftp.rmd(directory)
            # print(f"dir {directory} del")
        # else:
        #     print(f"dir {directory} not found")

    def _delete_directory_contents(self, directory):
        file_list = []
        self.ftp.retrlines('LIST ' + directory, file_list.append)
        for f in file_list:
            parts = f.split()
            name = parts[-1]
            if f.startswith('d') or f.startswith('D'):
                if name == '.' or name == '..':
                    continue
                # print(f"ound dir: {name}")
                self.delete_directory(f"{directory}/{name}")
            else:
                # print(f"del {name}")
                self.ftp.delete(f"{directory}/{name}")

    def list_files(self, directory):
        file_list = []
        self.ftp.retrlines(f'LIST {directory}', file_list.append)
        return file_list

    def check_connection(self):
        try:
            self.ftp.voidcmd("NOOP")
            # print("active")
        except:
            print("no active")

    def create_user(self, user_name):
        base_path = f"/{user_name}"
        # print(f"Creating base directory: {base_path}")
        self.create_directory("/", user_name)  # Создание основной директории

        # Проверка существует ли базовый путь
        if not self.directory_exists(base_path):
            # print(f"Base directory {base_path} was not created!")
            return

        # Создание подкаталогов
        self.create_directory(base_path, "Xml")
        self.create_directory(base_path, "Check")
        self.create_directory(base_path, "Agrement")
        # print(f"Directories created: {base_path}/Xml, {base_path}/Check, {base_path}/Agrement")

    def upload_file(self, user_name, local_file, remote_directory):
        # print(f"Local file: {local_file}")
        # print(f"Remote directory: {remote_directory}")

        if not os.path.isfile(local_file):
            # print(f"Local file {local_file} does not exist.")
            return

        # Проверка и создание директории
        if not self.directory_exists(remote_directory):
            # print(f"Remote directory {remote_directory} does not exist. Creating...")
            self.create_user(user_name)  # Создать пользователя и его директорию

            if not self.directory_exists(remote_directory):
                # print(f"Failed to create remote directory: {remote_directory}")
                return

        remote_path = os.path.join(remote_directory, os.path.basename(local_file))
        # print(f"Determined remote path: {remote_path}")

        try:
            with open(local_file, 'rb') as file:
                self.ftp.storbinary(f'STOR {remote_path}', file)
                # print(f"File uploaded successfully: {remote_path}")
        except Exception as e:
            print(f"Failed to upload {local_file} to {remote_path}: {str(e)}")

    def close_connection(self):
        self.ftp.quit()






#if __name__ == "__main__":
   # print('SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS')
   # server = '194.63.141.80'
  #  username = 'user2824307'
 #   password = 'Hj2dOu2agcj7'
#
 #   ftp_client = FTPClient(server, username, password)
#
 #   ftp_client.check_connection()

 #   ftp_client.create_user('ООО ТД Полымя')
#
  #  local_file_path = f'/home/sammy/WebAppServer-FastApi-main/webapp/Front/static/document/agrement/PDF/ООО ТД Полымя.pdf'
 #   remote_directory_path = f"ООО ТД Полымя/Xml"
#
 #   ftp_client.upload_file('ООО ТД Полымя', local_file_path, remote_directory_path)
#
 #   files = ftp_client.list_files(remote_directory_path)
#    print("Files in directory:", files)






