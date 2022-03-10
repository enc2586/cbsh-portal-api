import flask
import requests as req
import json
from bs4 import BeautifulSoup

app = flask.Flask(__name__)

SIGNIN_URL = "http://academic.petapop.com/sign/actionLogin.do"


def cleanUp(str):
    stringList = str.split()
    result = " ".join(stringList)
    return result


@app.route('/', methods=['GET'])
def root():
    return "Hello, world!"


@app.route('/legacySelfLearn/credentialValidity', methods=['POST'])
def checkIfCredentialValid():
    userData = {
        "id": flask.request.json['id'],
        "password": flask.request.json['password']
    }

    with req.session() as sess:
        res = sess.post(SIGNIN_URL, data=userData)
        rawPage = BeautifulSoup(res.content.decode('utf-8'), "html.parser")

        if cleanUp(rawPage.li.get_text()) == "선생님은 가입해주세요.":
            return False

        else:
            return True
