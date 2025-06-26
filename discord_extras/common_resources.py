import json, asyncrcon, datetime, json, discord

class save():
    async def save_info(Dir, srvfolder, blog=None, plog=None, rlog=None, slog=None, db=None):
        dt = datetime.datetime.now()
        dtprint = dt.strftime("%A, %B %d, %Y at %I:%M:%S %p")
        if blog != None:
            with open(f'{srvfolder}/banklog.txt', 'a') as f:
                f.write(f"{dtprint}: {blog}\n")
        if plog != None:
            with open(f'{srvfolder}/prisonlog.txt', 'a') as f:
                f.write(f"{dtprint}: {plog}\n")
        if rlog != None:
            with open(f'{srvfolder}/rconlog.txt', 'a') as f:
                f.write(f"{dtprint}: {rlog}\n")
        if slog != None:
            with open(f'{srvfolder}/shoplog.txt', 'a') as f:
                f.write(f"{dtprint}: {slog}\n")
        if db != None:
            with open(f'{srvfolder}/maindb.json', 'r+') as f:
                f.seek(0)
                json.dump(db, f)
                f.truncate()
            with open(f'{Dir}/web/css/data.json', 'r+') as d:
                yo = db
                yo["Misc Data"]["ip"] = {"No": "IP"}
                d.seek(0)
                json.dump(yo, d)
                d.truncate()
            
    async def change_inflation(Dir, srvfolder, db):
        datalist = []
        for player in db['User Data']:
            datalist.append(db['User Data'][player]['economy']['money'])
        global temp
        global totalmoney
        global emptyuser
        temp, totalmoney, emptyuser = 0, 0, 0
        for item in datalist:
            try:
                if datalist[temp] == 0:
                    emptyuser += 1
                else:
                    totalmoney=totalmoney+datalist[temp]
                temp=temp+1
            except:
                pass
        if totalmoney == 0:
            averagebal = 0
        else:
            averagebal=round(totalmoney/(len(datalist)-emptyuser),4)
        if averagebal >= 0:
            inflation = round((averagebal/50000)**.25,4)
        else:
            inflation = 0
        if inflation <= .01:
            inflation = .01
        db['Misc Data']['inflation'] = inflation
        await save.save_info(Dir, srvfolder, blog=f"Inflation rate changed to {round(inflation*100,2):,}%", db=db)
        
class load():   
    async def get_info(i, Dir):
        server, userid, name = i.guild.id, str(i.user.id), i.user.nick
        srvfolder = f"{Dir}/discord/{server}"
        with open(f"{srvfolder}/maindb.json", 'r+') as f:
            db = json.load(f)
        if not name:
            name = i.user.display_name
        return server, userid, name, srvfolder, db

    async def get_user_info(user):
        playerid, username = str(user.id), user.nick
        if not username:
            username = user.display_name
        return playerid, username