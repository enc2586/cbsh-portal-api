import flask
from flask_cors import CORS
from datetime import datetime
import pytz
import requests as req
import json
from bs4 import BeautifulSoup

SIGNIN_URL = "http://academic.petapop.com/sign/actionLogin.do"
APPLY_URL = "http://academic.petapop.com/self/requestSelfLrn.do"

KST = pytz.timezone('Asia/Seoul')


def kstNow():
    return datetime.utcnow().astimezone(KST)


def cleanUp(str):
    stringList = str.split()
    result = " ".join(stringList)
    return result


app = flask.Flask(__name__)
CORS(app)


@app.route('/', methods=['GET'])
def root():
    return "Hello, world!"


@app.route('/legacySelfLearn/credentialValidity', methods=['POST'])
def applySelfLearn():
    body = flask.request.json

    userData = {
        "id": body['id'],
        "password": body['password']
    }

    with req.session() as sess:
        res = sess.post(SIGNIN_URL, data=userData)
        rawPage = BeautifulSoup(res.content.decode('utf-8'), "html.parser")

        if cleanUp(rawPage.li.get_text()) == "선생님은 가입해주세요.":
            return json.dumps(False)

        else:
            return json.dumps(True)


@app.route('/legacySelfLearn/selfLearn', methods=['PUT'])
def applySelfLearn():
    body = flask.request.json

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

    with req.session() as sess:
        res = sess.post(SIGNIN_URL, data=userData)
        rawPage = BeautifulSoup(res.content.decode('utf-8'), "html.parser")

        if cleanUp(rawPage.li.get_text()) == "선생님은 가입해주세요.":
            return "Failed to log in", 400

        else:
            result = []

            for period in body['periods']:
                applyCaseData = applyData.copy()
                applyCaseData['lrnPd'] = period

                res = sess.post(APPLY_URL, data=applyCaseData)
                response = json.loads(res.content.decode('utf-8'))

                if response['result']['success'] == True:
                    result.append(response['slrnNo'])

                else:
                    result.append(-1)

            return result
