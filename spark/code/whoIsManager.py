import json
import time
from datetime import datetime

import whois


class WhoIsManager:
    relevant_fields = [
        "domain_name",
        "whois_server",
        "registrar",
        "org",
        "referral_url",
        "state",
        "city",
        "country",
        "creation_date",
        "updated_date",
        "expiration_date",
    ]

    def __init__(self):
        self.cache = {}

    def extract_elem(self, var, pos="Last", should_be=""):
        if should_be == "datetime":
            if not isinstance(var, datetime):
                return datetime.min
            return var

        if isinstance(var, list):
            if pos == "Last":
                index = len(var) - 1
            else:
                index = pos
            return var[index]

        return var

    def request(self, url):
        if url in self.cache:
            return True

        try:
            time.sleep(0.01)
            response = whois.whois(url)
            self.cache[url] = response
            return True
        except Exception as e:
            print(f"(WhoIsManager request): {e}")
            return False

    def look_for(self, url, field=""):
        if not self.request(url):
            return None

        if field == "":
            return self.cache[url]

        if field in self.cache[url]:
            return self.cache[url][field]

        return None

    def get_relevant_fields(self, url):
        data = {}
        for field in WhoIsManager.relevant_fields:
            try:
                value = self.extract_elem(self.look_for(url, field))
                if isinstance(value, datetime):
                    value = value.isoformat()
                data[field] = str(value)
            except Exception:
                data[field] = "aa"
        return json.dumps(data, indent=4)


def main():
    urls = [
        "https://www.aranzulla.it",
        "https://www.kmu.gov.ua/en",
        "https://it.wikipedia.org/wiki/Dragon_Ball_Z",
        "https://it.wikipedia.org/wiki/Che_Guevara",
        "https://it.wikipedia.org/wiki/Coordinate_geografiche",
        "https://it.wikipedia.org/wiki/Vladimir_Putin",
        "https://stackoverflow.com/questions/32331848/create-a-custom-transformer-in-pyspark-ml",
        "https://sparkbyexamples.com/pyspark/pyspark-cast-column-type",
        "https://it.quora.com/partners",
    ]

    whois_manager = WhoIsManager()
    for url in urls:
        print(whois_manager.get_relevant_fields(url))
        print("-" * 30)


if __name__ == "__main__":
    main()
