import datetime
import random
import string

import motor.motor_asyncio

import config

database = motor.motor_asyncio.AsyncIOMotorClient(config.DATABASE.URI).memebot


class USER_DATABASE:
    async def find(user_id: int):
        """
        user_id (int): 필수, 디스코드 유저 ID 입력
        """
        return await database.user.find_one({"_id": user_id})

    async def insert(user_id: int):
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
        user_data = await USER_DATABASE.find(user_id)
        if user_data:
            lists = [i["meme_id"] for i in user_data["favorite"]]
            if favorite_meme in lists:
                user_data["favorite"] = []
                for i in user_data["favorite"]:
                    if favorite_meme != i["meme_id"]:
                        user_data["favorite"].append(i)
                await database.user.update_one({"_id": user_id}, {"$set": user_data})
                result = await MEME_DATABASE.find(favorite_meme)
                result["star"] -= 1
                await database.meme.update_one({"_id": favorite_meme}, {"$set": result})
                return {"code": 200, "message": "정상적으로 즐겨찾기가 제거되었습니다."}
            else:
                json = {"meme_id": favorite_meme, "added_at": datetime.datetime.now()}
                user_data["favorite"].insert(0, json)
                await database.user.update_one({"_id": user_id}, {"$set": user_data})
                result = await MEME_DATABASE.find(favorite_meme)
                result["star"] += 1
                await database.meme.update_one({"_id": favorite_meme}, {"$set": result})
                return {"code": 200, "message": "정상적으로 즐겨찾기에 추가되었습니다."}
        else:
            return {"code": 403, "message": "가입을 진행하지 않았습니다. ``/가입`` 명령어로 가입이 필요합니다."}

    async def favorite_meme_list(user_id: int):
        """
        user_id (int): 필수, 디스코드 유저 ID 입력
        """
        user_data = await USER_DATABASE.find(user_id)
        if user_data:
            lists = [i["meme_id"] for i in user_data["favorite"]]
            return {
                "code": 200,
                "favorite_list": lists,
                "message": "정상적으로 즐겨찾기 목록을 조회하였습니다.",
            }
        else:
            return {"code": 403, "message": "가입을 진행하지 않았습니다. ``/가입`` 명령어로 가입이 필요합니다."}

    async def delete(user_id: int):
        """
        user_id (int): 필수, 디스코드 유저 ID 입력
        """
        await database.user.delete_one({"_id": user_id})

    async def ulist(filter: dict = None):
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
    async def search(user_id: int):
        """
        user_id (int): 필수, 디스코드 유저 ID 입력
        """
        return await database.blacklist.find_one({"user_id": user_id, "deleted": False})

    async def blist(filter: dict = {}):
        """
        filiter (dict): 선택, 검색할 필터를 입력해주세요.
        """
        black_list = []
        async for i in database.blacklist.find(filter):
            black_list.append(i)
        return black_list

    async def add(
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
                "user_id": user_id,
                "reason": reason,
                "started_at": datetime.datetime.now(),
                "ended_at": ended_at,
                "moderator": mod_id,
                "deleted": False,
            }
        )

    async def delete(
        user_id: int,
        reason: str,
        mod_id: int,
    ):
        """
        user_id (int): 필수, 제재를 해제할 디스코드 유저 ID 입력
        reason (str): 필수, 제재 해제 사유 입력
        mod_id (int): 필수, 제재를 해제 관리자 ID 입력 (자동 해제일 경우, 짤방러 봇 ID 입력)
        """
        return await database.blacklist.update_one(
            {"user_id": user_id, "deleted": False},
            {
                "$set": {
                    "deleted": True,
                    "deleted_reason": reason,
                    "deleted_at": datetime.datetime.now(),
                    "deleted_moderator": mod_id,
                }
            },
        )


class MEME_DATABASE:
    async def mlist(filter: dict = {}):
        """
        filter (dict): 선택, DICT 형식으로 입력
        """
        meme_list = []
        async for i in database.meme.find(filter):
            meme_list.append(i)
        return meme_list

    async def insert(title: str, url: str, uploader_id: int):
        """
        title (str): 필수, 짤 제목 입력
        url (str): 필수, 짤 사진 url 입력
        uploader_id (int): 필수, 짤 업로더 ID 입력
        """
        while True:
            string_pool = string.ascii_letters + string.digits
            randomcode = ""

            for sul in range(8):
                randomcode += random.choice(string_pool)

            if (await MEME_DATABASE.find(randomcode)) == None:
                break

        return await database.meme.insert_one(
            {
                "_id": randomcode,
                "uploader_id": uploader_id,
                "title": title,
                "url": url,
                "upload_at": datetime.datetime.now(),
                "star": 0,
            }
        )

    async def random():
        result = await MEME_DATABASE.mlist()
        return random.choice(result)

    async def find(query):
        result = database.meme.find({"_id": {"$regex": query}})
        try:
            search_result = [i async for i in result]
            return search_result[0]
        except IndexError:
            return None

    async def search(query):
        result = database.meme.find({"title": {"$regex": query}})
        try:
            search_result = [i async for i in result]
            return search_result
        except IndexError:
            return []
