from nonebot.plugin import on_command, on_regex
from nonebot.typing import T_State
from nonebot.params import CommandArg, RegexGroup
from nonebot.adapters.onebot.v11 import MessageEvent, Message, GroupMessageEvent, Bot
from nonebot.log import logger
from nonebot.rule import to_me
from datetime import datetime
from utils.utils import is_number, scheduler, get_bot
from utils.image_utils import text2image
from utils.message_builder import image
from .model import HomeworkSub
from .level_user import LevelUser
from typing import Tuple, Optional, Any
from configs.config import Config

__zx_plugin_name__ = "作业通知"
__plugin_usage__ = """
usage：
    作业通知
    指令：[示例Id乱打的，仅做示例]
        添加作业 [作业内容] [作业截至时间] --[管理员命令]
        修改作业内容 [id] [作业内容] --[管理员命令]
        修改作业时间 [id] [作业截至时间] --[管理员命令]
        删除作业 [id] --[管理员命令]
        查看作业

        示例：添加作业 嵌入式三问 2022.01.01
        示例：修改作业内容 1 嵌入式三问
        示例：修改作业时间 1 2022/01/01
        示例：删除作业 1
        示例：查看作业

        备注：修改备注即修改作业内容 id为999
             作业截止时间格式： [年=当前年份]-{月}-{日}-[小时=20]-[分钟=0]-[秒=0]
""".strip()
__plugin_des__ = "作业管理通知bate"
__plugin_cmd__ = [  "添加作业 [作业内容] [作业截至时间]", 
                    "修改作业内容 [id] [作业内容]",
                    "修改作业时间 [id] [作业截至时间]",
                    "删除作业 [id]",
                    "查看作业"
                ]
__plugin_version__ = 0.1
__plugin_author__ = "lihua"

__plugin_settings__ = {
    "level": 5,
    "default_status": True,
    "limit_superuser": False,
    "cmd": ["添加作业", "修改作业内容", "修改作业时间", "删除作业", "查看作业"],
}

__plugin_configs__ = {
    "USER_HOMEWORK_SUB_LEVEL": {
        "value": 5,
        "help": "管理作业的权限",
        "default_value": 5,
    },
    "SUPERUSER_HOMEWORK_SUB_LEVEL": {
        "value": 9,
        "help": "超级管理作业的权限",
        "default_value": 9,
    },
    "SUPERUSER_QQ": {
        "value": 0,
        "help": "超级管理员QQ",
        "default_value": 0,
    },
    "BANJI_QQ": {
        "value": 0,
        "help": "班级QQ",
        "default_value": 0,
    },
}

add_sub = on_command("添加作业", priority=5, block=True)
update_hw_sub = on_command("修改作业内容", priority=5, block=True)
update_end_date_sub = on_command("修改作业时间", priority=5, block=True)
del_sub = on_regex(r"^删除作业[\s\S]*?(\d+)$", priority=5, block=True)
show_sub_info = on_regex("^查看作业$", rule=to_me(),priority=5, block=True)
user_sub = on_command("修改用户权限", priority=5, block=True)

@add_sub.handle()
async def _(event: MessageEvent, state: T_State, arg: Message = CommandArg()):
    if not await LevelUser.check_level(
            event.user_id,
            Config.get_config("homework_manage", "USER_HOMEWORK_SUB_LEVEL"),
        ):
            await add_sub.finish(f"您的权限不足")
    msg = arg.extract_plain_text().strip().split()
    if len(msg) < 2:
        await add_sub.finish("参数不完全，请使用作业命令...\n帮助 作业通知")
    hw_ = msg[0]
    end_date_ = msg[1]
    end_date_ = msg[1].split('-')
    if(len(end_date_) < 2) : 
        end_date_ = msg[1].split('.')
    if(len(end_date_) < 2) : 
        end_date_ = msg[1].split('/')
    if(len(end_date_) < 2) : 
        await update_end_date_sub.finish("作业截至日期格式错误，请使用作业命令...\n帮助 作业通知")
    
    len_end_date_ = len(end_date_)


    year = datetime.now().year
    idx = 0
    month = (int)(end_date_[idx])
    idx += 1
    if(month > 1000):
        year = month
        month = (int)(end_date_[idx])
        idx += 1
    if(len_end_date_ <= idx):
        await update_end_date_sub.finish("作业截至日期格式错误，请使用作业命令...\n帮助 作业通知")
    
    day = (int)(end_date_[idx])
    idx += 1

    hour = 22
    minute = 0
    second = 0

    if(len_end_date_ > idx):
        hour = (int)(end_date_[idx])
        idx += 1
    
    if(len_end_date_ > idx):
        minute = (int)(end_date_[idx])
        idx += 1
    
    if(len_end_date_ > idx):
        second = (int)(end_date_[idx])
        idx += 1
    
    if(len_end_date_ > idx):
        await update_end_date_sub.finish("作业截至日期格式错误，请使用作业命令...\n帮助 作业通知")

    try:
        end_date_ = datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second)
    except:
        await update_end_date_sub.finish("作业截至日期格式错误，请使用作业命令...\n帮助 作业通知")
    res = await HomeworkSub.add_homework_sub(hw_, end_date_)
    if( res['res']) : 
        await add_sub.finish(res['msg'])
    else :
        await add_sub.finish(res['msg'])
    

