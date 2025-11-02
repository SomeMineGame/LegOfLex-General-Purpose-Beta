import json, datetime, json, discord, os, shutil
from discord import app_commands
di = discord.Interaction

class files():
    async def add_files(Dir: str, path: str):
        os.makedirs(f"{path}/Charities")
        open(f"{path}/banklog.txt", "x")
        open(f"{path}/prisonlog.txt", "x")
        open(f"{path}/rconlog.txt", "x")
        open(f"{path}/shoplog.txt", "x")
        open(f"{path}/maindb.json", "x")
        with open(f"{path}/maindb.json", "r+") as f:
            data = {"Misc Data": {"day": 0, "inflation": 0, "ip": {"JIP": "Not Yet Setup", "BIP": "Not Yet Setup", "BP": 0}, "lotto": 0, "tax": 0}, "User Data": {}}
            json.dump(data, f)
            f.truncate()
        open(f"{path}/nations.json", "x")
        with open(f"{path}/nations.json", "r+") as f:
            data = {}
            json.dump(data, f)
            f.truncate()
        open(f'{Dir}/web/css/data.json', 'x')
        with open(f'{Dir}/web/css/data.json', 'r+') as d:
            data = {"Misc Data": {"day": 0, "inflation": 0, "ip": {"JIP": "No", "BIP": "No", "BP": 0}, "lotto": 0, "tax": 0}, "User Data": {}}
            json.dump(data, d)
            d.truncate()
            
    async def archive_files(Dir: str, srvfolder: str, i: discord.Interaction, resetname: str = None):
        if not resetname:
            dt = datetime.datetime.now()
            resetname = dt.strftime("%B %d, %Y")
        try:
            oldfolder = f"{srvfolder}/ResetData/{resetname}"
            os.makedirs(oldfolder)
        except:
            await i.response.send_message("You can only use a name one time and symbols aren't allowed. You can try to add numbers at the end.")
            return False
        for (root, dirs, files) in os.walk(f"{srvfolder}"):
            for file in files:
                shutil.move(f"{srvfolder}/{file}", f"{oldfolder}")
            for dir in dirs:
                if f"{srvfolder}/{dir}" != f"{srvfolder}/ResetData":
                    shutil.move(f"{srvfolder}/{dir}", f"{oldfolder}")
            break
        os.remove(f'{Dir}/web/css/data.json')

class save():
    async def save_info(Dir:str, srvfolder: str, blog: str=None, plog: str=None, rlog: str=None, slog:str=None, db: dict=None, nations: dict=None):
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
        if nations != None:
            with open(f'{srvfolder}/nations.json', 'r+') as f:
                f.seek(0)
                json.dump(nations, f)
                f.truncate()    
            
    async def change_inflation(Dir: str, srvfolder: str, db: dict):
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
    async def get_info(i: di, Dir: str):
        server, userid, name = i.guild.id, str(i.user.id), i.user.nick
        srvfolder = f"{Dir}/discord/{server}"
        with open(f"{srvfolder}/maindb.json", 'r+') as f:
            db = json.load(f)
        if not name:
            name = i.user.display_name
        return server, userid, name, srvfolder, db

    async def get_user_info(user: discord.Member):
        playerid, username = str(user.id), user.nick
        if not username:
            username = user.display_name
        return playerid, username
    
    class prices():
        async def data(Dir:str):
            with open(f"{Dir}/discord/Prices.json", "r+") as f:
                return json.load(f)
        
        async def ListFormat(Dir:str):
            return list((await load.prices.data(Dir)).keys())

async def load_prices_AutoComplete(interaction: di, current: str):
    items = []
    for item in await load.prices.ListFormat(os.getcwd()):
        if current.title().strip() in item[:len(current.strip())]:
            items.append(app_commands.Choice(name=item, value=item))
    return items[:10]