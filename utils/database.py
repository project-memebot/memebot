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

    async def favorite_meme(user_id: int, favorite_meme: str):
        """
        user_id (int): 필수, 디스코드 유저 ID 입력
        favorite_meme (str): 필수, 짤 ID 입력
        """
        user_data = await USER_DATABASE.user_find(user_id)
        lists = [i['meme_id'] for i in user_data['favorite']]
        if user_data:
            if favorite_meme in lists:
                user_data['favorite'] = []
                for i in user_data['favorite']:
                    if favorite_meme != i['meme_id']:
                        user_data['favorite'].append(i)
                await database.user.update_one({"_id": user_id}, {"$set": user_data})
                result = await MEME_DATABASE.find_meme(favorite_meme)
                result['star'] -= 1
                await database.meme.update_one({"_id": favorite_meme}, {"$set": result})
                return {"code": 200, "message": "정상적으로 즐겨찾기가 제거되었습니다."}
            else:
                json = {"meme_id": favorite_meme, "added_at": datetime.datetime.now()}
                user_data["favorite"].insert(0, json)
                await database.user.update_one({"_id": user_id}, {"$set": user_data})
                result = await MEME_DATABASE.find_meme(favorite_meme)
                print(result)
                result['star'] += 1
                await database.meme.update_one({"_id": favorite_meme}, {"$set": result})
                return {"code": 200, "message": "정상적으로 즐겨찾기에 추가되었습니다."}
        else:
            return {"code": 403, "message": "가입을 진행하지 않았습니다. ``/가입`` 명령어로 가입이 필요합니다."}

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

    async def find_meme(query):
        result = database.meme.find({"_id": {"$regex": query}})
        search_result = [i async for i in result]
        return search_result[0]
"""
string_pool = string.ascii_letters + string.digits
                    randomcode = ""
                    for i in range(leng):
                        randomcode += random.choice(string_pool)
"""
