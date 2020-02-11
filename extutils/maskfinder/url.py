class URL:
    @staticmethod
    def get_target(zip_code, product_id, range_mi):
        return f"https://api.target.com/fulfillment_aggregator/v1/fiats/{product_id}?" \
               f"key=eb2551e4accc14f38cc42d32fbc2b2ea&nearby={zip_code}" \
               f"&radius={range_mi}&include_only_available_stores=true"

    @staticmethod
    def post_walgreens():
        return "https://www.walgreens.com/locator/v1/search/stores/inventory"
