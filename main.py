import csv
import datetime
import os
import random
from faker import Faker
import firebase_admin
from firebase_admin import db, credentials, auth
from classes import Report
import plotly.graph_objects as go
import pandas as pd
from geopy.geocoders import Nominatim
import pyrebase


MOCK = False
config = {
  "apiKey": "AIzaSyDxX9QaTuO7d_IFNu9TIcbApHf3Pt9ExQw",
  "authDomain": "android-location-699e9.firebaseapp.com",
  "databaseURL": "https://android-location-699e9-default-rtdb.firebaseio.com",
  "projectId": "android-location-699e9",
  "storageBucket": "android-location-699e9.appspot.com",
  "messagingSenderId": "786487980961",
  "appId": "1:786487980961:web:df375320bb4bc11944d1e0",
  "measurementId": "G-2YXB5JNKX3"
}


def main():
    get_csv_reports()
    if MOCK:
        save_reports(mock_reports())
    else:
        save_reports(get_db_reports())
    plot_graph()


def save_reports(reports: list):
    types = ['Suspicious Drug Activity', 'Street-based Prostitution']
    reports0 = []
    reports1 = []
    for report in reports:
        if report.get_type() == types[0]:
            reports0.append(report.dump())
        else:
            reports1.append(report.dump())
    data_to_csv(reports0, 0)
    data_to_csv(reports1, 1)


def get_db_reports():
    a_file = open("../common/report_ids.txt", "w")
    a_file.truncate()
    a_file.close()
    cred = credentials.Certificate("android-location-699e9-firebase-adminsdk-49wyo-aa19913070.json")
    firebase_admin.initialize_app(cred,
                                  {'databaseURL': 'https://android-location-699e9-default-rtdb.firebaseio.com/'})
    database = db.reference('Locations')
    storage = pyrebase.initialize_app(config).storage()
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
            has_image = str(data[key]['has_image'])
            if has_image == "True":
                with open('../common/report_ids.txt', 'a') as filehandle:
                    filehandle.write('%s\n' % key)
                storage.child("pictures/" + key + ".jpg").download("/home/alvaro/Desktop/DriveAwarePython/get_reports/",
                                                                   "images/" + key + ".jgp")
        except KeyError:
            has_image = na
        try:
            anonymous = data[key]['anonymous']
            if not anonymous:
                email = get_user_email(user_reporting_id)
            else:
                email = 'anonymous'
        except KeyError:
            email = get_user_email(user_reporting_id)

        reports.append(Report(key, report_type, report_latitude, report_longitude, report_date, report_time,
                              report_address, user_reporting_id, report_county, report_postal_code, email, has_image))
    return reports


def mock_reports():
    fake = Faker()
    Faker.seed(0)
    types = ['Suspicious Drug Activity', 'Street-based Prostitution']
    data = [[], []]
    for i in range(0, 25):
        mock_data = fake.local_latlng()
        data[0].append([types[0], mock_data[0], mock_data[1], 'moc@moc.com'])
        mock_data = fake.local_latlng()
        data[1].append([types[1], mock_data[0], mock_data[1], 'moc@moc.com'])
    reports = []
    for group in data:
        for report in group:
            reports.append(Report('', report[0], report[1], report[2], get_random_date(), get_random_time(),
                                  get_address(report[1], report[2]), '', '', '', report[3], False))
    return reports


def get_address(latitude, longitude):
    geo_locator = Nominatim(user_agent="DriveAware")
    location = geo_locator.reverse(latitude + ',' + longitude)
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


def get_user_email(user_id):
    page = auth.list_users()
    while page:
        for user in page.users:
            if user.uid == user_id:
                return user.email
        page = page.get_next_page()


def data_to_csv(reports: list, report_id: int = -1):
    with open('reports/report' + str(report_id) + '.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['Type', 'Latitude', 'Longitude', 'Email', 'Date', 'Time', 'Address', 'Has_image'])
        for report in reports:
            writer.writerow([report[0], report[1], report[2], report[3], report[4], report[5], report[6], report[7]])


def get_csv_reports():
    directory = 'reports'
    files = []
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            files.append(file_path)
    return files


def plot_graph():
    reports = get_csv_reports()
    types = ['Suspicious Drug Activity', 'Street-based Prostitution']
    colors = ['rgba(255,165,0,0.3)', 'rgba(50,205,50,0.3)']
    trace_size = 10
    if MOCK:
        plot_title = 'DriveAware MOCK Reports'
    else:
        plot_title = 'DriveAware Reports'
    fig = go.Figure()
    for (report, color, type_) in zip(reports, colors, types):
        df = pd.read_csv(report)
        df.head()
        df_size = len(df)
        df['text'] = 'Type ' + 'Latitude' + 'Longitude' + 'Email' + 'Date' + 'Time' + 'Address'
        fig.add_trace(go.Scattergeo(
            locationmode='USA-states',
            text=df['Type'] + '<br>' + df['Date'] + ' ' + df['Time'] +
            '<br>Address:' + df['Address'] + '<br>Email:' + df['Email'] + " <a href=\"../common/images/-N2kwbO5uzvYCC9jgmJZ.jgp\">picture</a>",  #  <img src=\"../common/images/-N2kwbO5uzvYCC9jgmJZ.jgp\" width=\"500\" height=\"600\"> ",
            lon=df['Longitude'],
            lat=df['Latitude'],
            marker=dict(
                size=trace_size,
                color=color,
                line_color='rgba(40,40,40)',
                line_width=0.5,
                sizemode='area'
            ),
            name=type_ + ': ' + str(df_size)))
    fig.update_layout(
        title_text=plot_title,
        showlegend=True,
        geo=dict(
            scope='usa',
            landcolor='rgb(217, 217, 217)',
        )
    )
    # fig.show()
    if MOCK:
        fig.write_html("../common/DriveAware_MOCK_Report.html")
    else:
        fig.write_html("../common/DriveAware_Report.html")


if __name__ == "__main__":
    main()
