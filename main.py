import csv
import datetime
import random

from faker import Faker
import firebase_admin
from firebase_admin import db, credentials, auth
from itertools import groupby
from classes import Report
import plotly.graph_objects as go
import pandas as pd
from geopy.geocoders import Nominatim

MOC = True


def main():
    if not MOC:
        cred = credentials.Certificate("android-location-699e9-firebase-adminsdk-49wyo-aa19913070.json")
        firebase_admin.initialize_app(cred,
                                      {'databaseURL': 'https://android-location-699e9-default-rtdb.firebaseio.com/'})
        database = db.reference('Locations')
        data = dict(database.get())
        keys = data.keys()
        reports = []
        na = "NA"
        for key in keys:
            try:
                report_type = data[key]['type']
            except KeyError:
                report_type = na
            try:
                report_latitude = data[key]['latitude']
            except KeyError:
                report_latitude = na
            try:
                report_longitude = data[key]['longitude']
            except KeyError:
                report_longitude = na
            try:
                report_date = data[key]['date']
            except KeyError:
                report_date = na
            try:
                report_time = data[key]['time']
            except KeyError:
                report_time = na
            try:
                report_address = data[key]['address']
            except KeyError:
                report_address = na
            try:
                user_reporting_id = data[key]['userId']
            except KeyError:
                user_reporting_id = na
            try:
                report_county = data[key]['county']
            except KeyError:
                report_county = na
            try:
                report_postal_code = data[key]['postalCode']
            except KeyError:
                report_postal_code = na
            try:
                anonymous = data[key]['anonymous']
                if not anonymous:
                    email = get_user_info(user_reporting_id)
                else:
                    email = 'anonymous'
            except KeyError:
                email = get_user_info(user_reporting_id)

            reports.append(Report(key, report_type, report_latitude, report_longitude, report_date, report_time,
                                  report_address, user_reporting_id, report_county, report_postal_code, email))

    else:
        reports = moc_reports()

    groups = [list(result) for key, result in groupby(
        reports, key=lambda obj: obj.type)]

    sorted_reports = []
    i = 0
    for group in groups:
        temp = []
        for report in group:
            report = report.dump()
            temp.append(report)
            if report is group[-1]:
                temp = []
        print(len(temp), temp[0][0])
        data_to_csv(temp, i)
        i += 1
        sorted_reports.append(temp)
    plot_graph()


def moc_reports():
    fake = Faker()
    Faker.seed(0)
    types = ['Suspicious Drug Activity', 'Street-based Prostitution']
    data = [[], []]
    for i in range(0, 25):
        moc_data = fake.local_latlng()
        data[0].append([types[0], moc_data[0], moc_data[1], 'moc@moc.com'])
        moc_data = fake.local_latlng()
        data[1].append([types[1], moc_data[0], moc_data[1], 'moc@moc.com'])
    reports = []
    for group in data:
        for report in group:
            reports.append(Report('', report[0], report[1], report[2], get_random_date(), get_random_time(),
                                  get_address(report[1], report[2]), '', '', '', report[3]))
    return reports


def get_address(latitude, longitude):
    geolocator = Nominatim(user_agent="DriveAware")
    location = geolocator.reverse(latitude + ',' + longitude)
    return location[0]


def get_random_time():
    return str(random.randint(0, 59)) + ':' + str(random.randint(0, 59)) + ':' + str(random.randint(0, 59))


def get_random_date():
    # ref: https://www.adamsmith.haus/python/answers/how-to-generate-a-random-date-between-two-dates-in-python
    start_date = datetime.date(2019, 1, 1)
    end_date = datetime.date(2020, 12, 31)
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + datetime.timedelta(days=random_number_of_days)
    return str(random_date)


def get_user_info(user_id):
    page = auth.list_users()
    while page:
        for user in page.users:
            if user.uid == user_id:
                return user.email
        page = page.get_next_page()


def print_groups(reports):
    print('Total # reports:', len(reports))
    groups = [list(result) for key, result in groupby(
        reports, key=lambda obj: obj.email)]
    line = "-------------------------------"
    print(str(len(groups)) + " group(s)\n")
    for group in groups:
        print(str(len(group)) + " report(s)")
        print(line, end="")
        for report in group:
            print(report.dump())
        print(line)
    print('Total # reports:', len(reports))


def data_to_csv(reports: list, report_id: int = -1):
    with open('reports/report' + str(report_id) + '.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['Type', 'Latitude', 'Longitude', 'Email', 'Date', 'Time', 'Address'])
        for report in reports:
            writer.writerow([report[0], report[1], report[2], report[3], report[4], report[5], report[6]])


def plot_graph():
    df = pd.read_csv('reports/report0.csv')
    df.head()
    df_size = len(df)
    df1 = pd.read_csv('reports/report1.csv')
    df1.head()
    df1_size = len(df1)
    df['text'] = 'Type ' + 'Latitude' + 'Longitude' + 'Email' + 'Date' + 'Time' + 'Address'
    df1['text'] = df['text']
    scale = df_size + df1_size
    min_size = 5
    if MOC:
        plot_title = 'DriveAware MOC Reports'
    else:
        plot_title = 'DriveAware Reports'

    fig = go.Figure()
    fig.add_trace(go.Scattergeo(
        locationmode='USA-states',
        text=df['Type'] + '<br>' + df['Date'] + ' ' + df['Time'] +
        '<br>Address:' + df['Address'] + '<br>Email:' + df['Email'],
        lon=df['Longitude'],
        lat=df['Latitude'],
        marker=dict(
            size=min_size + (df_size / scale) * 5,
            color='rgba(255,165,0,0.3)',
            line_color='rgba(40,40,40)',
            line_width=1,
            sizemode='area'
        ),
        name='Suspicious Drugs Activity: ' + str(df_size)))
    fig.add_trace(go.Scattergeo(
        locationmode='USA-states',
        text=df['Type'] + '<br>' + df['Date'] + ' ' + df['Time'] +
        '<br>Address:' + df['Address'] + '<br>Email:' + df['Email'],
        lon=df1['Longitude'],
        lat=df1['Latitude'],
        marker=dict(
            size=min_size + (df1_size / scale) * 5,
            color='rgba(50,205,50,0.3)',
            line_color='rgb(40,40,40)',
            line_width=1,
            sizemode='area'
        ),
        name='Street-based Prostitution: ' + str(df1_size)))
    fig.update_layout(
        title_text=plot_title,
        showlegend=True,
        geo=dict(
            scope='usa',
            landcolor='rgb(217, 217, 217)',
        )
    )
    # fig.show()
    if MOC:
        fig.write_html("DriveAware_MOC_Report.html")
    else:
        fig.write_html("DriveAware_Report.html")


if __name__ == "__main__":
    main()
