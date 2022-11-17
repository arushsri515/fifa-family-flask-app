from flask import Flask, render_template, request, jsonify
import psycopg2
import psycopg2.extras
import re


def takeGroup(lst):
    return lst[3]

app = Flask(__name__)


@app.route('/')
def index():
    database = "postgres"
    user = "postgres"
    password = "Unknowndoctor5"
    conn = psycopg2.connect(database=database, 
                                    user=user, 
                                    password=password, 
                                    host = "fifa-comp.c7h7ikseecbs.us-east-1.rds.amazonaws.com", 
                                    port = "5432")
    cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM public.\"PLAYERS\" ORDER BY \"Rank\" ASC")
    results = cur.fetchall()
    results = [dict(row) for row in results]
    print(results)
    for i in results:
        i['PreviousRank'] = int(i['PreviousRank'])
        i['RankDifferential'] = abs(i['PreviousRank'] - i['Rank'])
        if i['PreviousRank'] - i['Rank'] < 0:
            i['color'] = 'danger'
            i['arrow'] = 'down'
        else:
            i['color'] = 'success'
            i['arrow'] = 'up'
        
    return render_template('index.html', data=results)

@app.route('/makepredictions')
def predictions():
    database = "postgres"
    user = "postgres"
    password = "Unknowndoctor5"
    conn = psycopg2.connect(database=database, 
                                    user=user, 
                                    password=password, 
                                    host = "fifa-comp.c7h7ikseecbs.us-east-1.rds.amazonaws.com", 
                                    port = "5432")
    cur = conn.cursor()
    cur.execute("SELECT \"Match\" FROM public.\"PREDICTIONS\"")
    results = cur.fetchall()
    matches = [row[0] for row in results]
    print(matches)
    print("\n")
    matchqas = []
    groups = {"Group A" : ["Qatar", "Ecuador", "Senegal", "Netherlands"],
              "Group B" : ["England", "Iran", "USA", "Wales"],
              "Group C" : ["Argentina", "Saudi Arabia", "Mexico", "Poland"],
              "Group D" : ["France", "Australia", "Denmark", "Tunisia"],
              "Group E" : ["Spain", "Costa Rica", "Germany", "Japan"],
              "Group F" : ["Belgium", "Canada", "Morocco", "Croatia"],
              "Group G" : ["Brazil", "Serbia", "Switzerland", "Cameroon"],
              "Group H" : ["Portugal", "Ghana", "Uruguay", "South Korea"]}
    for match in matches:
        print(match)
        if match[0]!="G":
            continue
        temp1 = re.split(" vs ", match)
        team1 = re.split(": ", temp1[0])[1]
        team2 = re.split(" ", temp1[1])[0]
        print(team1)
        print(team2)
        for key,value in groups.items():
            if team1 in value:
                group = key
        print(team1 + " : " + group)
        match = re.sub('Group [A-H]', group, match)
        print(match)
        matchqas.append([match,team1,team2,group])
    matchqas.sort(key=takeGroup)
    index = 0
    for matchq in matchqas:
        matchq.insert(3, index)
        index+=1
    print(matchqas)
    return render_template('predictions.html',matchqas=matchqas)

@app.route('/pushpredictions', methods=["POST","GET"])
def pushPredictions():
    database = "postgres"
    user = "postgres"
    password = "Unknowndoctor5"
    data = dict(request.get_json())
    print(data)
    conn = psycopg2.connect(database=database, 
                                    user=user, 
                                    password=password, 
                                    host = "fifa-comp.c7h7ikseecbs.us-east-1.rds.amazonaws.com", 
                                    port = "5432")
    cur = conn.cursor()
    for item in data.keys():
        if item!='name':
            cur.execute(f'''UPDATE public."PREDICTIONS"
                                SET "{data['name']}"=%s
                                WHERE "Match"=%s;''',(data[item],item))
            conn.commit()
    conn.commit()
    return jsonify({"success" : 200})

if __name__=='__main__':
    app.run(debug=True, port=8080)

