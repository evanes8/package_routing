from loader import package_importer, dist_importer
from tsp import prims, dfs
from package_routing import Package, Load, Truck

import datetime

#for rn i dont see why this is useful ill just read directly into the hash table


#the hashtable insert should be able to work on its own and create brand new packages to
#be added. we just happen to be reading our objects into this hash table
class HashTable:
    def __init__(self, initial_cap=40):
        self.table =[]
        for i in range(initial_cap):
            self.table.append([])
    
    def insert(self, id, address, deadline, city, zip, mass, status):
        new_package=Package(id, address, deadline, city, zip, mass, status)
        bucket=hash(new_package)%len(self.table)
        bucket_list=self.table[bucket]
        
        for package in bucket_list:
            if package.id==new_package.id:
                bucket_list.remove(package)
        bucket_list.append(new_package)
        return True

    def search(self, id):
        bucket=hash(id)%len(self.table)
        bucket_list=self.table[bucket]
        for package in bucket_list:
            if package.id==id:
                return package
        return None



#create a dictionary that will be used to store values from matrix
class AdjacencyList:
    def __init__(self, initial_cap=20):
        self.table =[]
        for i in range(initial_cap):
            self.table.append([])
    def insert(self, key, item):
        bucket=hash(key)%len(self.table)
        bucket_list=self.table[bucket]

        for kv in bucket_list:
            if kv[0]==key:
                kv[1]=item
                return True
        key_value=[key, item]
        bucket_list.append(key_value)
        return True

    def add_vertex(self, key, vertex):
        bucket=hash(key)%len(self.table)
        bucket_list=self.table[bucket]

        for kv in bucket_list:
            if kv[0]==key:
                kv[1].append(vertex)
                return True
        key_value=[key,[vertex]]
        bucket_list.append(key_value)
        return True


    def search(self, key):
        bucket=hash(key)%len(self.table)
        bucket_list=self.table[bucket]
        for kv in bucket_list:
            if kv[0]==key:
                return kv[1]
        return None
    
    def keys(self):
        keys=[]
        for bucket in self.table:
            for key, value in bucket:
                keys.append(key)
        return keys
    
    def print_items(self):
        for bucket in self.table:
            for key, value in bucket:
                print(key, value)




my_hash=HashTable()

packages=package_importer()
matrix, names=dist_importer()

def address_lookup(address):
    return names.index(address)

for package in packages:
    my_hash.insert(int(package[0]), package[1], package[5], package[2], package[4], package[6],'hub')

#load trucks with ids of packages
load1_packages=[1,5, 7, 13, 14, 15, 16, 19, 20,21, 29, 30, 34, 37, 39]#15
load1_departure_time=datetime.datetime(2020, 5, 17, 8) 
load1=Load(1, load1_packages, load1_departure_time)
truck1=Truck(1)
truck1.add_load(load1)

load2_packages=[3,4, 6,18, 25, 28,31, 32,  36, 38,40]#11
load2_departure_time=datetime.datetime(2020, 5, 17, 9, 5)
load2=Load(2, load2_packages, load2_departure_time)
truck2=Truck(2)
truck2.add_load(load2)

my_hash.insert(9, '410 S State St', 'EOD', 'Salt Lake City', '84111', '2.0', 'hub')
load3_packages=[2, 8, 9, 10, 11, 12, 17,22, 23, 24, 26, 27, 33, 35 ]#14
load3_departure_time=datetime.datetime(2020, 5, 17, 10, 30)
load3=Load(3, load3_packages, load3_departure_time)
truck1.add_load(load3)
#finish the rest of loading and testing
###################
def generate_route(package_list):
    truck_adjlist=AdjacencyList()
    for id1 in package_list:
        id1_val=[]
        for id2 in package_list:
            if id2!=id1:
                distance=matrix[(address_lookup(my_hash.search(id1).address))][(address_lookup(my_hash.search(id2).address))]
                id1_val.append([id2, distance])
        truck_adjlist.insert(id1, id1_val)
    
    for id2 in package_list:
        distance=matrix[0][(address_lookup(my_hash.search(id2).address))]
        truck_adjlist.add_vertex(0, [id2, distance])
        truck_adjlist.add_vertex(id2, [0, distance])
     
    tree, parents=prims(truck_adjlist, 0)
    truck_mst=AdjacencyList()
    for i in range(1, len(parents)):
        truck_mst.add_vertex(parents[i], tree[i])
   # truck_mst.print_items()

    root=tree[0]
    visited =[] # Set to keep track of visited nodes.
    dfs(visited, truck_mst, root)#shortest roundtrip tour is equal to the order nodes are visited in a dfs of the mst
    return visited

