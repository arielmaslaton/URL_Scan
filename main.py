# This is a sample Python script.
import requests
import json
import unidecode
from urllib.request import urlopen
import time

key = 'e259b23c-450e-47f2-9bb1-1458be3fa473'
urlToScan = 'https://www.walla.co.il'
def waitForResourceAvailable(urlReq, response, timeout, timewait):
    timer = 0
    while response.status_code != 200:
        print ('.')
        time.sleep(timewait)
        timer += timewait
        if timer > timeout:
            return response
        if response.status_code == 200:
            return response
        else:
            response = requests.get(urlReq)

    return response

def getQueryResponse(url):
    print(f'Send query of, {url}')
    headers = {'API-Key': key, 'Content-Type': 'application/json'}
    data = {"url": url, "visibility": "public"}
    response = requests.post('https://urlscan.io/api/v1/scan/', headers=headers, data=json.dumps(data))
    return waitForResourceAvailable(url, response, 30, 1)


def sendQuery(url):
    queryResponse = getQueryResponse(url)
    if queryResponse.status_code != 200:
        print('error code: %s' % url.status_code)
        return

    apiUrl = json.loads(queryResponse.text)['api']
    apiUrlResponseRetry = waitForResourceAvailable(apiUrl, requests.get(apiUrl), 30, 1)
    if apiUrlResponseRetry.status_code != 200:
        print('error code: %s' % apiUrlResponseRetry.status_code)
        return

    jsonReponse = json.loads(apiUrlResponseRetry.text)
    verdict = jsonReponse['verdicts']['overall']['malicious']
    print('verdict for url:', url + ' is:', verdict)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    sendQuery(urlToScan)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
