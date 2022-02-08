#Evan Supple 001513809
from csv_loader import package_importer, dist_importer
from tsp import prims, dfs
from package_routing import Package, Load, Truck

import datetime

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


#Create a dictionary to store points and vertexs
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

#loading the data from csv O(n) time and space
packages=package_importer()
matrix, names=dist_importer()

#Lookup function to convert address to indexs for the distance matrix
#O(n) time O(1) space
def address_lookup(address):
    return names.index(address)

#inserting packages in hash table O(1) time and O(n) space
for package in packages:
    my_hash.insert(int(package[0]), package[1], package[5], package[2], package[4], package[6],'hub')

print("Package data imported.")

#Packages are assigned to specific loads and loads are assigned to specific trucks
#O(n) space
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

#The error in package 9's address is corrected here because the load containing
#this package isnt leaving until 10:30.
my_hash.insert(9, '410 S State St', 'EOD', 'Salt Lake City', '84111', '2.0', 'hub')
load3_packages=[2, 8, 9, 10, 11, 12, 17,22, 23, 24, 26, 27, 33, 35 ]#14
load3_departure_time=datetime.datetime(2020, 5, 17, 10, 30)
load3=Load(3, load3_packages, load3_departure_time)
truck1.add_load(load3)
print("Trucks Loaded.")

#This function creates an adjacency list from the packages assigned to each load
#and passes it to function prims(defined in tsp.py) which creates a 
#minimum spanning tree from the package distances. The MST is passed to function dfs
# also defined in tsp.py). The output of dfs is a preorder traversal of the MST
#which is used as the tour of packages for the load.
#Function runs in total O(n^2) time b/c adjaceny list generation takes O(n^2)
#and prims also takes O(n^2) where n is the number of packages. Space is also
#O(n^2) where n is the number of packages b/c of the adjacnecy list generation.
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

    root=tree[0]
    visited =[] # Set to keep track of visited nodes.
    dfs(visited, truck_mst, root)#shortest roundtrip tour is equal to the order nodes are visited in a dfs of the mst
    return visited

load1.set_route(generate_route(load1.packages))
load2.set_route(generate_route(load2.packages))
load3.set_route(generate_route(load3.packages))
print("Load routes generated.")

#Given a specific load, this function delivers the packages in the order
#determined by the load's route. Times are calculated based on the assumed speed
#of the trucks and the distance between each pair of addresses.
#This function runs in O(n) time based on the number of packages in the load.
#Space is O(1) b/c constant space is used no matter how many packages are
#in the load.
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
        time_change=datetime.timedelta(seconds=seconds)
        total_dist+=distance
        time+=time_change
        j_package.update_status('delivered', time)
    
    #this block finds the distance and time from the last package delivery back to the hub
    i_address=my_hash.search(route[-1]).address
    j_address='HUB'
    distance=matrix[address_lookup(i_address)][address_lookup(j_address)]
    seconds=distance/speed
    time_change=datetime.timedelta(seconds=seconds)
    total_dist+=distance
    time+=time_change#dont need to update status for this last one cause its not a package
    load.set_arrival_time(time)
    return total_dist, time.strftime("%X")

dist1, time1=deliver_packages(load1)
dist2, time2=deliver_packages(load2)
dist3, time3=deliver_packages(load3)
print(f'All packages delivered. Combined distance travelled by all trucks is {dist1+dist2+dist3} miles.' )
print()

#Given id and a time, print nicely on screen all package data from the hash table
def package_info(package_id, timestamp):
    package=my_hash.search(package_id)
    status_message=package.check_status(timestamp)
    return f'|Package ID: {package.id:2}| Address: {package.address:40}| City: {package.city:17}| Zip: {package.zip:6}| Deadline: {package.deadline:10}| Weight: {package.mass:3}| Delivery Status: {status_message:21}|'


#Backcalculate the distance each truck covered at a specific time
#by finding the time each load was driving for and multiplying by 
#constant speed.
#O(n) time , O(1) space
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




#This interface for package and truck data is run after the packages are delivered and timestamped.

choice= input("Type 1 and press enter to see the data for a "+
        "specific package, type 2 and press enter to see the data for all the packages, "
        "or type q and press enter to exit.")

if choice!='q':
    if choice=='1':
        packageid=int(input('Please enter the Id of the package you would like to see the data for. '))
        while packageid<1 or packageid>40:
            print('Package does not exist!')
            packageid=int(input('Please enter the Id of the package you would like to see the data for. '))

        time_string=input('Enter a time after 08:00:00 (in millitary time i.e., 0900) to check package status. '+
           'The entered time must have exactly 4 digits. ' )
        hour=int(time_string[:2])
        minute=int(time_string[2:])

        while len(time_string)!=4 or hour<8 or minute>59:
            print('Time entered incorrectly. ')
            time_string=input('Enter a time after 08:00:00 (in millitary time i.e., 0900) to check package status. '+
           'The entered time must have exactly 4 digits. ' )
            hour=int(time_string[:2])
            minute=int(time_string[2:])
        time=datetime.datetime(2020, 5, 17, hour, minute)
        print()
        print(f'Packge data for package number {packageid} at time '+ time.strftime("%X"))
        print()
        print(package_info(packageid, time))
        print(f'Total mileage traveled by all trucks as of ' + time.strftime("%X") + f': {total_truck_distance(time)} miles' )

    if choice=='2':
        time_string=input('Enter a time after 08:00:00 (in millitary time i.e., 0900) to check package status. '+
           'The entered time must have exactly 4 digits. ' )
        hour=int(time_string[:2])
        minute=int(time_string[2:])

        while len(time_string)!=4 or hour<8 or hour>23 or minute>59:
            print('Time entered incorrectly. ')
            time_string=input('Enter a time after 08:00:00 (in millitary time i.e., 0900) to check package status. '+
           'The entered time must have exactly 4 digits. ' )
            hour=int(time_string[:2])
            minute=int(time_string[2:])
        time=datetime.datetime(2020, 5, 17, hour, minute)
        print()
        print(f'Packge data for all packages at time '+ time.strftime("%X")+ ' : ')
        print()

        for i in range(1, 41):
            print(package_info(i, time))
        
        print(f'Total mileage traveled by all trucks as of ' + time.strftime("%X") + f': {total_truck_distance(time)} miles' )

#total program runtime O(n^2), total space O(n^2)
            





