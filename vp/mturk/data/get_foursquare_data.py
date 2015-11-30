__author__ = 'michelleshu','Justin Hinh'


import Tkinter, tkFileDialog
import csv
import os
import requests
from time import sleep

def main():
    input_file_path = tkFileDialog.askopenfile()
    output_file_path = input_file_path.name[:-4] + "-fs.csv"
    output_file = open(output_file_path, 'wb')
    
    with open(input_file_path.name, 'r') as input_file:

        filewriter = csv.writer(output_file)
        filereader = csv.reader(input_file)

        filewriter.writerow(["id", "name", "latitude", "longitude", "url", "category", "address", "phone_number", "check_ins", "rating"])

        for row in filereader:
            foursquareId = row[0].strip()

            data = (requests.get("https://api.foursquare.com/v2/venues/" + foursquareId,
                params = {
                    'client_id': '5UYCQBJIYH3405FP2DXWWPQZUODAF501LTPVH2DHRS2U53DE',
                    'client_secret': 'JT1KP2GERALEXTMFATKZCFUGXOMCOCHDAMBZP0VTUVYWCOES',
                    'v': '20151003'
                })
                .json())['response']

            if (data.get('venue')):
                data = data['venue']
            else:
                continue

            name = data.get('name').encode("utf-8")
            latitude = data['location'].get('lat')
            longitude = data['location'].get('lng')

            categories = data['categories']
            primary_category = None
            for category in categories:
                if (category.get('primary')):
                    primary_category = category.get('name').encode("utf-8")

            if (data['location'].get('formattedAddress') != None):
                encoded_address = []
                for l in data['location']['formattedAddress']:
                    encoded_address.append(l.encode("utf-8"))
                formattedAddress = "\n".join(encoded_address)

            formattedPhoneNumber = data['contact'].get('formattedPhone')
            website = None
            if (data.get('url') != None):
                website = data.get('url').encode("utf-8")

            rating = data.get('rating')

            checkins = data['stats'].get('checkinsCount')

            filewriter.writerow([foursquareId, name, latitude, longitude, website, primary_category, formattedAddress, formattedPhoneNumber, checkins, rating])

        input_file.close()
        output_file.close()
main()