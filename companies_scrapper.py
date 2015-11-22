from urllib.request import Request, urlopen
from pymongo import MongoClient

site_address = ""
client = MongoClient()
db = client.test


def scrap_companies_data():
    web_page_data = get_web_page_data()
    get_companies_data_from_web_page(web_page_data)


def get_web_page_data():
    req = Request(site_address + '/league_tables/table/global-500-2015', headers={'User-Agent': 'Mozilla/5.0'})
    return urlopen(req).read()


def get_companies_data_from_web_page(data):
    for line in data.splitlines():
        if line.startswith(b'<div id="tableWrapper">'):
            index = 0
            for raw_data in str(line).split('<tr'):
                company_name = ''
                image_name = ''
                image = None
                for raw_data_el in raw_data.split('<td'):
                    if 'table_name' in raw_data_el:
                        company_name = get_company_name(raw_data_el)
                    if 'logo_mini' in raw_data_el:
                        image, image_name = get_company_logo(raw_data_el)
                if company_name and image_name:
                    index += 1
                    db.companies.insert_one({"index": index, 'name': company_name, 'image_name': image_name,
                                             'image': image})
                    print(index)


def get_company_name(raw_data_el):
    company_name = raw_data_el[:raw_data_el.index('</a>')].rpartition('>')[-1]
    return company_name


def get_company_logo(raw_data_el):
    image_name = raw_data_el.split('"')[3]
    req = Request(site_address + image_name, headers={'User-Agent': 'Mozilla/5.0'})
    image = urlopen(req).read()
    return image_name, image


if __name__ == '__main__':
    scrap_companies_data()
