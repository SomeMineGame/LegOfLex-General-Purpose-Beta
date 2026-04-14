import json, datetime, json, discord, os, shutil, math
import discord_extras.bot as bt
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
        open(f"{path}/demand_price.json", "x")
        os.makedirs(f"{path}/Price_Data")
        with open(f"{Dir}/discord/Prices.json", "r") as f:
            prices = json.load(f)
            for price in prices:
                open(f"{path}/Price_Data/")
            
    async def archive_files(Dir: str, srvfolder: str, i: discord.Interaction, resetname: str = None):
        """Creates an archive of the provided Discord server. Retrieves the server from srvfolder.

        Args:
            Dir (str): The root directory of the main bot file.
            srvfolder (str): The path of the target Discord folder.
            i (discord.Interaction): The Discord interaction passed from the command.
            resetname (str, optional): Name of the archive. Defaults to the timestamp if None is provided.

        Does not return anything.
        """
        if not resetname:
            dt = datetime.datetime.now()
            resetname = dt.strftime("%B-%d-%Y")
        resetname = resetname.lower()
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
    async def save_info(Dir:str, srvfolder: str, db: dict, blog: str=None, plog: str=None, rlog: str=None, slog:str=None, nations: dict=None):
        """Saves modified info for a Discord server. Only saves to the files which are not None when calling.

        Args:
            Dir (str): The root directory of the main bot file.
            srvfolder (str): The path of the target Discord folder.
            db (dict): The updated database dictionary.
            blog (str, optional): A string to append to the end of the bank log.
                                Defaults to None.
            plog (str, optional): A string to append to the end of the prison log.
                                Defaults to None.
            rlog (str, optional): A string to append to the end of the rcon log.
                                Defaults to None.
            slog (str, optional): A string to append to the end of the shop log.
                                Defaults to None.
            nations (dict, optional): An updated nations dictionary.
                                Defaults to None.
                                
        Does not return anything.
        """
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
        """Updates the inflation of the server.

        Args:
            str: The root directory of the main bot file.
            str: The path of the target Discord folder.
            dict: The updated database dictionary.
            
        Does not return anything.
        """
        totalmoney, contributors = db["Misc Data"]['tax'], 1
        for player in db['User Data']:
            money = db['User Data'][player]['economy']['money']
            bank = db['User Data'][player]['economy']['bank']
            net = bank*0.75 + money
            if net == 0:
                pass
            else:
                totalmoney += net
                contributors += 1
        if totalmoney == 0:
            averagebal = 0
        else:
            averagebal=round(totalmoney/(contributors),4)
        if averagebal >= 0:
            inflation = round((averagebal/125000)**.25,4)
        else:
            inflation = 0
        if inflation <= .01:
            inflation = .01
        db['Misc Data']['inflation'] = inflation
        await save.save_info(Dir, srvfolder, blog=f"Inflation rate changed to {round(inflation*100,2):,}%", db=db)
        
    async def change_demand(Dir: str, srvfolder: str, username: str, item: str, amount: int):
        """Updates the demand of an item.

        Args:
            str: The root directory of the main bot file.
            str: The path of the target Discord folder.
            str: The name of the item to update.
            int: The amount of the item.
            
        Does not return anything.
        """
        dt = datetime.datetime.now()
        ty,tm,td,th = str(dt.year),str(dt.month),str(dt.day),str(dt.hour)
        ##############################
        ### PART ONE - PLAYER SIDE ###
        ##############################
        if not os.path.exists(f"{srvfolder}/PriceData/Players/{username}/{item[0]}/{item.replace(' ', "_")}.json"):
            try:
                os.makedirs(f"{srvfolder}/PriceData/Players/{username}/{item[0]}")
            except:
                pass
            open(f"{srvfolder}/PriceData/Players/{username}/{item[0]}/{item.replace(' ', "_")}.json", "x")
            with open(f"{srvfolder}/PriceData/Players/{username}/{item[0]}/{item.replace(' ', "_")}.json", "r+") as f:
                f.seek(0)
                f.write('{"History": {"AllTime": {"Bought": 0, "Sold": 0}}}')
                f.truncate()
                f.close()
        with open(f"{srvfolder}/PriceData/Players/{username}/{item[0]}/{item.replace(' ', "_")}.json", "r+") as f:
            data = json.load(f)
            history=data["History"]
        if not ty in history:
            history[ty]={"Totals": {"Bought": 0, "Sold": 0}, tm: {"Totals": {"Bought": 0, "Sold": 0}, td: {"Totals": {"Bought": 0, "Sold": 0}, th: {"Totals": {"Bought": 0, "Sold": 0}}}}}
        elif not tm in history[ty]:
            history[ty][tm]={"Totals": {"Bought": 0, "Sold": 0}, td: {"Totals": {"Bought": 0, "Sold": 0}, th: {"Totals": {"Bought": 0, "Sold": 0}}}}
        elif not td in history[ty][tm]:
            history[ty][tm][td]={"Totals": {"Bought": 0, "Sold": 0}, th: {"Totals": {"Bought": 0, "Sold": 0}}}
        elif not th in history[ty][tm][td]:
            history[ty][tm][td][th]={"Totals": {"Bought": 0, "Sold": 0}}
        if amount > 0:
            history["AllTime"]["Bought"] += amount
            history[ty]["Totals"]["Bought"] += amount
            history[ty][tm]["Totals"]["Bought"] += amount
            history[ty][tm][td]["Totals"]["Bought"] += amount
            history[ty][tm][td][th]["Totals"]["Bought"] += amount
        if amount < 0:
            history["AllTime"]["Sold"] -= amount
            history[ty]["Totals"]["Sold"] -= amount
            history[ty][tm]["Totals"]["Sold"] -= amount
            history[ty][tm][td]["Totals"]["Sold"] -= amount
            history[ty][tm][td][th]["Totals"]["Sold"] -= amount
        with open(f"{srvfolder}/PriceData/Players/{username}/{item[0]}/{item.replace(' ', "_")}.json", "r+") as f:
            data["History"]=history
            f.seek(0)
            json.dump(data,f)
            f.truncate()
            f.close()
        ##############################    
        ### PART TWO - SERVER SIDE ###
        ##############################
        if not os.path.exists(f"{srvfolder}/PriceData/Server/{item[0]}/{item.replace(' ', "_")}.json"):
            try:
                os.makedirs(f"{srvfolder}/PriceData/Server/{item[0]}")
            except:
                pass
            open(f"{srvfolder}/PriceData/Server/{item[0]}/{item.replace(' ', "_")}.json", "x")
            with open(f"{srvfolder}/PriceData/Server/{item[0]}/{item.replace(' ', "_")}.json", "r+") as f:
                f.seek(0)
                f.write('{"History": {"AllTime": {"Bought": 0, "Sold": 0}}}')
                f.truncate()
                f.close()
        with open(f"{srvfolder}/PriceData/Server/{item[0]}/{item.replace(' ', "_")}.json", "r+") as f:
            data = json.load(f)
            history=data["History"]
        if not ty in history:
            history[ty]={"Totals": {"Bought": 0, "Sold": 0}, tm: {"Totals": {"Bought": 0, "Sold": 0}, td: {"Totals": {"Bought": 0, "Sold": 0}, th: {"Totals": {"Bought": 0, "Sold": 0}}}}}
        elif not tm in history[ty]:
            history[ty][tm]={"Totals": {"Bought": 0, "Sold": 0}, td: {"Totals": {"Bought": 0, "Sold": 0}, th: {"Totals": {"Bought": 0, "Sold": 0}}}}
        elif not td in history[ty][tm]:
            history[ty][tm][td]={"Totals": {"Bought": 0, "Sold": 0}, th: {"Totals": {"Bought": 0, "Sold": 0}}}
        elif not th in history[ty][tm][td]:
            history[ty][tm][td][th]={"Totals": {"Bought": 0, "Sold": 0}}
        if amount > 0:
            history["AllTime"]["Bought"] += amount
            history[ty]["Totals"]["Bought"] += amount
            history[ty][tm]["Totals"]["Bought"] += amount
            history[ty][tm][td]["Totals"]["Bought"] += amount
            history[ty][tm][td][th]["Totals"]["Bought"] += amount
        if amount < 0:
            history["AllTime"]["Sold"] -= amount
            history[ty]["Totals"]["Sold"] -= amount
            history[ty][tm]["Totals"]["Sold"] -= amount
            history[ty][tm][td]["Totals"]["Sold"] -= amount
            history[ty][tm][td][th]["Totals"]["Sold"] -= amount
        h_bought, h_sold = 0, 0
        for day in range(0, 30):
            pdt = dt - datetime.timedelta(days=day)
            py,pm,pd = pdt.year,pdt.month,pdt.day
            for hr in range(0, 24):
                try:
                    h_bought+=history[str(py)][str(pm)][str(pd)][str(hr)]['Totals']['Bought']
                    h_sold+=history[str(py)][str(pm)][str(pd)][str(hr)]['Totals']['Sold']
                except:
                    pass
        if h_bought == 0 and h_sold == 0:
            ratio = 1
        elif h_bought == 0:
            ratio = 1/(h_sold+1)
        elif h_sold == 0:
            ratio = h_bought+1
        else:
            ratio = h_bought/h_sold
        prices = await load.prices.data(Dir, item[0].capitalize())
        influence = prices[item]['influence']
        if ratio > 1:
            # Determines how many items to double the cost (rate of change slows around here, 10 is min)
            # Exponential but diminishing.
            demand = math.copysign(1,ratio-1)*math.sqrt(abs(ratio-1)/(influence*(ratio**(1/3)))**0.75)+1
        else:
            # Always 10 when selling
            # Exponential but diminishing. Lower limit of 0.01
            demand = ratio**(1-10**(-(((3100-influence)/50000)**0.75)))
        print(demand)
        if demand < 0.01:
            demand = 0.01
        else:
            demand = round(demand,2)
        with open(f"{srvfolder}/PriceData/Server/{item[0]}/{item.replace(' ', "_")}.json", "r+") as f:
            data["History"]=history
            f.seek(0)
            json.dump(data,f)
            f.truncate()
            f.close()
        with open(f"{srvfolder}/demand_price.json", 'r+') as f:
            data = json.load(f)
            data[item] = demand
            f.seek(0)
            json.dump(data, f)
            f.truncate()
            f.close()
        
