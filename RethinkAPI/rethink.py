import requests
import html_to_json

# Insert URL Here
url = ''


class loginIncorrectErr(Exception):
    def __init__(self):
        super().__init__(
            "Cannot authenticate, the username or password is incorrect.")


class connectionFailed(Exception):
    def __init__(self):
        super().__init__(
            "Cannot connect to the server, are you connected to the internet?")


class sessionAuthError(Exception):
    def __init__(self):
        super().__init__("Session is not authenticated")


def authCheck(auth):
    data = {"what": "redisplayLoginScreen"}
    try:
        r = requests.post(url, data=data, cookies=auth)
    except requests.exceptions.ConnectionError:
        raise connectionFailed()
    substring1 = '<caption><img src="images/school_logo.png?v=2" /></caption>'
    substring2 = '<strong>Sessions Active For   ()</strong></div>'
    if substring1 in r.text or substring2 in r.text:
        return False
    return True


def auth(username, password):
    s = requests.Session()
    data = {
        "what": "login",
        "username": str(username),
        "password": str(password),
    }
    try:
        r = s.post(url, data=data)
    except requests.exceptions.ConnectionError:
        raise connectionFailed()
    substring1 = '<caption><img src="images/school_logo.png?v=2" /></caption>'
    substring2 = '<div class="tblHeader"><strong>Sessions Active For   ()</strong></div>'
    if substring1 in r.text or substring2 in r.text:
        raise loginIncorrectErr()

    return s.cookies.get_dict()


def getInfo(auth):
    try:
        data = {"what": "redisplayLoginScreen", "PHPSESSID": auth["PHPSESSID"]}
    except (KeyError, AttributeError):
        raise sessionAuthError()
    try:
        r = requests.post(url, data=data, cookies=auth)
    except requests.exceptions.ConnectionError:
        raise connectionFailed()
    substring1 = '<caption><img src="images/school_logo.png?v=2" /></caption>'
    substring2 = '<div class="tblHeader"><strong>Sessions Active For   ()</strong></div>'
    if substring1 in r.text or substring2 in r.text:
        raise sessionAuthError()

    resToJSON = html_to_json.convert(r.text)

    mk1 = r.text.find('<div class="tblHeader"><strong>Sessions Active For ')
    mk2 = r.text.find('</strong></div>', mk1)
    username_and_id = r.text[mk1 + 51:mk2]

    mk1 = username_and_id.find('(')
    mk2 = username_and_id.find(')', mk1)
    ID = username_and_id[mk1 + 1:mk2]

    username = username_and_id.replace(ID, "").replace("(",
                                                       "").replace(")", "")
    username = username[0:len(username) - 1]

    if "+" in resToJSON["html"][0]["body"][0]["div"][1]["table"][0]["caption"][
            0]["div"][1]["_value"]:
        week = resToJSON["html"][0]["body"][0]["div"][1]["table"][0][
            "caption"][0]["div"][1]["_value"].split("+")[1].replace(" ", "")
    else:
        week = "0"

    return {"name": str(username), "studentid": str(ID), "week": int(week)}


def addClass(auth, classid):
    try:
        data = {
            "what": "addStudentToSession",
            'sessionId': str(classid),
            "PHPSESSID": str(auth["PHPSESSID"])
        }
    except (KeyError, AttributeError):
        raise sessionAuthError()
    try:
        r = requests.post(url, data=data, cookies=auth)
    except requests.exceptions.ConnectionError:
        raise connectionFailed()
    substring1 = '<caption><img src="images/school_logo.png?v=2" /></caption>'
    substring2 = '<div class="tblHeader"><strong>Sessions Active For   ()</strong></div>'
    if substring1 in r.text or substring2 in r.text:
        raise sessionAuthError()
    return


def removeClass(auth, classid):
    try:
        data = {
            "what": "removeStudentFromSession",
            'sessionId': str(classid),
            "PHPSESSID": str(auth["PHPSESSID"])
        }
    except (KeyError, AttributeError):
        raise sessionAuthError()
    try:
        r = requests.post(url, data=data, cookies=auth)
    except requests.exceptions.ConnectionError:
        raise connectionFailed()
    substring1 = '<caption><img src="images/school_logo.png?v=2" /></caption>'
    substring2 = '<div class="tblHeader"><strong>Sessions Active For   ()</strong></div>'
    if substring1 in r.text or substring2 in r.text:
        raise sessionAuthError()
    return


