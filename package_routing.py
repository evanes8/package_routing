import datetime


class Package:
    def __init__(self, id, address, deadline, city, zip, mass, status):
        self.id = id
        self.address=address
        self.deadline=deadline
        self.city=city
        self.zip=zip
        self.mass=mass
        self.status=status
        self.enroute_time=0
        self.delivered_time=0
    
    def __hash__(self):
        return self.id
    
    def update_status(self, status, *args):
        self.status=status
        for arg in args:
            if isinstance(arg, datetime.date):
                if self.status=='enroute':
                    self.enroute_time=arg
                else:
                    self.delivered_time=arg

class Load():
    def __init__(self, id, packages, departure_time):
        self.id=id
        self.packages=packages
        self.departure_time=departure_time
        self.arrival_time=None
        self.route=None
    
    def set_arrival_time(self, arrival_time):
        self.arrival_time=arrival_time
    def set_route(self, route):
        self.route=route

class Truck():
    def __init__(self, id):
        self.id=id
        self.loads=[]
    def add_load(self, load):
        self.loads.append(load)
    def get_load(self, load_id):
        for load in self.loads:
            if load.id==load_id:
                return load


