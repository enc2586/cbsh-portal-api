import flask
from flask_cors import CORS
from datetime import datetime
import pytz
import requests as req
import json
from bs4 import BeautifulSoup

SIGNIN_URL = "http://academic.petapop.com/sign/actionLogin.do"
APPLY_URL = "http://academic.petapop.com/self/requestSelfLrn.do"
DELETE_URL = "http://academic.petapop.com/self/deleteSelfLrn.do"
TCRINFO_URL = "http://academic.petapop.com/self/writeSelfLrnReqst.do"
ROOMINFO_URL = "http://academic.petapop.com/clssrm/buldDrw.do"
SEATINFO_URL = "http://academic.petapop.com/clssrm/seatInfo.json"
LRNSTAT_URL = "http://academic.petapop.com/self/mainSelfLrnReqst.do"

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
    return json.dumps(True)


@app.route('/legacySelfLearn/credentialValidity', methods=['POST'])
def checkCredentialValidity():
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


@app.route('/legacySelfLearn/selfLearn', methods=['PUT', 'DELETE'])
def applySelfLearn():
    body = flask.request.json

    if flask.request.method == 'PUT':
        if not all(item in body.keys() for item in ["id", "password", "homeRoomTeacherCode", "conductingTeacherCode", "classroomCode", "periods"]):
            return flask.make_response("Invalid request body.", 400)

        userData = {
            "id": body['id'],
            "password": body['password']
        }

        applyData = {
            'roomTcherId': body['homeRoomTeacherCode'],
            'cchTcherId': body['conductingTeacherCode'],
            'clssrmId': body['classroomCode'],
            'actCode': body['actCode'] if 'actCode' in body else "ACT999",
            'actCn': body['actContent'] if 'actCn' in body else ".",
            'sgnId': body['date'] if 'date' in body else kstNow().strftime(r"%Y%m%d")
        }

        with req.session() as sess:
            for period in body['periods']:
                if type(period) != int:
                    return flask.make_response("Period data includes non-int values.", 400)

            res = sess.post(SIGNIN_URL, data=userData)
            rawPage = BeautifulSoup(res.content.decode('utf-8'), "html.parser")

            if cleanUp(rawPage.li.get_text()) == "선생님은 가입해주세요.":
                return flask.make_response("Invalid credentials", 400)

            else:
                result = {}

                for period in body['periods']:
                    applyCaseData = applyData.copy()
                    applyCaseData['lrnPd'] = period

                    res = sess.post(APPLY_URL, data=applyCaseData)
                    response = json.loads(res.content.decode('utf-8'))

                    if response['result']['success'] == True:
                        result[period] = response['slrnNo']

                    else:
                        result[period] = False

                return json.dumps(result)

    elif flask.request.method == 'DELETE':
        if not all(item in body.keys() for item in ["id", "password", "target"]):
            return flask.make_response("Invalid request body.", 400)

        userData = {
            "id": body['id'],
            "password": body['password']
        }

        with req.session() as sess:
            for serial in body['target']:
                if type(serial) != int:
                    return flask.make_response("Target data includes non-int values.", 400)

            res = sess.post(SIGNIN_URL, data=userData)
            rawPage = BeautifulSoup(res.content.decode('utf-8'), "html.parser")

            if cleanUp(rawPage.li.get_text()) == "선생님은 가입해주세요.":
                return flask.make_response("Invalid Credentials", 400)

            else:
                result = {}
                for serial in body['target']:
                    deleteData = {
                        "slrnNo": serial
                    }
                    res = sess.post(DELETE_URL, data=deleteData)
                    response = json.loads(res.content.decode('utf-8'))

                    if response['result']['success'] == True:
                        result[serial] = True

                    else:
                        result[serial] = False

                return json.dumps(result)


@app.route('/legacySelfLearn/teacherCodes', methods=['POST'])
def getTeacherCodes():
    body = flask.request.json

    if not all(item in body.keys() for item in ["id", "password"]):
        return flask.make_response("Invalid request body.", 400)

    userData = {
        "id": body['id'],
        "password": body['password'],
    }

    with req.session() as sess:
        res = sess.post(SIGNIN_URL, data=userData)
        rawPage = BeautifulSoup(res.content.decode('utf-8'), "html.parser")

        if cleanUp(rawPage.li.get_text()) == "선생님은 가입해주세요.":
            return flask.make_response("Invalid credentials", 400)

        else:
            res = sess.get(TCRINFO_URL)
            pageData = BeautifulSoup(
                res.content.decode('utf-8'), "html.parser")

            teacherData = {}
            for element in pageData.find_all('option'):
                if element['value']:
                    teacherData[element.get_text()] = element['value']

            if not teacherData:
                return json.dumps(False)

            teacherData['지도교사없음'] = ''
            return json.dumps(teacherData)


@app.route('/legacySelfLearn/classDatas', methods=['POST'])
def getClassDatas():
    body = flask.request.json

    if not all(item in body.keys() for item in ["id", "password"]):
        return flask.make_response("Invalid request body.", 400)

    userData = {
        "id": body['id'],
        "password": body['password'],
    }

    with req.session() as sess:
        res = sess.post(SIGNIN_URL, data=userData)
        rawPage = BeautifulSoup(res.content.decode('utf-8'), "html.parser")

        if cleanUp(rawPage.li.get_text()) == "선생님은 가입해주세요.":
            return flask.make_response("Invalid credentials", 400)

        else:
            res = sess.get(ROOMINFO_URL)
            response = BeautifulSoup(
                res.content.decode('utf-8'), "html.parser")

            rawClassList = response.select(
                'div > div > div > div.data-list.custom-list > table > tbody > tr')

            classData = {}
            for rawClassHTML in rawClassList:
                rawClassData = rawClassHTML.select('td')
                name = rawClassData[1].get_text()
                if not ('삭제' in name):
                    classData[name] = {
                        "floor": rawClassData[0].get_text(),
                        "maxppl": cleanUp(rawClassData[3].get_text()),
                        "tcher": rawClassData[2].get_text(),
                        "id": rawClassData[4].select_one('div > input')['value'],
                    }

            if not classData:
                return json.dumps(False)

            return json.dumps(classData)
