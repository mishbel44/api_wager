
from flask import Flask, jsonify
import json
import requests

app = Flask(__name__)

# URL внешнего API, к которому мы будем обращаться
backOffice_bets_api = "https://backoffice.pbsvc.bz/api/backoffice/client/information" # url API-шки бэкофиса откуда берем ставки


@app.route('/get_WageringSum/<int:client_id>', methods=['GET']) #Наша API для получения Суммы отгрыша бонуса (или чего там)
def get_data(client_id):
    try:
        # GET запрос к внешнему API
        url = "https://backoffice.pbsvc.bz/api/paygate/client/lastTransactions"
        params = {
            "fsid": "l1I9wLGY9Sfzj7x5bhpZCwY3",
            "userId": "5611",
            "userLang": "ru",
            "clientId": client_id,
            "maxCount": 200,
            "login": "nimakarov"
        }

        response = requests.post(url=url, json=params)

        # Чекаем распонс-код
        if response.status_code == 200:
            data = response.json()

            max_lastupdated = 0
            withdrawal_element = None

            for element in data["response"]:
                if element["type"] == "withdrawal" and element["status"] != "SUCCESS" and int(
                        element["lastUpdated"]) > max_lastupdated:
                    max_lastupdated = int(element["lastUpdated"])
                    withdrawal_element = element

            if withdrawal_element is not None:
                withdrawal_id = withdrawal_element["id"]
                # print(withdrawal_id)
                url = "https://backoffice.pbsvc.bz/api/payoutrisk/getPayoutHistory"
                params = {
                    "clientId": client_id,
                    "globalId": f"{withdrawal_id}",
                    "login": "usrPariBackofficeApi",
                    "fsid": "l1I9wLGY9Sfzj7x5bhpZCwY3",
                    "userId": "5611",
                    "userLang": "ru"
                }
                response = requests.post(url=url, json=params)
                data = response.json()
                if data["response"]["list"]:
                    ovv_found = False
                    af_found = False
                    for item in data["response"]["list"]:
                        if "#ОВВ" in item["object"]["userComment"]:
                            ovv_found = True
                        if "#АФ" in item["object"]["userComment"]:
                            af_found = True
                    if ovv_found:
                        result_item = "Требуется ОВВ"
                    elif af_found:
                        result_item = "В обработке АФ"
                    else:
                        result_item = "Недостаточно информации"
                else:
                    result_item = "Верификация не требуется"

            else:
                result_item = "Операция завершена/Недостаточно информации"

            print(result_item)



            result = {'Verification status':f'{result_item}'}
            return jsonify(result)
        else:
            #Или возвращаем сообщение об ошибке
            return jsonify({'error': 'Не удалось сфетчить с апишки данные'}), 500
    except Exception as e:
        # Возвр саму ошибку
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
