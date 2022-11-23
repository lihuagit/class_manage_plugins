from services.db_context import db
from services.log import logger
from datetime import datetime
from typing import Optional, List
from utils.image_utils import BuildImage
from pathlib import Path

MY_IMAGE_PATH = Path() / "plugins" / "homework_manage" / "res"

# 声明模型
class HomeworkSub(db.Model):
    __tablename__ = 'homework_sub'

    id = db.Column(db.Integer(), primary_key=True)
    sub_id = db.Column(db.Integer(), nullable=False)
    hw = db.Column(db.String(), default='noname')
    hw_end_date = db.Column(db.DateTime())
    hw_updata_date = db.Column(db.DateTime())

    """
    说明:
        添加作业
    参数:
        :param hw: 作业内容
        :param hw_end_date: 作业截至时间
    """
    @classmethod
    async def add_homework_sub(
        cls,
        hw: str,
        hw_end_date: Optional[datetime] = None,
    ) -> dict:
        try:
            # 统计数据库中的作业数量 给新作业下发合适的作业号
            # 数据库的文档太sb了 找不到可以直接获得数量的api
            query = await cls.query.gino.all()
            hk_count = -1
            for q in query :
                hk_count+=1
            sub = await cls.create(
                sub_id=hk_count+1, hw=hw, hw_end_date=hw_end_date
            )
            return {'res':True, 'msg':'作业添加成功'}
        except Exception as e:
            logger.info(f"homework_sub 添加作业错误 {type(e)}: {e}")
            return {'res':False, 'msg':'添加作业错误'}

    """
    说明:
        删除作业
    参数:
        :param sub_id: 作业id
    """
    @classmethod
    async def delete_homework_sub(cls, sub_id: int) -> dict:
        try:
            async with db.transaction():
                query = (
                    await cls.query.where(
                        (cls.sub_id == sub_id)
                    )
                    .with_for_update()
                    .gino.first()
                )
                if not query:
                    return {'res':False, 'msg':'作业id不存在'}
                await query.delete()
                return {'res':True, 'msg':'作业已删除'}
        except Exception as e:
            logger.info(f"homework_sub 删除作业错误 {type(e)}: {e}")
        return {'res':False, 'msg':'未知 删除作业错误'}

    """
    说明:
        修改作业内容
    参数:
        :param sub_id: 作业id
        :param hw: 作业内容
    """
    @classmethod
    async def update_homework_hw(cls, sub_id: int, hw: str) -> dict:
        try:
            async with db.transaction():
                query = (
                    await cls.query.where(
                        (cls.sub_id == sub_id)
                    )
                    .with_for_update()
                    .gino.first()
                )
                if not query:
                    return {'res':False, 'msg':'作业id不存在'}
                await query.update(hw=hw).apply()
                return {'res':True, 'msg':'作业内容已更新'}
        except Exception as e:
            logger.info(f"homework_sub 作业内容更新错误 {type(e)}: {e}")
        return {'res':False, 'msg':'homework_sub 作业内容更新错误'}
        
    """
    说明:
        修改作业内容
    参数:
        :param sub_id: 作业id
        :param hw_end_date: 作业截至时间
    """
    @classmethod
    async def update_homework_end_date(cls, sub_id: int, hw_end_date: datetime) -> dict:
        try:
            async with db.transaction():
                query = (
                    await cls.query.where(
                        (cls.sub_id == sub_id)
                    )
                    .with_for_update()
                    .gino.first()
                )
                if not query:
                    return {'res':False, 'msg':'作业id不存在'}
                await query.update(hw_end_date=hw_end_date).apply()
                return {'res':True, 'msg':'作业截至时间已更新'}
        except Exception as e:
            logger.info(f"homework_sub 作业截至时间更新错误 {type(e)}: {e}")
        return {'res':False, 'msg':'homework_sub 作业截至时间更新错误'}

    """
    说明:
        获取所有数据
    """
    @classmethod
    async def get_all_sub_data(
        cls,
    ) -> List:
        hk_data = []
        query = await cls.query.order_by(cls.hw_end_date, cls.id).gino.all()
        i=1
        for x in query:
            if x.sub_id == 999 :
                hk_data.append(x)
                continue
            await x.update(sub_id=i).apply()
            i+=1
            hk_data.append(x)
        
        send_rst = "目前的作业有:\n"
        res = True
        for x in hk_data:
            if(x.sub_id == 999):
                send_rst +="\n----------------------------------\n"
                send_rst += f"！！！备注：{x.hw}\n"
                continue
            send_rst += (
                f"\t{x.sub_id} : {x.hw}\n" 
                f"\t\t\t\t  -------- {x.hw_end_date} \n\n"
            )
        if (len(hk_data) == 0):
            send_rst += (
                "       目前没有任何作业...\n"
            )
            res = False
        width = 0
        for x in send_rst.split("\n"):
            _width = len(x) * 24
            width = width if width > _width else _width
        height = len(send_rst.split("\n")) * 35
        A = BuildImage(width, height, font_size=24, is_alpha=True)

        bk = BuildImage(
            w=(int)(width*1.1),
            h=(int)(height*1.25),
            color = (230, 200, 160),
        )
        
        # 获取宽和高的最小值，以便之后以此为标准变换贴图大小
        minn = min(bk.h, bk.w)

        # [229,201,159]
        # 调整背景大小
        # bk.resize(ratio = height/(0.95*bk.h))

        # 白底
        bd = BuildImage(
            w=width,
            h=height,
            background=MY_IMAGE_PATH / "白底.png",
        )

        # 分割线
        fgx = BuildImage(
            w=0,
            h=0,
            background=MY_IMAGE_PATH / "分割线.png",
        )
        fgx.resize(ratio = 0.1*minn/fgx.h)

        # 云1
        y1 = BuildImage(
            w=0,
            h=0,
            background=MY_IMAGE_PATH / "云1.png",
        )
        y1.resize(ratio = 0.15*minn/y1.h)

        # 云2
        y2 = BuildImage(
            w=0,
            h=0,
            background=MY_IMAGE_PATH / "云2.png",
        )
        y2.resize(ratio = 0.15*minn/y2.h)


        # 屏风贴图
        ph = BuildImage(
            w=0,
            h=0,
            background=MY_IMAGE_PATH / "屏风.png",
        )
        ph.resize(ratio = 0.2*minn/ph.h)

        # 钟离贴图
        zl = BuildImage(
            w=0,
            h=0,
            background=MY_IMAGE_PATH / "钟离.png",
        )
        zl.resize(ratio = 0.25*minn/zl.h)

        
        # 胡桃贴图
        ht = BuildImage(
            w=0,
            h=0,
            background=MY_IMAGE_PATH / "胡桃.png",
        )
        ht.resize(ratio = 0.3*minn/ht.h)

        
        # 锅巴贴图
        gb = BuildImage(
            w=0,
            h=0,
            background=MY_IMAGE_PATH / "锅巴.png",
        )
        gb.resize(ratio = 0.2*minn/gb.h)

        # 文字
        A.text((int(width * 0.1), int(height * 0.21)), send_rst)

        bk.paste(img=bd, center_type='center', alpha=True)
        bk.paste(img=fgx, pos=(0, 0), center_type='by_width', alpha=True)
        bk.paste(img=y1, pos=(0, (int)(bk.h*0.05)), alpha=True)
        bk.paste(img=y2, pos=(bk.w-y2.w, (int)(bk.h*0.05)), alpha=True)

        bk.paste(img=ph, pos=(0, bk.h-ph.h), alpha=True)
        bk.paste(img=zl, pos=((int)(0.05*bk.w), bk.h-zl.h), alpha=True)
        bk.paste(img=ht, pos=(bk.w-ht.w, bk.h-ht.h), alpha=True)
        bk.paste(img=gb, pos=((int)(0.35*bk.w), bk.h-gb.h), alpha=True)
        bk.paste(img=A, alpha=True)

        # A.paste(bk, alpha=True)
        # A.text((int(width * 0.048), int(height * 0.21)), send_rst)

        return {'res': res, 'img':bk.pic2bs4()}

