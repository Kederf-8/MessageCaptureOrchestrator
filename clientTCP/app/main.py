import os
import sys

from tgScraper import tgScraper
from translator import translator
from util_funcs import strOrNone, toBool

if __name__ == "__main__":
    # Il canale viene passato come parametro all'esecuzione di main.py
    channel = "https://t.me/" + sys.argv[1]

    # I restanti parametri vengono passati come varabiali d'ambiente
    last_id = int(os.environ["ENV_LAST_ID"])
    overwrite_last_id = toBool(os.environ["ENV_OVERWRITE_LAST_ID"])
    method = os.environ["ENV_METHOD"]
    batch = toBool(os.environ["ENV_BATCH"])
    toFile = strOrNone(os.environ["ENV_TO_FILE"])
    stdout = toBool(os.environ["ENV_STDOUT"])
    sendTCP = toBool(os.environ["ENV_SENDTCP"])
    translation = toBool(os.environ["ENV_TRANSLATION"])
    query = strOrNone(os.environ["ENV_QUERY"])
    translateFROM = os.environ["ENV_TRANSLATE_FROM"].split()
    translateTO = os.environ["ENV_TRANSLATE_TO"]
    delay = int(os.environ["ENV_DELAY"])

    if toFile is not None:
        toFile = f"{toFile}.json"

    # effettua una traduzione
    tr = None
    if translation is True:
        tr = translator(file="translators.txt", FROM=translateFROM, TO=translateTO)

    fetcher = tgScraper(channel, "logstash", 10155, tr)

    if method.lower() == "all":
        fetcher.getAllMessages(
            min_id=last_id,
            max_id=None,
            query=query,
            sendTCP=sendTCP,
            toFile=toFile,
            stdout=stdout,
            batch=batch,
            sleepTime=delay,
        )
    elif method.lower() == "new":
        fetcher.getLastMessages(
            toFile=toFile, stdout=stdout, sendTCP=sendTCP, batch=batch, sleepTime=delay
        )
    else:
        print(f"method: {method} isn't correct")
