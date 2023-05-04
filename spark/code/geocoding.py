import json
import re

import pandas as pd
import requests


def fetch_dataset():
    url = "https://parseapi.back4app.com/classes/City?limit=1512&keys=name,population,location,cityId"
    headers = {
        "X-Parse-Application-Id": "WHhatLdoYsIJrRzvkD0Y93uKHTX49V9gmHgp8Rw3",
        "X-Parse-Master-Key": "iyzSAHUmPKUzceWRIIitUD1OKAGHvVUzEYb5DCpj",
    }
    dict_data = json.loads(requests.get(url, headers=headers).content.decode("utf-8"))
    df = pd.DataFrame(dict_data["results"])
    print(f"COUNT: {df.count()}")
    print(f"COLUMNS: {df.columns}")
    print(df.head())
    df.to_csv("ukraine_cities.csv", encoding="utf-8")


def modify_dataset():
    pattern = r"[0-9.]+"
    df = pd.read_csv("ukraine_cities.csv", engine="python")
    df["name"] = df["name"].str.lower()
    df["latitude"] = df["location"].apply(lambda x: re.findall(pattern, x)[0])
    df["longitude"] = df["location"].apply(lambda x: re.findall(pattern, x)[1])
    new_df = df[["name", "population", "latitude", "longitude"]]
    new_df.to_csv("ukraine_cities_cleaned.csv", encoding="utf-8")


def load_ukraine_cities():
    datasets = ["ukraine_cities_cleaned.csv"]
    for dataset in datasets:
        try:
            return pd.read_csv(dataset, engine="python")
        except FileNotFoundError:
            print(f"Dataset {dataset} not found")
    print("No dataset found")
    return False


def find_city(cityname):
    df = load_ukraine_cities()
    search = df[df["name"] == cityname.lower()]
    return search


def get_location(cityname):
    city_df = find_city(cityname)
    if city_df.empty:
        return False
    location = {
        "latitude": city_df.iloc[0]["latitude"],
        "longitude": city_df.iloc[0]["longitude"],
    }
    return location


def get_location_as_string(cityname):
    location = get_location(cityname)
    if location is False:
        return None
    return f"POINT({location['longitude']} {location['latitude']})"


def get_locations_as_string(list):
    points_list = []
    for city in list:
        points_list.append(get_location_as_string(city))
    if not points_list:
        return None
    return points_list


def find_cities_in_text(text, min_len=4, max_len=10):
    if not text:
        return
    cities = []
    tokens = [word for word in text.split() if min_len <= len(word) <= max_len]
    for token in tokens:
        result = find_city(token)
        if not result.empty:
            cities.append(result.iloc[0]["name"])
    return cities


def test():
    text = "ciao questa non ZybIny è una zlynka città zolochiv"
    result = find_cities_in_text(text)
    print(result)
    print()
    print(get_locations_as_string(result))


if __name__ == "__main__":
    fetch_dataset()
    modify_dataset()
    test()
