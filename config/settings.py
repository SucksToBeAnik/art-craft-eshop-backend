# Settings to make the evironment variables useable throughout the project
from dotenv import find_dotenv, dotenv_values

env_path = find_dotenv()
env_values = dotenv_values(env_path)


class Settings:
    admin_emails = env_values['ADMIN_EMAILS'] or "[anik.islam1494@gmail.com]"

    admin_emails = admin_emails[1:-1].replace(" ","").split(',')

