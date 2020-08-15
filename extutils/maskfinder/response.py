"""
Response wrapper for US mask finder.
"""
from typing import List

import requests

from .url import URL
from .payload import Payload
from .result import MaskFindingResult


class Response:
    """
    Class to get the responses from various mask vendors.
    """

    @staticmethod
    def get_target(zip_code, product_body, range_mi, silent_fail) -> List[MaskFindingResult]:
        """
        Get the inventory status from Target.

        :param zip_code: zip code of the search range
        :param product_body: product info response body
        :param range_mi: max searching range
        :param silent_fail: if the function should silently fail
        :return: list of `MaskFindingResult`
        """
        try:
            ret = []
            product_id, product_name = product_body

            response = requests.get(URL.get_target(zip_code, product_id, range_mi)).json()
            for location in response["products"][0]["locations"]:
                ret.append(MaskFindingResult(
                    name=location["store_name"],
                    product_name=product_name,
                    amount=int(location["location_available_to_promise_quantity"]),
                    distance=float(location["distance"]),
                    address=location["store_address"].replace("\n", "")
                ))

            return ret
        except Exception as ex:
            if silent_fail:
                return []

            raise ex

    @staticmethod
    def get_walgreens(zip_code, product_body, silent_fail) -> List[MaskFindingResult]:
        """
        Get the inventory status from Walgreens.

        :param zip_code: zip code of the search range
        :param product_body: product info response body
        :param silent_fail: if the function should silently fail
        :return: list of `MaskFindingResult`
        """
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

                ret.append(MaskFindingResult(
                    name=f'{store["name"]} #{location["storeNumber"]}',
                    product_name=product_name,
                    amount=int(location["inventory"]["inventoryCount"]),
                    distance=float(location["distance"]),
                    address=f'{address_body["street"]}, {address_body["state"]} {address_body["zip"]}',
                    time=f'{store["storeOpenTime"]}~{store["storeCloseTime"]}'
                ))

            return ret
        except Exception as ex:
            if silent_fail:
                return []

            raise ex
