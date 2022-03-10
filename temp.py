from distutils.command.clean import clean
import requests as req
from bs4 import BeautifulSoup
import json

SIGNIN_URL = "http://academic.petapop.com/sign/actionLogin.do"


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


userData = {
    "id": "enc2586",
    "password": "rhkgkrrh1!"
}

# print(checkIfCredentialValid(**userData)) #아이디 비번 유효 확인
