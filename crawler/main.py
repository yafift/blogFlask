import xml.etree.ElementTree as ET
import urllib.request
import random
import hashlib
from zipfile import ZipFile
import os
import sqlite3
import csv
import datetime



conn = sqlite3.connect("mydatabase.db")
cursor = conn.cursor()
 
cursor.execute("""DROP TABLE IF EXISTS prods""")
cursor.execute("""CREATE TABLE prods (filename text, path text, md5sum text) """)
			


def insertInf(filename,path,sum):		
    sql = ''' INSERT INTO prods(filename,path,md5sum) VALUES(?,?,?) '''
    file=(filename,path,sum)
    cursor.execute(sql, file)
    


def downl(url,name):
    username='serhiizelenyi'
    password = 'RiverFlows44'
    password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, url, username, password)
    handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
    opener = urllib.request.build_opener(handler)
    opener.open(url)
    urllib.request.install_opener(opener)
    urllib.request.urlretrieve(url, name)
    
def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def FilesInf(path):
    for r, d, f in os.walk(path):
        for file in f:
            try:
                insertInf(file, os.path.join(r, file), md5(os.path.join(r, file)))
            except Exception as e:
                print(str(e))
                break


def unzip(name):
    with ZipFile(name+".zip", 'r') as zipObj:
        zipObj.extractall(name)



timetext = ""
txt = open("timerange.txt","w+")
beginpoint = datetime.datetime.now()
endpoint = datetime.datetime.now()-datetime.timedelta(days=4)
timetext = "FROM "+str(beginpoint)+" TO " + str(endpoint)
txt.write(timetext)
txt.close()

url = 'https://scihub.copernicus.eu/dhus/search?q=beginposition:%5bNOW-4DAY%20TO%20NOW%5d%20'

downl(url, 'prods.xml')

mytree = ET.parse('prods.xml')
myroot = mytree.getroot()
i=0
for entry in myroot.findall('{http://www.w3.org/2005/Atom}entry'):
    i=i+1
ff = random.randrange(0,i-1,1)
sf = random.randrange(0,i-1,1)
tf = random.randrange(0,i-1,1)
if sf == ff or sf == tf:
    sf = random.randrange(0,i-1,1)
if tf == ff or tf == sf:
    tf = random.randrange(0,i-1,1)

#print(i,ff,sf,tf)
i=0
links = []
names = []
for entry in myroot.findall('{http://www.w3.org/2005/Atom}entry'):
    if i==ff or i==sf or i==tf:
        links.append(entry[1].attrib['href'])
        for str in entry.findall('{http://www.w3.org/2005/Atom}str'):
            if str.attrib['name'] == 'filename':
                names.append(str.text)
    i=i+1
#print(names,links)


print("Downloading a files")
downl(links[0], names[0]+".zip")
downl(links[1], names[1]+".zip")
downl(links[2], names[2]+".zip")

try:
   print(md5(names[0]+".zip") == md5(names[0]+".zip"))
except Exception as e:
    print(str(e))
    quit()
try:
    print(md5(names[1]+".zip") == md5(names[1]+".zip"))
except Exception as e:
    print(str(e))
    quit()
try:
    print(md5(names[2]+".zip") == md5(names[2]+".zip"))
except Exception as e:
    print(str(e))
    quit()

print("Unpacking")
unzip(names[0])
unzip(names[1])
unzip(names[2])
print("Base filling")
FilesInf(names[0]+"/"+names[0]+"/")
FilesInf(names[1]+"/"+names[1]+"/")
FilesInf(names[2]+"/"+names[2]+"/")


cursor.execute("SELECT * FROM prods")	
rows = cursor.fetchall()
#print(rows[1])
columnsname=('filename','path','md5sum')
with open('result.csv', 'w') as writeFile:
    writer = csv.writer(writeFile)
    writer.writerow(columnsname)
    writer.writerows(rows)
writeFile.close()



print("Program complited")