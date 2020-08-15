"""
Payload for the service - US mask finder.
"""


class Payload:  # pylint: disable=R0903
    """
    Class to generate the payload to be sent for US mask finder.
    """

    @staticmethod
    def get_walgreens(addr, product_id):
        """
        Get the payload for getting the Walgreens product status.

        :param addr: address of the Walgreens store
        :param product_id: product ID
        :return: payload to be sent to get the Walgreens' product status
        """
        return {
            "zip": addr,
            "requestType": "findAtYourLocal",
            "inStockOnly": "true",
            "p": "1",
            "s": "100",
            "r": "5000",
            "plnId": product_id
        }
