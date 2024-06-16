from pydantic_settings import BaseSettings
from langchain.callbacks.tracers import LangChainTracer


class Settings(BaseSettings):
    server_host: str = '0.0.0.0'
    server_port: int = 8000
    debug: bool = False

    tracer = LangChainTracer(project_name="ap_capilot")
    # db_url_xata = "https://Andrey-Petrunin-s-workspace-vdk82p.us-east-1.xata.sh/db/capilot"

    # agent_answer
    aa_model = "gpt-3.5-turbo-1106"
    aa_temperature = 0.0
    aa_top_k = 3
    aa_type_search = 'vector'
    # openai_api_key: str = ''
    # database_uri: str = 'sqlite:///./database.sqlite3'

    # jwt_secret: str
    # jwt_algorithm: str = 'HS256'
    # jwt_expiration: int = 60 * 60 * 24


settings = Settings(
    _env_file='.env',
    _env_file_encoding='utf-8',
)