#################
load1.set_route(generate_route(load1.packages))
print(load1.route)

load2.set_route(generate_route(load2.packages))
print(load2.route)

load3.set_route(generate_route(load3.packages))
print(load3.route)
#deliver the packages along the route in visited
#keep track of distance travled starting from the hub
#trucks move at 18 mph
#time starts at 8am
#timesstamp when they are on enroute and delivered as [0, 0] or time

#this has to be made into a funtion
#takes in start time and the trucks visited array
#set that status as enroute and include a timestamp
#then deliver and mark time as u deliver
def deliver_packages(load):
    route=load.route
    start_time=load.departure_time
    total_dist=0
    time=start_time
    speed=.005 #miles per second

    for packageid in route:
        if packageid!=0:
            package=my_hash.search(packageid)
            package.update_status('enroute', start_time)

    for i in range(len(route)-1):#iterate to second to last package
        j=i+1
        if route[i]==0:
            i_address='HUB'#hub isnt a package so its not in the hashtable
        
        else:
            i_address=my_hash.search(route[i]).address
        
        j_package=my_hash.search(route[j])
        j_address=j_package.address
        distance=matrix[address_lookup(i_address)][address_lookup(j_address)]
        seconds=distance/speed
        print(i_address,'|',  j_address,'|',  distance,'|',  seconds)
        time_change=datetime.timedelta(seconds=seconds)
        total_dist+=distance
        time+=time_change
        j_package.update_status('delivered', time)
    #this for loop dosnt include time from last package back to hub need to add that
    i_address=my_hash.search(route[-1]).address
    j_address='HUB'
    distance=matrix[address_lookup(i_address)][address_lookup(j_address)]
    seconds=distance/speed
    print(i_address,'|',  j_address,'|',  distance,'|',  seconds)
    time_change=datetime.timedelta(seconds=seconds)
    total_dist+=distance
    time+=time_change#dont need to update status for this last one cause its not a package
    load.set_arrival_time(time)
    return total_dist, time.strftime("%X")

print(deliver_packages(load1))
print(deliver_packages(load2))
print(deliver_packages(load3))

'''
#make sure each package is delivered in time test

for id in range(1, 41):
    package=my_hash.search(id)
    print('package ID: ', package.id,  'package deadline :',
            package.deadline, 'package enroute :', package.enroute_time, 'package delivered :', package.delivered_time)

'''

def package_info(package_id, timestamp):
    #given a proper datetime and package id, print nicley on screen all package data
    package=my_hash.search(package_id)
    status_message=package.check_status(timestamp)
    return f'|Package ID: {package.id:2}| Address: {package.address:40}| City: {package.city:17}| Zip: {package.zip:6}| Deadline: {package.deadline:10}| Weight: {package.mass:3}| Delivery Status: {status_message:21}|'


#also need a function to display total distance of all the trucks at a specific time

def total_truck_distance(time):
    total_distance=0
    loads=truck1.loads+truck2.loads
    for load in loads:
        if load.arrival_time<=time:
            time_diff=load.arrival_time-load.departure_time
        elif load.departure_time<=time:
            time_diff=time-load.departure_time
        else:
            time_diff=datetime.timedelta(seconds=0)
        distance=time_diff.total_seconds()*.005 #miles per second
        total_distance+=distance
    return total_distance




for i in range(1, 41):
    print(package_info(i, datetime.datetime(2020, 5, 17, 9, 35)))

print(total_truck_distance(datetime.datetime(2020, 5, 17, 9, 35)))

#now that these functions work need to create a while loop prompt
#also need to parse time input and convert to proper datetime


