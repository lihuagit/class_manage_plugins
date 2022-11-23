from asyncpg import UniqueViolationError

from services.db_context import db


class LevelUser(db.Model):
    __tablename__ = "homework_level_users"

    id = db.Column(db.Integer(), primary_key=True)
    user_qq = db.Column(db.BigInteger(), nullable=False)
    user_level = db.Column(db.BigInteger(), nullable=False)

    @classmethod
    async def get_user_level(cls, user_qq: int) -> int:
        """
        说明:
            获取用户的等级
        参数:
            :param user_qq: qq号
        """
        query = cls.query.where(cls.user_qq == user_qq)
        user = await query.gino.first()
        if user:
            return (int)(user.user_level)
        else:
            return -1

    @classmethod
    async def set_level(
        cls, user_qq: int, level: int) -> bool:
        """
        说明:
            设置用户权限
        参数:
            :param user_qq: qq号
            :param level: 权限等级
        """
        print(user_qq)
        query = cls.query.where(cls.user_qq == user_qq)
        query = query.with_for_update()
        user = await query.gino.first()
        try:
            if not user:
                await cls.create(
                    user_qq=user_qq,
                    user_level=level,
                )
                print(cls.user_qq)
                return True
            else:
                await user.update(user_level=level).apply()
                return True
        except UniqueViolationError:
            return False

    @classmethod
    async def delete_level(cls, user_qq: int) -> bool:
        """
        说明:
            删除用户权限
        参数:
            :param user_qq: qq号
        """
        query = cls.query.where(cls.user_qq == user_qq)
        query = query.with_for_update()
        user = await query.gino.first()
        if user is None:
            return False
        else:
            await user.delete()
            return True

    @classmethod
    async def check_level(cls, user_qq: int, level: int) -> bool:
        """
        说明:
            检查用户权限等级是否大于 level
        参数:
            :param user_qq: qq号
            :param level: 权限等级
        """
        query = cls.query.where(cls.user_qq == user_qq)
        user = await query.gino.first()
        if user is None:
            return False
        user_level = user.user_level
        if user_level >= level:
            return True
        else:
            return False