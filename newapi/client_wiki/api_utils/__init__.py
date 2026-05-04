from .ask_bot import AskBot, showDiff
from .botEdit import (
    bot_May_Edit,
    check_create_time,
    check_last_edit_time,
)

change_codes = {
    "bat_smg": "bat-smg",
    "be-x-old": "be-tarask",
    "be_x_old": "be-tarask",
    "cbk_zam": "cbk-zam",
    "fiu_vro": "fiu-vro",
    "map_bms": "map-bms",
    "nb": "no",
    "nds_nl": "nds-nl",
    "roa_rup": "roa-rup",
    "zh_classical": "zh-classical",
    "zh_min_nan": "zh-min-nan",
    "zh_yue": "zh-yue",
}

__all__ = [
    "AskBot",
    "change_codes",
    "showDiff",
    "bot_May_Edit",
    "check_create_time",
    "check_last_edit_time",
]
