from dotenv import load_dotenv
import os

load_dotenv('security.env')
print("DB_USER:", os.getenv('DB_USER'))
