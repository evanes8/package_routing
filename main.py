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
'''
truck1=[1, 13, 14, 15, 16, 19, 20, 29, 30, 31, 34, 37]
'''
load1_packages=[1, 13, 14, 15, 16, 19, 20, 29, 30, 31, 34, 37]
load1_departure_time=datetime.datetime(2020, 5, 17, 8) 
load1=Load(1, load1_packages, load1_departure_time)
truck1=Truck(1)
truck1.add_load(load1)

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
    truck_mst.print_items()

    root=tree[0]
    visited =[] # Set to keep track of visited nodes.
    dfs(visited, truck_mst, root)#shortest roundtrip tour is equal to the order nodes are visited in a dfs of the mst
    return visited

#################
load1.set_route(generate_route(load1.packages))
print(load1.route)

'''
#need to create an ajdecy list from this 
truck1_adjlist=AdjacencyList()

for id1 in truck1:
    id1_val=[]
    for id2 in truck1:
        if id2!=id1:
            distance=matrix[(address_lookup(my_hash.search(id1).address))][(address_lookup(my_hash.search(id2).address))]
            id1_val.append([id2, distance])
    truck1_adjlist.insert(id1, id1_val)

#every adjency list should start and end at the hub so hub will be included regardless
#of the the packages loaded
#create hubs adjency list and update the lists for all to include hub
for id2 in truck1:
    distance=matrix[0][(address_lookup(my_hash.search(id2).address))]
    truck1_adjlist.add_vertex(0, [id2, distance])
    truck1_adjlist.add_vertex(id2, [0, distance])

#truck1_adjlist.print_items()

#choose a vertex from keys
#tree.append(vertex)
#for each vertex in tree return the min if that min- if the min is in tree find a new one and return that
#once u have the mins of all the vertexs in tree pick the smallest one and append it to tree
#if a vertex has no valid min to return just return none
#when ur overall min is none your done


tree, parents=prims(truck1_adjlist, 0)
truck1_mst=AdjacencyList()
for i in range(1, len(parents)):
    truck1_mst.add_vertex(parents[i], tree[i])

truck1_mst.print_items()



#truck1_mst is an adj list of the mst graph
#now do simple dfs discovery
root=tree[0]
visited =[] # Set to keep track of visited nodes.
dfs(visited, truck1_mst, root)#shortest roundtrip tour is equal to the order nodes are visited in a dfs of the mst
print(visited)
'''
#deliver the packages along the route in visited
#keep track of distance travled starting from the hub
#trucks move at 18 mph
#time starts at 8am
#timesstamp when they are on enroute and delivered as [0, 0] or time

#this has to be made into a funtion
#takes in start time and the trucks visited array
#set that status as enroute and include a timestamp
#then deliver and mark time as u deliver
def deliver_packages(route, start_time):
    total_dist=0
    time=start_time
    speed=.005 #miles per second

    for packageid in route:
        if packageid!=0:
            package=my_hash.search(packageid)
            package.update_status('enroute', start_time)

    for i in range(len(route)-2):#iterate to second to last package
        j=i+1
        if route[i]==0:
            i_address='HUB'#hub isnt a package so its not in the hashtable
        
        else:
            i_address=my_hash.search(route[i]).address
        
        j_package=my_hash.search(route[j])
        j_address=j_package.address
        distance=matrix[address_lookup(i_address)][address_lookup(j_address)]
        seconds=distance/speed
        print(distance, seconds)
        time_change=datetime.timedelta(seconds=seconds)
        total_dist+=distance
        time+=time_change
        j_package.update_status('delivered', time)
    #this for loop dosnt include time from last package back to hub need to add that
    i_address=my_hash.search(route[-1]).address
    j_address='HUB'
    distance=matrix[address_lookup(i_address)][address_lookup(j_address)]
    seconds=distance/speed
    print(distance, seconds)
    time_change=datetime.timedelta(seconds=seconds)
    total_dist+=distance
    time+=time_change#dont need to update status for this last one cause its not a package
    return total_dist, time.strftime("%X")

print(deliver_packages(load1.route, load1.departure_time))
print(my_hash.search(14).status, my_hash.search(14).enroute_time)

'''
total_dist=0
time=datetime.datetime(2020, 5, 17, 8)
speed=.005 #miles per second
for i in range(len(visited)-2):#iterate to second to last package
    j=i+1
    if visited[i]==0:
        i_address='HUB'#hub isnt a package so its not in the hashtable
    else:
        i_address=my_hash.search(visited[i]).address
    
    j_package=my_hash.search(visited[j]) 
    j_address=j_package.address
    distance=matrix[address_lookup(i_address)][address_lookup(j_address)]
    seconds=distance/speed
    print(distance, seconds)
    time_change=datetime.timedelta(seconds=seconds)
    total_dist+=distance
    time+=time_change
    my_hash.update_status(j_package.id, time)
#this for loop dosnt include time from last package back to hub need to add that
i_address=my_hash.search(visited[-1]).address
j_address='HUB'
distance=matrix[address_lookup(i_address)][address_lookup(j_address)]
seconds=distance/speed
print(distance, seconds)
time_change=datetime.timedelta(seconds=seconds)
total_dist+=distance
time+=time_change



print(total_dist)
print(time.strftime("%X"))
'''
