from datetime import datetime
import time
import whois
from pyspark.sql.functions import udf,lit

def extractElem(var,pos="Last",shouldBe=""):
    index = 0

    if shouldBe == "datetime":
        if not isinstance(var, datetime):
            return datetime.min
        return var

    if isinstance(var,list):
        if pos == "Last":
            index = len(var)-1
        else:
            index = pos
        return var[index]
    return var

url_prove = ["https://www.aranzulla.it","https://www.kmu.gov.ua/en","https://it.wikipedia.org/wiki/Dragon_Ball_Z","https://it.wikipedia.org/wiki/Che_Guevara","https://it.wikipedia.org/wiki/Coordinate_geografiche","https://it.wikipedia.org/wiki/Vladimir_Putin","https://stackoverflow.com/questions/32331848/create-a-custom-transformer-in-pyspark-ml","https://sparkbyexamples.com/pyspark/pyspark-cast-column-type","https://it.quora.com/partners"]

class whoIsManager:


    def __init__(self):
        self.cache = {}
        
        self.udf_domain_name = lambda x: extractElem(self.lookFor(x,"domain_name"),pos="Last")
        self.udf_whois_server = lambda x:self.lookFor(x,"whois_server")
        self.udf_registrar = lambda x:self.lookFor(x,"registrar")
        self.udf_org = lambda x:self.lookFor(x,"org")
        self.udf_referral_url = lambda x:self.lookFor(x,"referral_url")
        self.udf_state = lambda x:self.lookFor(x,"state")

        self.udf_city = lambda x:self.lookFor(x,"city")
        self.udf_country = lambda x:self.lookFor(x,"country")
        
        self.udf_address = lambda x: extractElem(self.lookFor(x,"address"))

        self.udf_creation_date = lambda x:extractElem(self.lookFor(x,"creation_date"),shouldBe="datetime")
        self.udf_updated_date = lambda x: extractElem(self.lookFor(x,"updated_date"),shouldBe="datetime")
        self.udf_expiration_date = lambda x: extractElem(self.lookFor(x,"expiration_date"),shouldBe="datetime")
        


    def request(self,URL):
        try:
            response = {}
            time.sleep(0.01)
            response = whois.whois(URL)
            self.cache[URL] = response
            return True
        except Exception as e: 
            print(f"(WhoIsManager request): {e}")
            return False

    def lookFor(self, URL, field=""):
        #effettua la richiesta se non è già in cache
        if URL not in self.cache:
            if not self.request(URL): return None
        
        if field=="":
            return self.cache[URL]

        #controlla se il field richiesto è presente
        if field in self.cache[URL]:
            return self.cache[URL][field]
        return None


def main():
    whoIs = whoIsManager()
    for url in url_prove:
        print(whoIs.udf_domain_name(url))
        print(type(whoIs.udf_domain_name(url)))
        print(whoIs.udf_creation_date(url))
        print(type(whoIs.udf_creation_date(url)))
        print("-"*30)
    # print(whoIs.lookFor("https://github.com","domain_name"))
    # print(whoIs.lookFor("https://wikipedia.com","domain_name"))
    # print(whoIs.lookFor("https://lynn-kwong.medium.com/","domain_name"))
if __name__ == '__main__':
    main()