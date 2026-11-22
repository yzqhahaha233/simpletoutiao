from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

class UserRequest(BaseModel):
    username:str
    password:str

class UserInfoBase(BaseModel):
    # 允许从 ORM 对象读取属性, 子类会继承该配置
    model_config = ConfigDict(from_attributes=True)

    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=255, description="头像URL")
    gender: Optional[str] = Field(None, max_length=10, description="性别")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")

class UserInfoResponse(UserInfoBase):
    id: int
    username: str
    model_config = ConfigDict(
        from_attributes=True  # 允许从 ORM 对象属性中取值
    )


class UserAuthResponse(BaseModel):
    # 不继承 UserInfoResponse, 否则会多出 id/username 两个必填字段
    token: str
    user_info: UserInfoResponse=Field(...,alias='userInfo')
    model_config = ConfigDict(populate_by_name=True,from_attributes=True)

class UserUpdateRequest(BaseModel):
    nickname: str = None
    avatar: str = None
    gender: str = None
    bio: str = None
    phone: str = None


class UserChangePasswordRequest(BaseModel):
    # populate_by_name: 允许用字段名(old_password)或别名(oldPassword)两种写法提交
    model_config = ConfigDict(populate_by_name=True)

    old_password: str = Field(..., alias="oldPassword", description="旧密码")
    new_password: str = Field(..., min_length=6, alias="newPassword", description="新密码")