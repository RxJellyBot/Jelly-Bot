"""
URLs for the US mask finder to get.
"""


class URL:
    """
    API URL of various vendors.
    """

    @staticmethod
    def get_target(zip_code, product_id, range_mi):
        """
        Get the Target inventory API URL which can be used using ``GET``.

        :param zip_code: zip code for the search range
        :param product_id: product ID to search
        :param range_mi: max searching range in miles
        :return: configured Target API URL
        """
        return f"https://api.target.com/fulfillment_aggregator/v1/fiats/{product_id}?" \
               f"key=eb2551e4accc14f38cc42d32fbc2b2ea&nearby={zip_code}" \
               f"&radius={range_mi}&include_only_available_stores=true"

    @staticmethod
    def post_walgreens():
        """
        Get the Walgreens inventory API URL which can be used using ``POST``.

        :return: Walgreens inventory API URL
        """
        return "https://www.walgreens.com/locator/v1/search/stores/inventory"