# # 增加作业
# async def homework_add(tag_homework, tag_str_date):
#     if(tag_homework == ''): return False
#     tag_str_date_s = tag_str_date.split('-')
#     tag_str_date_s = tag_str_date.split('.')
#     tag_str_date_s = tag_str_date.split('/')
#     if(len(tag_str_date_s) != 3) : return False
#     tag_date=datetime(tag_str_date_s[0], tag_str_date_s[1], tag_str_date_s[2])
#     homework = await HomeworkSub.create(homework=tag_homework, end_date=tag_date)
#     return True




# # 获取所有作业
# async def homework_getall():
#     all_homework = await db.all(Homework.query)
#     return all_homework

# # 获取tag_id的作业
# async def homework_get_by_id(tag_id):
#     homework = await Homework.create(id=tag_id)
#     if( tag_id == homework.id ):
#         return [homework.id, homework.homework, homework.end_date]
#     else :
#         return [-1]
    
# # 更新id的作业内容
# async def homework_updata_homework(tag_id, tag_homework):
#     if(tag_homework == ''): return False
#     homework = await Homework.create(id=tag_id)
#     assert tag_id == homework.id
#     await homework.update(homework=tag_homework)
#     return True
    
# # 更新id的作业截止时间
# async def homework_updata_end_date(tag_id, tag_str_date):
#     tag_str_date_s = tag_str_date.split('-')
#     tag_str_date_s = tag_str_date.split('.')
#     tag_str_date_s = tag_str_date.split('/')
#     if(len(tag_str_date_s) != 3) : return False
#     tag_date=datetime(tag_str_date_s[0], tag_str_date_s[1], tag_str_date_s[2])
#     homework = await Homework.create(id=tag_id)
#     assert tag_id == homework.id
#     await homework.update(end_date=tag_date)
#     return True

# # 删除id作业
# async def homework_del(tag_id):
#     homework = await Homework.create(id=tag_id)
#     await homework.delete() 