@del_sub.handle()
async def _(event: MessageEvent, reg_group: Tuple[Any, ...] = RegexGroup()):
    if not await LevelUser.check_level(
            event.user_id,
            Config.get_config("homework_manage", "USER_HOMEWORK_SUB_LEVEL"),
        ):
            await del_sub.finish(f"您的权限不足")

    msg = (int)(reg_group[0])
    res = await HomeworkSub.delete_homework_sub(msg)
    if res['res']:
        logger.info(
            f"(USER {event.user_id}, GROUP "
            f"{event.group_id if isinstance(event, GroupMessageEvent) else 'private'})"
            f" 删除作业 {msg}"
        )
        await del_sub.finish(f"删除作业id：{msg} 成功...")
    else:
        await del_sub.finish(f"删除作业id：{msg} 失败...\n{res['msg']}")
    

    
@update_hw_sub.handle()
async def _(event: MessageEvent, state: T_State, arg: Message = CommandArg()):
    if not await LevelUser.check_level(
            event.user_id,
            Config.get_config("homework_manage", "USER_HOMEWORK_SUB_LEVEL"),
        ):
            await update_hw_sub.finish(f"您的权限不足")
    msg = arg.extract_plain_text().strip().split()
    if len(msg) < 2:
        await update_hw_sub.finish("参数不完全，请使用作业命令...\n帮助 作业通知")
    id_ = (int)(msg[0])
    hw_ = msg[1]
    res = await HomeworkSub.update_homework_hw(id_, hw_)
    if( res['res']) : 
        await update_hw_sub.finish(res['msg'])
    else :
        await update_hw_sub.finish(res['msg'])
    

@update_end_date_sub.handle()
async def _(event: MessageEvent, state: T_State, arg: Message = CommandArg()):
    if not await LevelUser.check_level(
            event.user_id,
            Config.get_config("homework_manage", "USER_HOMEWORK_SUB_LEVEL"),
        ):
            await update_end_date_sub.finish(f"您的权限不足")
    msg = arg.extract_plain_text().strip().split()
    if len(msg) < 2:
        await update_end_date_sub.finish("参数不完全，请使用作业命令...\n帮助 作业通知")
    id_ = (int)(msg[0])
    end_date_ = msg[1]
    end_date_ = msg[1].split('-')
    if(len(end_date_) < 2) : 
        end_date_ = msg[1].split('.')
    if(len(end_date_) < 2) : 
        end_date_ = msg[1].split('/')
    if(len(end_date_) < 2) : 
        await update_end_date_sub.finish("作业截至日期格式错误，请使用作业命令...\n帮助 作业通知")
    
    len_end_date_ = len(end_date_)


    year = datetime.now().year
    idx = 0
    month = (int)(end_date_[idx])
    idx += 1
    if(month > 1000):
        year = month
        month = (int)(end_date_[idx])
        idx += 1
    if(len_end_date_ <= idx):
        await update_end_date_sub.finish("作业截至日期格式错误，请使用作业命令...\n帮助 作业通知")
    
    day = (int)(end_date_[idx])
    idx += 1

    hour = 22
    minute = 0
    second = 0

    if(len_end_date_ > idx):
        hour = (int)(end_date_[idx])
        idx += 1
    
    if(len_end_date_ > idx):
        minute = (int)(end_date_[idx])
        idx += 1
    
    if(len_end_date_ > idx):
        second = (int)(end_date_[idx])
        idx += 1
    
    if(len_end_date_ > idx):
        await update_end_date_sub.finish("作业截至日期格式错误，请使用作业命令...\n帮助 作业通知")

    try:
        end_date_ = datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second)
    except:
        await update_end_date_sub.finish("作业截至日期格式错误，请使用作业命令...\n帮助 作业通知")

    res = await HomeworkSub.update_homework_end_date(id_, end_date_)
    if( res['res']) : 
        await update_end_date_sub.finish(res['msg'])
    else :
        await update_end_date_sub.finish(res['msg'])
    
    
@show_sub_info.handle()
async def _(event: MessageEvent):
    res = await HomeworkSub.get_all_sub_data()
    await show_sub_info.finish(image(b64=res['img']))

@scheduler.scheduled_job(
    "cron",
    hour=20,
    minute=0,
)
async def _():
    res = await HomeworkSub.get_all_sub_data()
    if(res['res'] == True):
        bot = get_bot()
        await bot.send_group_msg(group_id=Config.get_config("homework_manage", "BANJI_QQ"),
                                message=image(b64=res['img']))


@user_sub.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State, arg: Message = CommandArg()):
    if str(event.user_id) not in bot.config.superusers:
        await user_sub.finish(f"您的权限不足")
    msg = arg.extract_plain_text().strip().split()
    if len(msg) < 2:
        await user_sub.finish("参数不完全")
    qq_ = (int)(msg[0])
    level_ = (int)(msg[1])

    if(is_number(qq_) == False or is_number(level_) == False) :
        await user_sub.finish("参数不正确，qq和等级均为数字")

    res = await LevelUser.set_level(qq_, level_)

    if(res):
        await user_sub.finish(f"成功修改用户 {qq_} 权限为 {await LevelUser.get_user_level(qq_)}")
    else:
        await user_sub.finish(f"修改用户权限失败")
    
