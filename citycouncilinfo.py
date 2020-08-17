
#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

# The MIT License (MIT)
# Copyright (c) 2020 Michael M (mike.brooklyn525@gmail.com)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all 
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
# SOFTWARE.

from bs4 import BeautifulSoup
import requests
import csv
import re

NUM_CITY_COUNCIL = 51

def clean_phone_number(tel_num):
    return tel_num.lower().replace(":","").replace("fax","").replace("telephone", "").replace("phone","").replace("p","").replace('-','').replace(" ","").replace("(","").replace(")", "").strip()

def get_city_council_information(council_district):
    council_member = {}
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:79.0) Gecko/20100101 Firefox/79.0'}
    response = requests.get(url='https://council.nyc.gov/district-{}'.format(council_district), headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    h2_name_holder = soup.find("h2", class_='image-overlay-text district-member')
    if h2_name_holder is None:
        return None
    council_member["id"] = council_district
    council_member["Name"] = h2_name_holder.a.text
    council_member["District Number"] = council_district
    council_member["Email"] = ""
    council_member["Profile Image"] = ""
    council_member["District Office Address"] = ""
    council_member["District Office Phone"] = ""
    council_member["District Office Fax"] = ""
    council_member["Legislative Office Address"] = ""
    council_member["Legislative Office Phone"] = ""
    council_member["Legislative Office Fax"] = ""
    council_member_email = soup.find("a", class_="button secondary expanded dashicons-before dashicons-email-alt")
    if council_member_email is not None:
        council_member["Email"] = council_member_email["href"].replace("mailto:","")
    district_office_information = soup.find("div", attrs={"aria-label": "District office contact information"})
    if district_office_information is not None and district_office_information.find("p") is not None:
        district_office_information = soup.find("div", attrs={"aria-label": "District office contact information"}).find("p").text
        district_office_information = district_office_information.replace("<br>", "").replace("<br/>","").replace("\n","").split("\r")
        district_office_address = ""
        counter = 0
        while counter  < len(district_office_information) and not( ("phone" in district_office_information[counter].lower()) or ("fax" in district_office_information[counter].lower())) : 
            district_office_address += district_office_information[counter]+" "
            counter +=1
        council_member["District Office Address"] = district_office_address
        for i in range(counter,len(district_office_information)):
            if "phone" in district_office_information[i].lower():
                council_member["District Office Phone"] = clean_phone_number(district_office_information[i])
            elif "fax" in district_office_information[i].lower():
                council_member["District Office Fax"] = clean_phone_number(district_office_information[i])
    legislative_office_information = soup.find("div", attrs={"aria-label": "Legislative office contact information"})
    if legislative_office_information is not None and legislative_office_information.find("p") is not None:
        legislative_office_information = legislative_office_information.find("p").text
        legislative_office_information = legislative_office_information.replace("<br>", "").replace("<br/>","").replace("\n","").split("\r")
        legislative_office_address = ""
        counter = 0
        while counter < len(legislative_office_information) and not (("phone" in legislative_office_information[counter].lower()) or ("fax" in legislative_office_information[counter].lower()) ):
            legislative_office_address += legislative_office_information[counter]+" "
            counter +=1
        council_member["Legislative Office Address"] = legislative_office_address
        for i in range(counter, len(legislative_office_information)):
            if "phone" in legislative_office_information[counter].lower():
                council_member["Legislative Office Phone"] = clean_phone_number(legislative_office_information[i])
            elif "fax" in legislative_office_information[counter].lower(): 
                council_member["Legislative Office Fax"] = clean_phone_number(legislative_office_information[i])
    images_background = [ image.replace('"','').replace("'","") for image in re.findall('url\((.*?)\)', soup.prettify()) if ((".jpg" in image) or (".jpeg" in image) or (".png" in image))]
    if len(images_background):
        council_member["Profile Image"] = images_background[0]
    else:
        print(re.findall('url\((.*?)\)', soup.prettify()))
    return council_member

def convert_csv(filename, results):
    try:
        with open(filename , 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=results[0].keys())
            writer.writeheader()
            for row in results:
                writer.writerow(row)
    except IOError:
        print("I/O error")

if __name__ == '__main__':
    council_members = []
    for i in range(1,NUM_CITY_COUNCIL+1):
        council_member = get_city_council_information(i)
        if council_member is not None:
            council_members.append( council_member )
    convert_csv("findlocalrep_councilmember.csv", council_members)
    print("DONE!!!!")