def getEnrolledClasses(auth):
    try:
        data = {
            "what": "redisplayLoginScreen",
            "PHPSESSID": str(auth["PHPSESSID"])
        }
    except (KeyError, AttributeError):
        raise sessionAuthError()

    try:
        r = requests.post(url, data=data, cookies=auth)
    except requests.exceptions.ConnectionError:
        raise connectionFailed()
    substring1 = '<caption><img src="images/school_logo.png?v=2" /></caption>'
    substring2 = '<div class="tblHeader"><strong>Sessions Active For   ()</strong></div>'
    if substring1 in r.text or substring2 in r.text:
        raise sessionAuthError()
    resToJSON = html_to_json.convert(r.text)

    classElementList = resToJSON["html"][0]["body"][0]["div"][1]["table"][0][
        "tr"]

    classlist = []
    for a in classElementList:
        try:
            classlist.append({
                "type":
                str(a["td"][2]["_value"]),
                "classname":
                str(a["td"][3]["_value"]),
                "date":
                str(a["td"][4]["_value"]),
                "room":
                str(a["td"][5]["_value"]),
                "openseats":
                str(a["td"][6]["_value"]),
                "firstname":
                str(a["td"][7]["_value"]),
                "lastname":
                str(a["td"][8]["_value"]),
                "classid":
                str(a["td"][0]["img"][0]['_attributes']['onclick'].replace(
                    "removeStudentFromSession('", "").replace("')", "")),
            })
        except IndexError:
            pass

    return classlist


def getAllClasses(auth):
    try:
        data = {
            "what": "displaySignupScreen",
            "PHPSESSID": str(auth["PHPSESSID"])
        }
    except (KeyError, AttributeError):
        raise sessionAuthError()

    try:
        r = requests.post(url, data=data, cookies=auth)
    except requests.exceptions.ConnectionError:
        raise connectionFailed()
    substring1 = '<caption><img src="images/school_logo.png?v=2" /></caption>'
    substring2 = '<div class="tblHeader"><strong>Sessions Active For   ()</strong></div>'
    if substring1 in r.text or substring2 in r.text:
        raise sessionAuthError()
    resToJSON = html_to_json.convert(r.text)

    classElementList = resToJSON["html"][0]["body"][0]["div"][2]["div"][0][
        "div"][0]["table"][0]["tr"]

    classlist = []
    for a in classElementList:
        if not 'colspan' in a["td"][0]['_attributes']:
            classlist.append({
                "type":
                str(a["td"][2]["_value"]),
                "classname":
                str(a["td"][3]["_value"]),
                "date":
                str(a["td"][4]["_value"]),
                "openseats":
                str(a["td"][5]["_value"]),
                "room":
                str(a["td"][1]["img"][0]['_attributes']["classroom"]),
                "firstname":
                str(a["td"][6]["_value"]),
                "lastname":
                str(a["td"][7]["_value"]),
                "classid":
                str(a["td"][0]["img"][0]['_attributes']['onclick'].replace(
                    "addStudentToSession('", "").split("'")[0]),
            })

    return classlist


def shiftWeekUp(auth):
    try:
        data = {
            "what": "incrementWeekOffset",
            "PHPSESSID": str(auth["PHPSESSID"])
        }
    except (KeyError, AttributeError):
        raise sessionAuthError()
    try:
        r = requests.post(url, data=data, cookies=auth)
    except requests.exceptions.ConnectionError:
        raise connectionFailed()
    substring1 = '<caption><img src="images/school_logo.png?v=2" /></caption>'
    substring2 = '<div class="tblHeader"><strong>Sessions Active For   ()</strong></div>'
    if substring1 in r.text or substring2 in r.text:
        raise sessionAuthError()


def shiftWeekDown(auth):
    try:
        data = {
            "what": "decrementWeekOffset",
            "PHPSESSID": str(auth["PHPSESSID"])
        }
    except (KeyError, AttributeError):
        raise sessionAuthError()
    try:
        r = requests.post(url, data=data, cookies=auth)
    except requests.exceptions.ConnectionError:
        raise connectionFailed()
    substring1 = '<caption><img src="images/school_logo.png?v=2" /></caption>'
    substring2 = '<div class="tblHeader"><strong>Sessions Active For   ()</strong></div>'
    if substring1 in r.text or substring2 in r.text:
        raise sessionAuthError()  
