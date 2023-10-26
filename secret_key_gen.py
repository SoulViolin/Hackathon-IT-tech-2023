from cryptography.fernet import Fernet
import json

# Начнем со создания ключа, с помощью которого будут шифроваться и дешифроваться данные
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# Зададим пароль и логин администратора
admin_data = {
    "login": "admin_login",
    "password": "admin_password"
}

data_to_store = json.dumps(admin_data).encode()
encrypted_text = cipher_suite.encrypt(data_to_store)

# Сохраним зашифрованные данные в файл.
with open("secret_admin.dat", "wb") as file:
    file.write(encrypted_text)

with open("secret_key.key", "wb") as file:
    file.write(key)