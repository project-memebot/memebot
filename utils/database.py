import config
import datetime
import random
import motor.motor_asyncio

database = motor.motor_asyncio.AsyncIOMotorClient(config.DATABASE.URI).memebot


class USER_DATABASE:
    async def user_find(user_id: int):
        """
        user_id (int): 필수, 디스코드 유저 ID 입력
        """
        return await database.user.find_one({"_id": user_id})

    async def user_insert(user_id: int):
        """
        user_id (int): 필수, 디스코드 유저 ID 입력
        """
        return await database.user.insert_one(
            {"_id": user_id, "created_at": datetime.datetime.now(), "favorite": []}
        )

    async def user_add_favorite(user_id: int, favorite_meme: str):
        """
        user_id (int): 필수, 디스코드 유저 ID 입력
        favorite_meme (str): 필수, 짤 ID 입력
        """
        json = {"meme_id": favorite_meme, "added_at": datetime.datetime.now()}
        user = await user_find(user_id)
        user["favorite"].insert(0, json)
        return await database.user.update_one({"_id": user_id}, {"$set": user})

    async def user_delete(user_id: int):
        """
        user_id (int): 필수, 디스코드 유저 ID 입력
        """
        await database.user.delete_one({"_id": user_id})

    async def user_list(filter: dict = None):
        """
        filter (dict): 선택, DICT 형식으로 입력
        """
        user_list = []
        if filter:
            async for i in database.user.find(filter):
                user_list.append(i)
        else:
            async for i in database.user.find({}):
                user_list.append(i)
        return user_list


class BLACKLIST:
    async def search_blacklist(user_id: int):
        """
        user_id (int): 필수, 디스코드 유저 ID 입력
        """
        return await database.blacklist.find_one({"_id": user_id})

    async def add_blacklist(
        user_id: int, reason: str, mod_id: int, ended_at: datetime.datetime = None
    ):
        """
        user_id (int): 필수, 제재할 디스코드 유저 ID 입력
        reason (str): 필수, 제재 사유 입력
        mod_id (int): 필수, 제재한 관리자 ID 입력
        ended_at (datetime.datetime): 선택, 제재 종료 시간 입력
        """
        return await database.blacklist.insert_one(
            {
                "_id": user_id,
                "reason": reason,
                "started_at": datetime.datetime.now(),
                "ended_at": ended_at,
                "moderator": mod_id,
            }
        )


class MEME_DATABASE:
    async def meme_list(filter: dict = None):
        """
        filter (dict): 선택, DICT 형식으로 입력
        """
        meme_list = []
        if filter:
            async for i in database.meme.find(filter):
                meme_list.append(i)
        else:
            async for i in database.meme.find({}):
                meme_list.append(i)
        return meme_list

    async def random_meme():
        result = await MEME_DATABASE.meme_list()
        return random.choice(result)
"""
string_pool = string.ascii_letters + string.digits
                    randomcode = ""
                    for i in range(leng):
                        randomcode += random.choice(string_pool)
"""
