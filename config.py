from dataclasses import dataclass
from environs import Env

@dataclass
class Config:
    bot_token: str
    admin_id: int
    db_url: str
    work_group_id: int
    log_group_id: int
    ui_image_file_id: str

def load_config(path: str = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(
        bot_token=env.str("BOT_TOKEN"),
        admin_id=env.int("ADMIN_ID"),
        db_url=env.str("DATABASE_URL"),
        work_group_id=env.int("WORK_GROUP_ID"),
        log_group_id=env.int("LOG_GROUP_ID"),
        ui_image_file_id=env.str("UI_IMAGE_FILE_ID")
    )
