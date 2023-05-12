#project: p5
#submitter: kmconrad3
#partner: none
#hours: 20

import sys, time, csv, netaddr, json, re, pyproj
from zipfile import ZipFile, ZIP_DEFLATED
from shapely.geometry import box
from geopandas import GeoDataFrame as gdf
import pandas as pd
import geopandas as gpd



colors={}
jsondata=[]
df = pd.read_csv('ip2location.csv')
index = 0

def subs(arg):
    arg = re.sub("[a-z]","0", arg)
    return arg

def ipnums(arg):
    arg = int(netaddr.IPAddress(arg))
    return arg

def colorassign(name):
    if name in colors:
        instance = int(colors[name])
        if instance>=1:
            if instance<1000:
                return "orange"
        if instance>=1000:
            return "red"
    else:
        return "lightgray"

    

def rangloc(argg):
    global df
    global index
    arg = int(netaddr.IPAddress(argg))
    timer=time.time()
    while True:
        if arg> int(df.at[index,"high"]):
            index+=1
        elif arg< int(df.at[index,"low"]):
            index-=1
        else:
            timerr=(time.time() - timer)*10
            return {"ip":argg,"int_ip":arg, "region":df.at[index,"region"], "ms":timerr}
    
def writezip(zips,newz):
    with ZipFile(zips) as zf:
        with zf.open("rows.csv") as f:
             dff = pd.read_csv(f)
        dff["ip"] = dff["ip"].apply(subs)
        dff["ip"] = dff["ip"].apply(ipnums)
        dff = dff.sort_values("ip")
        dff["region"] = dff["ip"].apply(lambda x: rangloc(x)["region"])
    with ZipFile(newz, "w", compression=ZIP_DEFLATED) as zf:
         with zf.open("rows.csv", "w") as f:
                dff.to_csv(f, index=False)
                       
def zipcode(zipfname):
    correctzips=[]
    with ZipFile(zipfname) as zf:
        for info in zf.infolist():
            with zf.open(info.filename) as f:
                content = str(f.read())
            zips=re.findall('(NY|CA|WI|IL)\s([0-9]{5}-[0-9]{4}|[0-9]{5})', content)
            if len(zips)!=0:
                for zi in zips:
                    correctzips.append(zi[1])
    return list(set(correctzips))

def geomap(idd):
    with ZipFile("server_log2.zip") as zf:
        with zf.open("rows.csv") as f:
             dff = pd.read_csv(f)
    for index in range(len(dff)):
        if dff.at[index,"region"] in list(colors.keys()):
            colors[dff.at[index,"region"]]+=1
        else:
            colors[dff.at[index,"region"]]=1
    crs = pyproj.CRS.from_epsg(idd)
    b = box(crs.area_of_use.west, crs.area_of_use.south, crs.area_of_use.east, crs.area_of_use.north)
    path = gpd.datasets.get_path("naturalearth_lowres")
    df = gpd.read_file(path)
    df["colorname"] = df["name"].apply(colorassign)
    df["geometry"]=df.intersection(b)
    df=df[~df.is_empty]
    return df.to_crs(crs).plot(figsize=(8,8), color=df["colorname"], edgecolor="black")
        
                       
                       
def main():
    if len(sys.argv) < 2:
        print("usage: main.py <command> args...")
  
    elif sys.argv[1] == "ip_check":
        global jsondata
        ips = sys.argv[2:]
        for i in ips:
            jsondata.append(rangloc(i))
        jsyntax=str(jsondata).replace("\'", "\"")
        print(json.dumps(json.loads(str(jsyntax)), indent=3))
    
    elif sys.argv[1] == "region":
        zips = sys.argv[2]
        newz = sys.argv[3]
        writezip(zips,newz)
    
    elif sys.argv[1] == "zipcode":
        zipfname = sys.argv[2]
        for z in zipcode(zipfname):
            print(z)
            
    elif sys.argv[1] == "geo":
        img = sys.argv[3]
        idd = sys.argv[2]
        ax = geomap(idd)
        ax.get_figure().savefig(img, format="svg")
        
    else:
        print("unknown command: "+sys.argv[1])

        
if __name__ == '__main__':
     main()
        