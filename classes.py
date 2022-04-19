class Report:
    def __init__(self, key: str, report_type: str, latitude: str, longitude: str, date: str, time: str, address: str,
                 user_id: str, county: str, postal_code: str, email: str):
        self.key = key
        self.type = report_type
        self.latitude = latitude
        self.longitude = longitude
        self.date = date
        self.time = time
        self.address = address
        self.user_id = user_id
        self.county = county
        self.postal_code = postal_code
        self.email = email

    def dump(self):
        return [self.type, self.latitude, self.longitude, self.email, self.date, self.time, self.address]

    def dump_(self):
        return " ".join(["\nID:", self.key,
                         "\nemail:", str(self.email),
                         "\nType:", self.type,
                         "\nDate:", self.date, "Time:", self.time,
                         "\nLatitude:", self.latitude, "Longitude:", self.longitude,
                         "\nAddress:", self.address,
                         "\nCounty:", self.county,
                         "\nPostal Code:", self.postal_code,
                         "\nUser ID:", self.user_id])
