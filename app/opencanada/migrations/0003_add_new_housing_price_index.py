# Generated by Django 3.0.6 on 2020-05-26 16:16

from django.db import migrations
import datetime
import pandas as pd

def create_data(apps, schema_editor):
    file = "./opencanada/data/18100205_new_housing_price_index.csv"
    df = pd.read_csv(file)
    df = df.drop(df.index[df['GEO'] == 'Census metropolitan areas'].tolist())
    df = df.drop(df.index[df['GEO'] == 'Ottawa-Gatineau, Ontario/Quebec'].tolist())

    ottawa_indices = df.index[df['GEO'] == 'Ottawa-Gatineau, Ontario part, Ontario/Quebec'].tolist()
    gatineau_indices = df.index[df['GEO'] == 'Ottawa-Gatineau, Quebec part, Ontario/Quebec'].tolist()
    for i in ottawa_indices:
        df.loc[i, 'GEO'] = "Ottawa, Ontario"

    for i in gatineau_indices:
        df.loc[i, 'GEO'] = "Gatineau, Quebec"

    new = df["GEO"].str.split(", ", n = 1, expand = True) 
    df["CITY"] = new[0] 
    df["PROVINCE"] = new[1]
    df.dropna(subset = ["PROVINCE"], inplace=True)
    df.dropna(subset = ["VALUE"], inplace=True)


    new = df["REF_DATE"].str.split("-", n = 1, expand = True) 
    df["YEAR"] = new[0] 
    df["MONTH"] = new[1]

    Country = apps.get_model('opencanada', 'Country')
    canada = Country.objects.filter(name='Canada')[0]

    Province = apps.get_model('opencanada', 'Province')
    City = apps.get_model('opencanada', 'City')


    HousingPriceIndex = apps.get_model('opencanada', 'HousingPriceIndex')
    for c, p, v, m, y, t in zip(df.CITY, df.PROVINCE, df.VALUE, df.MONTH, df.YEAR, df['New housing price indexes']):
        city = City.objects.filter(name=c)
        #make a new city if needed
        if len(city) == 0:
            prov = Province.objects.filter(name=p)
            #make new province if needed
            if len(prov) == 0:
                prov = Province(name=p, country=canada)
                prov.save()
            else:
                prov = prov[0]
            city = City(name=c, province=prov)
            city.save()
        else:
            city = city[0]

        #See if housing price index already exists
        if t == "Total (house and land)":
            index_type = 'B'
        elif t ==  'House only':
            index_type = 'H'
        elif t ==  'Land only':
            index_type = 'L'

        HousingPriceIndex(city = city, date=datetime.date(int(y), int(m), 1), index_type=index_type, index_value=v).save()


class Migration(migrations.Migration):

    dependencies = [
        ('opencanada', '0002_addvacancysixunitsdata'),
    ]

    operations = [
        migrations.RunPython(create_data),
    ]
