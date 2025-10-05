import os
from dataclasses import dataclass
from typing import Final

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    bot_token: str
    admin_user_id: int | None = None


def get_settings() -> Settings:
    load_dotenv()

    env_var_name: Final[str] = "BOT_TOKEN"
    token = os.getenv(env_var_name)
    if not token:
        raise RuntimeError(
            f"Environment variable {env_var_name} is missing. "
            "Create a .env file (or set the variable) with BOT_TOKEN=YOUR_TOKEN"
        )
    admin_id_raw = os.getenv("ADMIN_USER_ID")
    admin_user_id = None
    if admin_id_raw:
        try:
            admin_user_id = int(admin_id_raw)
        except ValueError:
            raise RuntimeError("ADMIN_USER_ID должен быть числом (telegram user id)")

    return Settings(bot_token=token, admin_user_id=admin_user_id)