class load():   
    async def get_info(i: di, Dir: str):
        """Gets basic info for a Discord server, the user who initiated the
            command, and the database.

        Args:
            i (di): The Discord interaction passed from the command.
            Dir (str): The root directory of the main bot file.

        Returns:
            str: The id of the user who initiated the command.
                Formatted for use in the database.
            str: The nickname of of the user who initiated the command.
            str: The path of the current Discord folder.
            dict: The current database dictionary.
        """
        server, userid, name = i.guild.id, str(i.user.id), i.user.nick
        srvfolder = f"{Dir}/discord/{server}"
        with open(f"{srvfolder}/maindb.json", 'r+') as f:
            db = json.load(f)
        if not name:
            name = i.user.display_name
        return userid, name, srvfolder, db

    async def get_user_info(user: discord.Member):
        """Gets the ID and username of a Discord user.

        Args:
            user (discord.Member): The Discord member.

        Returns:
            str: The id of the user.
            str: The username of the user.
        """
        playerid, username = str(user.id), user.nick
        if not username:
            username = user.display_name
        return playerid, username
    
    class prices():
        async def data(Dir:str, Letter:str):
            """Gets the full prices dictionary for a letter.

            Args:
                Dir (str): The root directory of the main bot file.

            Returns:
                dict: The prices dictionary of a letter.
            """
            with open(f"{Dir}/discord/Prices/Prices_{Letter}.json", "r+") as f:
                return json.load(f)
        
        async def ListFormat(Dir:str, Letter: str):
            """Gets a list of all items in the prices file.

            Args:
                Dir (str): The root directory of the main bot file.

            Returns:
                list: All items in the prices file.
            """
            return list((await load.prices.data(Dir, Letter)).keys())
    
        async def get_price(Dir: str, srvfolder: str, db: dict, item:str, mode: str, void: bool):
            if void == True:
                # will change when shop is added
                voidb = 1
                voids = 1
            else:
                voidb, voids = 1, 1
            inflation = db['Misc Data']['inflation']
            with open(f"{srvfolder}/demand_price.json") as f:
                demands = json.load(f)
            demand = demands[item]
            prices = await load.prices.data(Dir, item[0].capitalize())
            cost = prices[item.title()]['basecost']
            if mode == 1 or mode == 2:
                if not os.path.exists(f"{srvfolder}/PriceData/Server/{item[0]}/{item.replace(' ', "_")}.json"):
                    ratio = 1
                else:
                    with open(f"{srvfolder}/PriceData/Server/{item[0]}/{item.replace(' ', "_")}.json", "r+") as f:
                        data = json.load(f)
                        history=data["History"]
                    dt = datetime.datetime.now()
                    h_bought, h_sold = 0, 0
                    for day in range(0, 30):
                        pdt = dt - datetime.timedelta(days=day)
                        py,pm,pd = pdt.year,pdt.month,pdt.day
                        for hr in range(0, 24):
                            try:
                                h_bought+=history[str(py)][str(pm)][str(pd)][str(hr)]['Totals']['Bought']
                                h_sold+=history[str(py)][str(pm)][str(pd)][str(hr)]['Totals']['Sold']
                            except:
                                pass
                    if h_bought == 0 and h_sold == 0:
                        ratio = 1
                    elif h_bought == 0:
                        ratio = 1/(h_sold+1)
                    elif h_sold == 0:
                        ratio = h_bought+1
                    else:
                        ratio = h_bought/h_sold
                if demand >= 1:
                    sdemand = demand/(demand**0.84+(math.copysign(1,abs(ratio-1))-1))
                else:
                    sdemand = demand
                sfactors = inflation*cost*sdemand
                stax = sfactors*0.95
            bfactors = inflation*cost*demand
            btax = bfactors*1.07
            if mode == 0:
                return btax*voidb, bfactors*0.07
            elif mode == 1:
                return stax*voids, sfactors*0.05
            elif mode == 2:
                return btax, btax*voidb, stax, stax*voids
        
    class charity():
        async def charities(Dir:str):
            """Returns a list of all charities.

            Args:
                Dir (str): The root directory of the main bot file.

            Returns:
                list: All charities.
            """
            for (_, _, files) in os.walk(Dir):
                return files
        
    async def load_charity(srvfolder, cname):
        with open(f"{srvfolder}/Charities/{cname}.json", "r+") as f:
            data = json.load(f)
            return data

