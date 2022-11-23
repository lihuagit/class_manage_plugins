from nonebot.adapters.onebot.v11 import (
    Bot,
)
from nonebot import on_command
from nonebot.permission import SUPERUSER
from utils.manager import group_manager


__zx_plugin_name__ = "查看所有群权限 [Superuser]"
__plugin_usage__ = """
usage：
    查看所有群权限 操作
    指令：
        查看所有群权限
""".strip()
__plugin_des__ = "查看所有群权限"
__plugin_cmd__ = [
    "查看所有群权限"
]
__plugin_version__ = 0.1
__plugin_author__ = "lihua"

add_group_level = on_command("查看所有群权限", priority=5, permission=SUPERUSER, block=True)


@add_group_level.handle()
async def _(bot: Bot):
    gl = await bot.get_group_list()
    msg = []
    for g in gl :
        msg.append(f"{g['group_id']} {g['group_name']} {group_manager.get_group_level(g['group_id'])}")
    msg = "\n".join(msg)
    msg = f"bot:{bot.self_id}\n| 群号 | 群名 | 共{len(gl)}个群\n" + msg
    await add_group_level.send(msg)
