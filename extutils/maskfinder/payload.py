class Payload:
    @staticmethod
    def get_walgreens(addr, product_id):
        return {
            "zip": addr,
            "requestType": "findAtYourLocal",
            "inStockOnly": "true",
            "p": "1",
            "s": "100",
            "r": "5000",
            "plnId": product_id
        }
