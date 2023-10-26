import os
import dotenv

dotenv.load_dotenv('.env')

token = os.environ["token"]
key = os.environ["key"]
encrypted_data  = os.environ["encrypted_data"]
