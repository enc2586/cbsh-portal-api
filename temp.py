from datetime import datetime
import pytz
import requests as req
from bs4 import BeautifulSoup
import json

SIGNIN_URL = "http://academic.petapop.com/sign/actionLogin.do"
APPLY_URL = "http://academic.petapop.com/self/requestSelfLrn.do"
CANCEL_URL = "http://academic.petapop.com/self/deleteSelfLrn.do"


KST = pytz.timezone('Asia/Seoul')


def kstNow():
    return datetime.utcnow().astimezone(KST)


def cleanUp(str):
    stringList = str.split()
    result = " ".join(stringList)
    return result


def checkIfCredentialValid(id, password):
    with req.session() as sess:
        res = sess.post(SIGNIN_URL, data=userData)
        # response = json.loads(res.content.decode('utf-8'))
        rawPage = BeautifulSoup(res.content.decode('utf-8'), "html.parser")

        if cleanUp(rawPage.li.get_text()) == "선생님은 가입해주세요.":
            return False

        else:
            return True


def applySelfLearn(body):

    userData = {
        "id": body['id'],
        "password": body['password']
    }

    applyData = {
        'roomTcherId': body['homeRoomTeacherCode'],
        'cchTcherId': body['conductingTeacherCode'],
        'clssrmId': body['classroomCode'],
        'actCode': body['actCode'],
        'actCn': body['actContent'],
        'sgnId': kstNow().strftime(r"%Y%m%d")
    }

    print("logging in")

    with req.session() as sess:
        res = sess.post(SIGNIN_URL, data=userData)
        rawPage = BeautifulSoup(res.content.decode('utf-8'), "html.parser")

        if cleanUp(rawPage.li.get_text()) == "선생님은 가입해주세요.":
            return "Failed to log in", 400

        else:
            print("logged in")
            result = []

            for period in body['periods']:
                print(f"applying for {period}")
                applyCaseData = applyData.copy()
                applyCaseData['lrnPd'] = period

                res = sess.post(APPLY_URL, data=applyCaseData)
                response = json.loads(res.content.decode('utf-8'))

                if response['result']['success'] == True:
                    result.append(response['slrnNo'])

                else:
                    result.append(-1)

            return result


userData = {
    "id": "enc2586",
    "password": "rhkgkrrh1!"
}


applyBody = {
    "id": "enc2586",
    "password": "rhkgkrrh1!",
    "homeRoomTeacherCode": "USRCNFRM_00000000441",
    "conductingTeacherCode": "USRCNFRM_00000000441",
    "classroomCode": "CLSSRM_0000000000063",
    "actCode": "ACT999",
    "actContent": "자습",
    "periods": [1, 2]
}

# print(checkIfCredentialValid(**userData)) #아이디 비번 유효 확인
print(applySelfLearn(applyBody))
