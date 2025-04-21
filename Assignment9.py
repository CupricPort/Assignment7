import arcpy
import requests
import csv

arcpy.env.overwriteOutput = True

def extract():
    '''
    Extract the source data table.
    '''
    r = requests.get('https://docs.google.com/spreadsheets/d/e/2PACX-1vTDjitOlmILea7koCORJkq6QrUcwBJM7K3vy4guXB0mU_nWR6wsPn136bpH6ykoUxyYMW7wTwkzE37l/pub?output=csv')
    r.encoding = ('utf-8')
    data = r.text
    with open(r'C:\Users\benlj\OneDrive\Documents\School\SpringSemester2025\ProgrammingForGIS\addresses.csv', 'w') as output_file:
        output_file.write(data)
extract()

def transform():
    transformed_file = open(r'C:\Users\benlj\OneDrive\Documents\School\SpringSemester2025\ProgrammingForGIS\new_addresses.csv', 'w')
    transformed_file.write("X,Y,Type\n")
    with open(r'C:\Users\benlj\OneDrive\Documents\School\SpringSemester2025\ProgrammingForGIS\addresses.csv', 'r') as partial_file:
        csv_dist = csv.DictReader(partial_file, delimeter=',')
        for row in csv_dist:
            address = row['Street Address'] + "Boulder CO"
            print(address)
            geocode_url = "https://geocoding.geo.geocensus.gov/geocoder/locations/oneLineaddress?adreess=" + address + \
                          "&benchmakr=2020&format=json"
            r = requests.get(geocode_url)

            resp_dict = r.json()
            x = resp_dict['result']['addressMatches'][0]['coordinates']['x']
            y = resp_dict['result']['addressMatches'][0]['coordinates']['y']
            transformed_file.write(f"{x}, {y}, Residential\n")

    transformed_file.close()

def load():
    arcpy.env.workspace = r"C:\Users\benlj\OneDrive\Documents\School\SpringSemester2025\ProgrammingForGIS\ProgrammingLabs\ProgrammingLabs.gdb"
    arcpy.env.overwriteOutput = True

    in_table = r'C:\Users\benlj\OneDrive\Documents\School\SpringSemester2025\ProgrammingForGIS\new_addresses.csv'
    out_feature_class = 'avoid_points'
    x_coords = 'X'
    y_coords = 'Y'

    arcpy.management.XYTableToPoint(in_table, out_feature_class, x_coords, y_coords)

    print(arcpy.GetCount_management(out_feature_class))

if __name__ == '--main__':
    extract()
    transform()
    load()
