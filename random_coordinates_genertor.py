from faker import Faker

fake = Faker()
Faker.seed(0)
# key, report_type, report_latitude, report_longitude, report_date, report_time,
# report_address, user_reporting_id, report_county, report_postal_code, email
'''data = []
types = ['Suspicious Drug Activity', 'Street-based Prostitution']
for i in range(5):
    moc_data = fake.local_latlng()
    print(i, types[0], moc_data[0], moc_data[1], '', '', '', '', '', '', 'moc')
'''