async def load_prices_AutoComplete(interaction: di, current: str):
    items = []
    if len(current) > 0:
        letter = current[0].capitalize()
    else:
        letter = 'A'
    for item in await load.prices.ListFormat(os.getcwd(), letter):
        if current.title().strip() in item[:len(current.strip())]:
            items.append(app_commands.Choice(name=item, value=item))
    return items[:10]

async def charity_action_Autocomplete(interaction: di, current: str):
    actions = ["create", "donate", "edit", "give", "info", "list", "pause", "remove", "resume"]
    matches = []
    for action in actions:
        if current.lower().strip() in action[:len(current.strip())]:
            matches.append(app_commands.Choice(name=action, value=action))
    return matches

async def load_charity_AutoComplete(interaction: di, current: str):
    charities = []
    Dir = f"{os.getcwd()}/discord/{interaction.guild_id}/Charities"
    for charity in await load.charity.charities(Dir):
        if current.title().strip() in charity[:-5][:len(current.strip())]:
            charities.append(app_commands.Choice(name=charity, value=charity))
    return charities[:10]

async def charity_recipient_AutoComplete(interaction: di, current: str):
    recipients = []
    charities = await load_charity_AutoComplete()
    with open(f"{os.getcwd()}/discord/{interaction.guild_id}/Charities", 'r') as f:
        data = json.load(f)
    for charity in charities:
        recipients.append(f"{charity} - C")
    for id in data['User Data']:
        member = interaction.guild.get_member(id)
        name = member.nick
        if not name:
            name = member.display_name
        recipients.append(f"{name} - P")
    recipients.sort()
    return recipients[:10]
