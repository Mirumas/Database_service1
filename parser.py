import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from models.classes import Base, Gost, Manufacturer, Parameter, Smell, Type_of_material, Printing_technology, Material
from db import get_session

def get_urls():
    url = "https://3dvision.su/material/table/fdm-fff/?utm_referer=geoadv_direct&utm_ya_campaign=65950864813&yabizcmpgn=11745514&utm_source=geoadv_direct&utm_candidate=59161049458&utm_content=16257341963&yclid=16521340288532479999"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    links = []

    div_container = soup.find('div', class_='catalog-section')
    if div_container:
        for link in div_container.find_all('a', class_='product-item-image-wrapper'):
            links.append(link['href'])

    return links


def get_data(links):
    material = []
    for l in links:
        url = 'https://3dvision.su' + l
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Находим все теги <tr> внутри таблицы
        rows = soup.find('table', class_='table').find_all('tr')

        # Создаем двумерный массив для хранения параметров и их значений
        data=[]

        name = soup.find('h1', class_='h1')
        data.append(['Название', name.text.strip()])

        price_element = soup.find('div', class_='product-item-detail-price-current')
        price = price_element['data-price']
        data.append(['Цена', price.strip()])

        # Итерируемся по каждому тегу <tr> и извлекаем параметры и их значения
        for row in rows:
            cols = row.find_all('td')
            cols = [col.text.strip() for col in cols]
            data.append([cols[0], cols[1]])
        material.append(data)
    return material

db = get_session()

data = get_data(get_urls())
print(data)


def is_manufacturer_exists(name, session):
    try:
        result = session.query(Manufacturer).filter(Manufacturer.name_manufacturer == name).one()
        return manufacturer.id_manufacturer
    except NoResultFound:
        return None


i = 1

for item in data:
    ma = is_manufacturer_exists(item[5][1])
    if ma is None:
        manufacturer = Manufacturer(name_manufacturer=item[5][1], country=item[6][1])
        ma = is_manufacturer_exists(item[5][1])

    material = Material(name_material=item[0][1], price=item[1][2], id_smell=1, id_manufacturer=ma, id_type=1)

