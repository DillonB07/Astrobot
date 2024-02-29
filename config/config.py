import yaml

class Config:
    def __init__(self, filepath: str):
        with open(filepath) as f:
            parsed = yaml.full_load(f).get("config")

        # Required config for running
        self.PREFIX: str = parsed.get("prefix")
        self.SERVER_ID: int = parsed.get("server_id")
        self.ADMIN_ROLE_ID: int = parsed.get("admin_role_id")
        self.DISCORD_TOKEN: str = parsed.get("discord_token")
        self.BOT_SECRET_KEY: str = parsed.get("db_secret_key")
        self.DATABASE_CONNECTION: str = parsed.get("database_connection")

        # Optional config
        self.OPENAI_API_KEY: str = parsed.get("openai_api_key")
        self.AI_INCLUDE_NAMES: bool = parsed.get("ai_include_names")
        self.AI_CHAT_CHANNELS: list[int] = parsed.get("ai_chat_channels")
        self.AI_SYSTEM_PROMPT: str = parsed.get("ai_system_prompt")
        self.PORTAINER_API_KEY: str = parsed.get("portainer_api_key")

        # Configuration
        self.LOG_LEVEL: str = parsed.get("log_level")
        self.SQL_LOGGING: bool = parsed.get("log_sql")
        self.KARMA_TIMEOUT: int = parsed.get("karma_cooldown")
        self.REMINDER_SEARCH_INTERVAL: int = parsed.get("reminder_search_interval")
        self.CHANNEL_CHECK_INTERVAL: int = parsed.get("channel_check_interval")
        self.UNICODE_NORMALISATION_FORM: str = "NFKD"
        self.PYROMANIAC_URL: str = parsed.get("pyromaniac_url")

CONFIG = Config("config.yaml")
