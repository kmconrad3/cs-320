#project: p4
#submitter: kmconrad3
#partner: none
#hours: 15

# my data is from Kaggle, its rows are split up by each lyric line in Taylor Swift's Reputation album
import pandas as pd
import re, csv, matplotlib, itertools
import matplotlib.pyplot as plt
matplotlib.use('Agg')
from flask import Flask, request, jsonify, Response
from io import BytesIO


app = Flask(__name__)
subcount=0
acount=0
bcount=0
viscount=0
df=pd.read_csv("main.csv")

@app.route('/')
def home():
    global acount
    global bcount
    global viscount
    with open("index.html") as f:
        html = f.read()
    viscount+=1
    if (viscount<=10):
        if (viscount%2==1):
            html = html.replace("QUERYSTRING", "?from=A")
            html = html.replace("REPLACECOLOR", "blue")
        if (viscount%2==0):
            html = html.replace("QUERYSTRING", "?from=B")
            html = html.replace("REPLACECOLOR", "orange")
    else:
        if (acount>bcount):
            html = html.replace("QUERYSTRING", "?from=A")
            html = html.replace("REPLACECOLOR", "blue")
        else:
            html = html.replace("QUERYSTRING", "?from=B")
            html = html.replace("REPLACECOLOR", "orange")
    return html
  
    
@app.route('/donate.html')
def donate():
    try:
        ff=request.args["from"]
        global acount
        global bcount
        if ff=="A":
            acount+=1
        if ff=="B":
            bcount+=1
    except:
        pass
    with open("donate.html") as f:
        html = f.read()
    return html


@app.route('/browse.html')
def browse():
    global df
    df.to_html() 
    return "<html>{}<html>".format("<h1> Browse\n </h1>" + df.to_html())


@app.route('/email', methods=["POST"])
def email():
    global subcount
    email = str(request.data, "utf-8")
    if re.match(r"\w+@\w+[.]\w{3}", email): # or use (edu|com|net|org|gov)
        with open("emails.txt", "a") as f: # opens file in append mode
            f.write(email + "\n")
        subcount+=1
        return jsonify(f"thanks, you're subscriber number {subcount} !")
    return jsonify(f"please be careful, you entered an invalid email address!")



@app.route("/dashb1.svg")
def plot_svg():
    unqtitl={}
    for titl in df["track_title"]:
        if titl in unqtitl.keys():
            unqtitl[titl]+=1
        else:
            unqtitl[titl]=1
    fig, ax = plt.subplots()
    ax.bar(x=list(unqtitl.keys()), height=list(unqtitl.values()))
    ax.set_title("Reputation Album's Songs' Lyric Line Count")
    ax.set_xlabel("Song title")
    ax.set_xticklabels(labels=list(unqtitl.keys()), rotation=90)
    ax.set_ylabel("Number of lyric lines")
    f = BytesIO()
    ax.get_figure().savefig(f, format="svg", bbox_inches="tight")
    plt.close(fig)
    return Response(f.getvalue(),
                    headers={"Content-Type": "image/svg+xml"})


@app.route('/dashb1_quer.svg')
def plotquer_svg():
    fig, ax = plt.subplots()
    ff = request.args["length"]
    lenline={}
    for titl in df["track_title"]:
        if titl not in lenline.keys():
            lenline[titl]=None
    for i in range(len(df)):
            if lenline[df.iloc[i]["track_title"]]==None:
                lenline[df.iloc[i]["track_title"]]=len(df.iloc[i]["lyric"])
    if ff=="max":
            if len(df.iloc[i]["lyric"])>lenline[df.iloc[i]["track_title"]]:
                lenline[df.iloc[i]["track_title"]]=len(df.iloc[i]["lyric"])
    else:
            if len(df.iloc[i]["lyric"])<lenline[df.iloc[i]["track_title"]]:
                lenline[df.iloc[i]["track_title"]]=len(df.iloc[i]["lyric"])
    ax.scatter(x=list(lenline.keys()), y=list(lenline.values()), c="pink")
    ax.set_title(f"Each song's {ff} lyric length")
    ax.set_xlabel("Song title")
    ax.set_xticklabels(labels=list(lenline.keys()), rotation=90)
    ax.set_ylabel("Number of characters per lines")
    f = BytesIO()
    ax.get_figure().savefig(f, format="svg", bbox_inches="tight")
    plt.close(fig)
    return Response(f.getvalue(),
                    headers={"Content-Type": "image/svg+xml"})  
 
    
@app.route('/dashboard_2.svg')
def plot2_svg():
    fig, ax = plt.subplots()
    wordc={}
    for i in range(len(df)):
        if df.iloc[i]["track_title"] == "Delicate":
              for word in df.iloc[i]["lyric"].split():
                    if word not in wordc.keys():
                        wordc[word]=1
                    else:
                        wordc[word]+=1              
    wordc=dict(itertools.islice((dict(sorted(wordc.items(), key=lambda x:x[1], reverse=True))).items(), 6))
    ax.pie(wordc.values(), labels=wordc.keys(), autopct='%1.1f%%', startangle=90)
    ax.set_title("Percentage of words used most in Song Delicate")
    plt.legend()
    f = BytesIO()
    ax.get_figure().savefig(f, format="svg", bbox_inches="tight")
    plt.close(fig)
    return Response(f.getvalue(),
                    headers={"Content-Type": "image/svg+xml"})  


    
@app.route('/robots.txt')
def robo():
    return Response("\n".join(["User-agent: busyspider","Disallow: /", "User-agent: hungrycaterpillar", "Disallow: /browse.html"]), headers={'Content-Type': "text/plain"})
                                       

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=False) # don't change this line!
# NOTE: app.run never returns (it runs forever, unless you kill the process [Ctrl + C])
# So don't define any functions after the app.run call, bc it'll never get that far.
