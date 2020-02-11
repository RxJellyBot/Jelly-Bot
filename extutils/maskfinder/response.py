import requests

from .url import URL
from .payload import Payload
from .result import Result


class Response:
    @staticmethod
    def get_target(zip_code, product_body, range_mi, silent_fail):
        try:
            ret = []
            product_id, product_name = product_body

            response = requests.get(URL.get_target(zip_code, product_id, range_mi)).json()
            for location in response["products"][0]["locations"]:
                ret.append(Result(
                    name=location["store_name"],
                    product_name=product_name,
                    amount=int(location["location_available_to_promise_quantity"]),
                    distance=float(location["distance"]),
                    address=location["store_address"].replace("\n", "")
                ))

            return ret
        except Exception as e:
            if silent_fail:
                return []
            else:
                raise e

    @staticmethod
    def get_walgreens(zip_code, product_body, silent_fail):
        try:
            ret = []
            product_id, product_name = product_body

            response = requests.post(
                URL.post_walgreens(),
                data=Payload.get_walgreens(zip_code, product_id)).json()
            print(response["summary"])
            for location in response["results"]:
                store = location["store"]
                address_body = store["address"]

                ret.append(Result(
                    name=f'{store["name"]} #{location["storeNumber"]}',
                    product_name=product_name,
                    amount=int(location["inventory"]["inventoryCount"]),
                    distance=float(location["distance"]),
                    address=f'{address_body["street"]}, {address_body["state"]} {address_body["zip"]}',
                    time=f'{store["storeOpenTime"]}~{store["storeCloseTime"]}'
                ))

            return ret
        except Exception as e:
            if silent_fail:
                return []
            else:
                raise e
