import csv


def dist_loader():
    with open('distance_table_csv.csv', newline='') as csv_file:
        csv_reader=csv.reader(csv_file)
        linecount=0
        rows=[]
        names=[]
        for row in csv_reader:
            linecount+=1
            if linecount==8:
                names=row
            elif linecount>8:
                rows.append(row)
        names=names[2:]


        for pos, row in enumerate(rows):
            row=row[2:]
            rows[pos]=row
        

        matrix=[[-1000]*27 for i in range(28)]
    

        count=0
        
       # print(matrix[0][0]) #0-27
    
        for i, row in enumerate(rows):
            for j, num in enumerate(row):
                matrix[i][j]=num

        matrix.pop(len(matrix)-1)
        for i in range(len(matrix)):
            for j in range(len(matrix)):
                matrix[i][j]=matrix[j][i]
        for i in range(len(matrix)):
            for j in range(len(matrix)):
                matrix[i][j]=float(matrix[i][j])
        names[1]='1060 Dalton Ave S'
        for pos, name in enumerate(names):
            name=name.strip()
            names[pos]=name
    return matrix, names
    
#name lsit is loaded by this point


def package_loader():
    with open('packages.csv', newline='') as csv_file:
        csv_reader=csv.reader(csv_file)
        linecount=0
        packages=[]
        for row in csv_reader:
            if linecount>7:
                packages.append(row)
            linecount+=1
    return packages

