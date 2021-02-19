import os
import time

import pandas as pd
import requests


def processed_data(data):
    result = []
    for item in data:
        address = item['formatted_address'].split(",")
        province = address[-2].split()
        result.append({
            "longitude": item['geometry']['location']['lng'],
            "latitude": item['geometry']['location']['lat'],
            "kelurahan": address[2],
            "kecamatan": address[3],
            "kota": address[4],
            "provinsi": " ".join([x for x in province[:-1]]),
            "kodepos": province[-1],
            "name": item["name"],
            "place_id": item["place_id"],
            "rating": item["rating"],
            "types": ",".join(item["types"]),
            "image": item["icon"]
        })

    return result


def fetch_data(query_input: str = None, next_page_token=None, results: list = []):
    api_key = os.getenv("GOOGLE_MAP_API_KEY")
    url = os.getenv("GOOGLE_MAP_URL")

    if query_input == "":
        raise Exception("input cannot be empty")

    params = {
        "key": api_key,
        "query": query_input
    }

    if next_page_token is not None:
        params.update({"pagetoken": next_page_token})

    r = requests.get(url, params)
    data = r.json()

    if data['results']:
        results.extend(data['results'])

    # allow pagination
    if 'next_page_token' in data:
        fetch_data(query_input, data['next_page_token'], results)

    return results


def export_to_csv(data, filename):
    output = os.path.dirname(os.path.abspath(__file__)) + "/output/" + filename
    df = pd.DataFrame(data)

    df.to_csv(output, header='column_names')
    print("Data Exported to " + output)


def main():
    while True:
        try:
            print("Input search query :")
            query_input = input()

            data = fetch_data(query_input)

            if data:
                data = processed_data(data)
                filename = "_".join(query_input.split()) + "_" + str(int(time.time())) + ".csv"
                export_to_csv(data, filename)
            else:
                print("data not found")

        except Exception as e:
            print(e)


main()
