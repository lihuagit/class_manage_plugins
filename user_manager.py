from utils.manager.data_class import StaticData
from pathlib import Path

class UserManager(StaticData):
    """
    用户权限 | 管理器
    """

    def __init__(self, file: Path):
        super().__init__(file)
        if not self._data:
            self._data = {
                "user_manager": {},
            }
        self._task = {}
    
    def set_user_level(self, user_id: int, level: int):
        """
        说明:
            设置用户权限
        参数:
            :param user_id: 用户QQ号
            :param level: 权限等级
        """
        user_id = str(user_id)
        if not self._data["user_manager"].get(user_id):
            self._init_group(user_id)
        self._data["user_manager"][user_id]["level"] = level
        self.save()

    def get_user_level(self, user_id: int) -> int:
        """
        说明:
            获取用户等级
        参数:
            :param user_id: 用户QQ号
        """
        user_id = str(user_id)
        if not self._data["user_manager"].get(user_id):
            self._init_group(user_id)
        return self._data["user_manager"][user_id]["level"]