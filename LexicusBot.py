import os, discord, json, datetime, typing, random, asyncio, minestat, re
import discord_extras.bot as bt
import discord_extras.common_resources as cr
import discord_extras.timers as timers
import discord_extras.nbt_json_utils as nbt_json_utils
import discord_extras.xuid as xuid
from asyncrcon import AsyncRCON
from discord import app_commands
from discord.ext import commands, tasks
from dateutil.relativedelta import relativedelta
from nbtlib import tag, Compound, List

DIR = os.getcwd()
di = discord.Interaction

intents = discord.Intents.all()
intents.members = True
intents.guilds = True

client = discord.Client(intents=intents, help_command=None)
bot = app_commands.CommandTree(client)

AsyncRCON.__init__(AsyncRCON, bt.MC.rcon, bt.MC.password, max_command_retries=1)
rcon = AsyncRCON(bt.MC.rcon, bt.MC.password)

@client.event
async def on_member_join(member: discord.Member):
    role = discord.utils.get(member.guild.roles, name="Applicant")
    await member.add_roles(role)
                            
@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Game(name="Use /help for the wiki!"))
    await rcon.open_connection()
    autoclockout.start()
    checkstat.start()
    print("LOL bot online!")
    
channel = 1407384861680861256
reactiona = "⚠"
reactionb = "🛠"
reactionc = "🖥"
reactiond = "🔔"
    
@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    if payload.channel_id == channel:
        if str(payload.emoji) == reactiona:
            Testing = discord.utils.get(payload.member.guild.roles, name="Testing")
            await payload.member.add_roles(Testing)
        elif str(payload.emoji) == reactionb:
            Builds = discord.utils.get(payload.member.guild.roles, name="Builds")
            await payload.member.add_roles(Builds)
        elif str(payload.emoji) == reactionc:
            Vids = discord.utils.get(payload.member.guild.roles, name="Vids")
            await payload.member.add_roles(Vids)
        elif str(payload.emoji) == reactiond:
            Notices = discord.utils.get(payload.member.guild.roles, name="Notices")
            await payload.member.add_roles(Notices)
    else:
        return
    
@client.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    guild = client.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)
    if payload.channel_id == channel:
        if str(payload.emoji) == reactiona:
            Testing = discord.utils.get(member.guild.roles, name="Testing")
            await member.remove_roles(Testing)
        elif str(payload.emoji) == reactionb:
            Builds = discord.utils.get(member.guild.roles, name="Builds")
            await member.remove_roles(Builds)
        elif str(payload.emoji) == reactionc:
            Vids = discord.utils.get(member.guild.roles, name="Vids")
            await member.remove_roles(Vids)
        elif str(payload.emoji) == Vids:
            Notices = discord.utils.get(member.guild.roles, name="Notices")
            await member.remove_roles(Notices)
    else:
        return
    
@tasks.loop(minutes=5)
async def autoclockout():
    await timers.timers.autoclockout(client, DIR, rcon)
                            
@tasks.loop(seconds=10)
async def checkstat():
    await timers.timers.checkstat(client, DIR, rcon)

#Base Commands
@bot.command(description="Adds your base for others to see")
async def addbase(i: di, x: int, y: int, z: int, dimension: typing.Literal['Overworld', 'Nether', 'The End']):
    server, userid, name, srvfolder, db = await cr.load.get_info(i, DIR) 
    base = db['User Data'][userid]['base']
    if x == 0 and y == 0 and z == 0:
        await i.response.send_message("You can't set your base there.", ephemeral=True)
    elif abs(x) >= 29999984 or y <= -64 or y >= 320 or abs(z) >= 29999984:
        await i.response.send_message("Those coordinates are outside of the current build zone. (±29,999,984, -63/319, ±29,999,984).", ephemeral=True)
    elif base['x'] == 0 and base['y'] == 0 and base['z'] == 0:
        db['User Data'][userid]['base'] = {"x": x, "y": y, "z": z, "dimension": dimension.title()}
        await rcon.command(f'dmarker add icon:house id:{name} label:"{name}\'s Base" x:{x} y:{y} z:{z} world:Lexicus_{dimension.lower().replace(" ", "_")}')
        await cr.save.save_info(DIR, srvfolder, db=db)
        await i.response.send_message(f"Your base cords are now set to `{x} {y} {z}` in the dimension `{dimension.title()}`.", ephemeral=True)
    else:
        await i.response.send_message("You already have a base set up! Use &viewBase to see it, or &editBase to change it.")
        
@bot.command(description="Edits your base location")
async def editbase(i: di, x: int, y: int, z: int, dimension: typing.Literal['Overworld', 'Nether', 'The End']):
    server, userid, name, srvfolder, db = await cr.load.get_info(i, DIR) 
    base = db['User Data'][userid]['base']
    if x == 0 and y == 0 and z == 0:
        await i.response.send_message("You can't set your base there.")
    elif abs(x) >= 29999984 or y <= -64 or y >= 320 or abs(z) >= 29999984:
        await i.response.send_message("Those coordinates are outside of the current build zone. (±29,999,984, -63/319, ±29,999,984).")
    elif base['x'] == 0 and base['y'] == 0 and base['z'] == 0:
        await i.response.send_message(f"You have no base to edit. Add one with `&addBase {x} {y} {z}`!")
    elif base['x'] == x and base['y'] == y and base['z'] == z and dimension.title() == base['dimension']:
        await i.response.send_message("Your base is already set there!")
    else:
        db['User Data'][userid]['base'] = {"x": x, "y": y, "z": z, "dimension": dimension.title()}
        await rcon.command(f'dmarker delete id:{name}')
        await rcon.command(f'dmarker add icon:house id:{name} label:"{name}\'s Base" x:{x} y:{y} z:{z} world:Lexicus_{dimension.lower().replace(" ", "_")}')
        await cr.save.save_info(DIR, srvfolder, db=db)
        await i.response.send_message(f"{i.user.mention}, your base cords are now set to `{x} {y} {z}` in the dimension `{dimension.title()}`.")

@bot.command(description="Removes your base location")
async def removebase(i: di):
    server, userid, name, srvfolder, db = await cr.load.get_info(i, DIR) 
    base = db['User Data'][userid]['base']
    if base['x'] == 0 and base['y'] == 0 and base['z'] == 0:
        await i.response.send_message("You already don't have a base saved.")
    else:
        db['User Data'][userid]['base'] = {"x": 0, "y": 0, "z": 0, "dimension": "Overworld"}
        await rcon.command(f'dmarker delete id:{name}')
        await cr.save.save_info(DIR, srvfolder, db=db)
        await i.response.send_message(f"{i.user.mention}, you have successfully removed your base.")

@bot.command(description="Gives the location of a base")
async def viewbase(i: di, player: discord.Member):
    server, userid, name, srvfolder, db = await cr.load.get_info(i, DIR) 
    playerid, username = await cr.load.get_user_info(player) 
    base = db['User Data'][str(playerid)]['base']
    if base['x'] == 0 and base['y'] == 0 and base['z'] == 0:
        await i.response.send_message("This player doesn't have a base saved. Ask them to add it!")
    else:
        await i.response.send_message(f"{i.user.mention}, {username}'s base is `{base['x']} {base['y']} {base['z']}` in the dimension `{base['dimension']}`.")

#Database Commands
@bot.command(description="Creates a Discord server's files")
@commands.has_role("Bot Admin")
async def addserver(i: di):
    path = f"{DIR}/discord/{i.guild.id}"
    if os.path.exists(f"{path}/maindb.json"):
        await i.response.send_message("This server is already active.")
        return
    os.makedirs(f"{path}/ResetData")
    await cr.files.add_files(DIR, path)
    await i.response.send_message("Server added!")
    
@bot.command(description="Adds a player to the database")
@commands.has_role("Bot Admin")
async def adduser(i: di, user: discord.Member):
    server, userid, name, srvfolder, db = await cr.load.get_info(i, DIR) 
    playerid, username = await cr.load.get_user_info(user) 
    if str(playerid) in db['User Data']:
        await i.response.send_message(f"{username} is already added!")
    else:  
        data = {str(playerid): {"base": {"x": 0, "y": 0, "z": 0, "dimension": "Overworld"}, "economy": {"bank": 0, "clockin": 0, "clockout": 0, "money": 0}, "lotteries": 0, "prison": {"player": f"{username}", "length": 0, "started": 0, "release": 0, "newrelease": 0, "status": "Released", "reason": "Not In Prison", "times": 0}, "shop": {}}}
        db['User Data'].update(data)
        await cr.save.save_info(DIR, srvfolder, db=db)
        await i.response.send_message(f"Added {username} to the database!")

@bot.command(description="Lists past server resets")
@commands.has_role("Bot Admin")
async def listoldservers(i: di):
    server, userid, name, srvfolder, db = await cr.load.get_info(i, DIR) 
    message = "Here are the past resets:\n\n```"
    for (root, dirs, files) in os.walk(f'{srvfolder}/ResetData'):
        if not dirs:
            await i.response.send_message("There are no past resets.")
            return 
        for dir in dirs:
            message+=dir
    message+="```"
    await i.response.send_message(message)
    
@bot.command(description="Adds you to the whitelist and database")
async def register(i: di, username: str, platform: typing.Literal['Java', 'Bedrock']):
    await i.response.defer()
    for user in i.channel.members.remove(i.user):
        if (user.nick or user.name).lower() == (username.lower() or f".{username.lower()}"):
            await i.followup.send("That username is already registered. Contact an admin for assistance if this is incorrect.")
            return
    if platform == 'Bedrock':
        for user in i.channel.members:
            if (user.nick or user.name).lower() == f".{username.lower()}":
                await i.followup.send("That username is already registered. Contact an admin for assistance if this is incorrect.")
                return
        try:
            uuid, gamertag = xuid.get(target_gamertag = username)
            if uuid == None:
                await i.followup.send("That gamertag doesn't exist. Check your spelling.")
                return
        except:
            await i.followup.send("That gamertag doesn't exist. Check your spelling.")
            return
        username = f".{gamertag}"
        output = await rcon.command(f"fwhitelist add 00000000-0000-0000-000{uuid[0]}-{uuid[1:]}")
        if "unable to find any" in output:
            await i.followup.send("There was an issue adding your name. Check your spelling and try again, or message a moderator to help.")
            return
        else:
            pass
    else:
        for user in i.channel.members:
            if (user.nick or user.name).lower() == username.lower():
                await i.followup.send("That username is already registered. Contact an admin for assistance if this is incorrect.")
                return
        output = await rcon.command(f"whitelist add {username}")
        if "not exist" in output:
            await i.followup.send(f"There was an issue adding your name. Check your spelling and try again, or message a moderator to help.")
            return
        else:
            username = output.split(" ")[1]
    await i.guild.get_channel(bt.IDS.whitelist).send(f"Added `{username}` to the whitelist. Old name: {i.user.nick}")
    try:
        if i.user.nick[0] == ".":
            await rcon.command(f"fwhitelist remove {i.user.nick}")
        else:
            await rcon.command(f"whitelist remove {i.user.nick}")
    except:
        pass
    playername = username
    server, userid, name, srvfolder, db = await cr.load.get_info(i, DIR) 
    playerid, username = await cr.load.get_user_info(user)
    await i.user.edit(nick=username)
    if str(playerid) in db['User Data']:
        db['User Data'][userid]['prison']['player'] = playername
        await cr.save.save_info(DIR, srvfolder, db=db)
        await i.followup.send(f"Your username has been updated to {playername}")
    else:
        data = {str(playerid): {"base": {"x": 0, "y": 0, "z": 0, "dimension": "Overworld"}, "economy": {"bank": 0, "clockin": 0, "clockout": 0, "money": 0}, "lotteries": 0, "prison": {"player": f"{playername}", "length": 0, "started": 0, "release": 0, "newrelease": 0, "status": "Released", "reason": "Not In Prison", "times": 0}, "shop": {}}}
        db['User Data'].update(data)
        await cr.save.save_info(DIR, srvfolder, db=db)
        await i.followup.send(f"You have been whitelisted and added to the database for access to the features!\n`Username: {playername}`")

@bot.command(description="Resets a server's files")
@commands.has_role("Server Owner")
async def resetserver(i: di, username: str, *, resetname: str=None):
    server, userid, name, srvfolder, db = await cr.load.get_info(i, DIR) 
    if not username:
        await i.response.send_message("You need your username as confirmation.")
        return
    if username != name:
        await i.response.send_message("That username didn't match yours!")
        return
    archive = cr.files.archive_files(DIR, srvfolder, i)
    if archive == False:
        return
    os.remove(f'{DIR}/web/css/data.json')
    await cr.files.add_files(DIR, srvfolder)
    await i.response.send_message(f"The Discord server has been reset!")
        
@bot.command(description="Restores data from a previous reset")
@commands.has_role("Bot Admin")
async def restoreserver(i: di, username: str, savename: str, resetname: typing.Optional[str]):
    pass

@bot.command(description="Updates files to a newer format")
@commands.has_role("Bot Admin")
async def update(i: di):
    await i.response.send_message("No database updates at this time.")

#Economy Commands
@bot.command(description="Adds money to a player's wallet")
@commands.has_role("Economy Admin")
async def addmoney(i: di, player: discord.Member, amount: float):
    server, userid, name, srvfolder, db = await cr.load.get_info(i, DIR) 
    playerid, username = await cr.load.get_user_info(player) 
    economy = db['User Data'][str(playerid)]['economy']
    economy['bank'] += round(amount,2)
    db['User Data'][str(playerid)]['economy'] = economy
    await cr.save.save_info(DIR, srvfolder, blog=f"Added ${round(amount,2):,} to {player.nick}'s bank account.", db=db)
    await i.response.send_message(f"Added ${round(amount,2)} to {username}'s bank.")

@bot.command(description="Manages your bank account")
async def bank(i: di, transaction: typing.Literal['Deposit', 'Withdraw', 'View'], amount: float=None):
    server, userid, name, srvfolder, db = await cr.load.get_info(i, DIR) 
    economy = db['User Data'][userid]['economy']
    money, Bank = economy['money'], economy['bank']
    if amount != None and amount < 0.01:
        await i.response.send_message("You can only transfer a minimum of 1 cent.")
        return
    if transaction.lower() == "deposit":
        if money < round(amount, 2):
            missing = round(amount-money,2)
            await i.response.send_message(f"You don't have enough cash to put into your bank account. You need `${missing:,}` more.", ephemeral=True)
        else:
            nmoney, nbank = round(money-amount,2), round(Bank+amount,2)
            economy['money'], economy['bank'] = nmoney, nbank
            db['User Data'][userid]['economy'] = economy
            await i.response.send_message(f"You deposited ${round(amount,2):,}.", ephemeral=True)
            await cr.save.save_info(DIR, srvfolder, blog=f"{name} deposited ${round(amount,2):,}")
            await cr.save.change_inflation(DIR, srvfolder, db)
    elif transaction.lower() == "view":
        await i.response.send_message(f"You have `${round(Bank, 2):,}` in the bank and `${round(money, 2):,}` in cash for a total of `${round(money+Bank, 2):,}`.",ephemeral=True)
    elif transaction.lower() == "withdraw":
        if Bank < round(amount, 2):
            missing = round(amount-Bank,2)
            await i.response.send_message(f"You don't have enough money in your bank account to take cash out. You need `${missing:,}` more.", ephemeral=True)
        else:
            nmoney, nbank = round(money+amount,2), round(Bank-amount,2)
            economy['money'], economy['bank'] = nmoney, nbank
            db['User Data'][userid]['economy'] = economy
            await i.response.send_message(f"You withdrew ${round(amount,2):,}.", ephemeral=True)
            await cr.save.save_info(DIR, srvfolder, blog=f"{name} withdrew ${round(amount,2):,}")
            await cr.save.change_inflation(DIR, srvfolder, db)
    else:
        await i.response.send_message("The options for this command are `deposit <amount>`, `withdrawal <amount>`, or `view`. *Replace `<amount>` with the number you want.*")

@bot.command(description="Buy an item in Minecraft from the shop")
@app_commands.autocomplete(item=cr.load_prices_AutoComplete)
async def buy(i: di, seller: typing.Optional[discord.Member], item: str, id: typing.Optional[int] = None, amount: int = 1):
    server, userid, name, srvfolder, db = await cr.load.get_info(i, DIR) 
    economy, inflation, Id = db['User Data'][userid]['economy'], db['Misc Data']['inflation'], id-1
    with open(f"{DIR}/discord/Prices.json", "r+") as f:
        data = json.load(f)
    cost = round((inflation*data[item.title()])*amount,2)
    inflated = round(cost*1.07, 2)
    output = await rcon.command(f"give {name} air")
    if "No player was found" in output:
        await i.response.send_message("You need to be in Minecraft to run this command!")
        return
    elif economy['money'] < inflated:
        await rcon.command(f'tellraw {name} "You don\'t have enough money!"')
        return
    async def get_sellers(progress, db, preference = None):
        global datalist
        global total
        users, peeps, datalist, total = db['User Data'], [], [], progress
        for q in users:
            if item.title() in users[i]['shop']:
                if users[q]['shop'][item.title()]['vars']['nonbt'] > 0:
                    peeps.append(i)
        if preference != None:
            peeps.remove(preference)
            datalist.append([preference, users[preference]['shop'][item.title()]])
        random.shuffle(peeps)
        for person in peeps:
            total += users[person]['shop'][item.title()]['vars']['nonbt']
            if round(total) < amount:
                datalist.append([person, users[person]['shop'][item.title()]['vars']['nonbt']])
            elif round(total) == amount:
                datalist.append([person, users[person]['shop'][item.title()]['vars']['nonbt']])
                break
            else:
                datalist.append([person, amount-(total-users[person]['shop'][item.title()]['vars']['nonbt'])])
                break
        if round(total) < amount:
            await i.response.send_message(f"There isn't enough {item.title()} available. You requested {amount}, but there's only {total}, meaning the shop is {amount-total} short.")
            return "error"
        for row in datalist:
            profit, tax = round(((inflation*data[item.title()])*row[1])*.95, 2), round(((inflation*data[item.title()])*row[1])*.05, 2)
            db['User Data'][row[0]]['shop'][item.title()]['vars']['nonbt'] -= row[1]
            db['User Data'][row[0]]['economy']['money'] += profit
            db['Misc Data']['tax'] += tax
            salesman = await commands.MemberConverter.convert(commands.MemberConverter, i, str(row[0]))
            pid, pname = await cr.load.get_user_info(salesman)
            await cr.save.save_info(DIR, srvfolder, blog=f"{pname} sold {row[1]} of {item.title()} to {name} for ${profit:,} with ${tax:,} in taxes paid")
        return db
    if not seller:
        txt = None
        db = await get_sellers(0, db)
        if db == "error":
            return
    else:
        playerid, username = await cr.load.get_user_info(seller)
        sellershop = db['User Data'][playerid]['shop']
        if item.title() not in sellershop:
            db = await get_sellers(0, db)
            if db == "error":
                return
            txt = f"{username} didn't have any items, so we relied on random sellers."
        elif sellershop[item.title()] < amount:
            db = await get_sellers(sellershop[item.title()], db, playerid)
            if db == "error":
                return
            txt = f"{username} didn't have enough items, so we got the remaining from other random sellers."
        else:
            profit, tax = round(((inflation*data[item.title()])*amount)*.95, 2), round(((inflation*data[item.title()])*amount)*.05, 2)
            db['User Data'][playerid]['shop'][item.title()] -= amount
            db['User Data'][playerid]['economy']['money'] += profit
            db['Misc Data']['tax'] += tax
            await cr.save.save_info(DIR, srvfolder, blog=f"{username} sold {amount} of {item.title()} to {name} for ${profit:,} with ${tax:,} in taxes paid")
            txt = None
    await rcon.command(f"give {name} {item.lower().replace(' ', '_')} {amount}")
    db['Misc Data']['tax'] += cost*.07
    db['User Data'][userid]['economy']['money'] -= inflated
    if txt != None:
        await rcon.command(f'tellraw {name} "{txt}"')
    await rcon.command(f'tellraw {name} ["",{{"text":"You paid","color":"gray"}},{{"text":" ${inflated:,}","color":"green"}},{{"text":" for ","color":"gray"}},{{"text":"{amount:,}","color":"aqua"}},{{"text":" of ","color":"gray"}},{{"text":"{item.title()}","color":"white"}}]')
    await cr.save.save_info(DIR, srvfolder, blog=f"{name} bought {amount} of {item} for ${inflated:,}, ${round(cost*.07, 2):,} of which was taxes.")
    await cr.save.change_inflation(DIR, srvfolder, db)

@bot.command(description="Manage or donate to charities")
async def charity(i: di, option1: str, charity:str=None, option2:str=None, person: typing.Optional[discord.Member]=None, *, option3:str=None):
    server, userid, name, srvfolder, db = await cr.load.get_info(i, DIR) 
    basecmd, fcharity = option1.lower(), charity.lower().replace(" ", "_")
    options, cpath = ["create", "donate", "edit", "give", "info", "list", "pause", "remove", "resume"], f"{srvfolder}/Charities/{fcharity}.json"
    async def save_charity(cname, cdata):
        with open(f"{srvfolder}/Charities/{cname}.json", "r+") as f:
            f.seek(0)
            json.dump(cdata, f)
            f.truncate()
    async def load_charity(cname):
        try:
            with open(f"{srvfolder}/Charities/{cname}.json", "r+") as f:
                data = json.load(f)
                return data
        except:
            await i.response.send_message(f"The charity \"{charity}\" does not exist. Check your spelling and try again.")
    if not basecmd in options:
        await i.response.send_message("That wasn't a charity option. View https://someminegame.com/Main/Commands/charity for more info on this feature's usage.")
        return
    if basecmd == "create":
        try:
            open(cpath, "x")
        except:
            await i.response.send_message("That charity is already active. Please choose a different name.")
            return
        if option2 or option3 == None:
            await i.response.send_message("You need a goal and a description.")
            return
        sdata = {"organizer": userid, "name": name, "cause": option3, "raised": 0, "goal": option2.replace(",", ''), "donations": 0, "funds": 0, "distributed": 0, "active": True, "activatable": True}
        await save_charity(fcharity, sdata)
        await i.response.send_message(f"Charity `{charity}` has been created!")
    elif basecmd == "donate":
        try:
            amount = float(round(option2,2))
        except:
            await i.response.send_message("option2 must be a number.")
            return
        if db['User Data'][userid]['economy']['money'] < amount:
            await i.response.send_message("You don't have enough cash for this. Try withdrawing some!")
            return
        cinfo = await load_charity(fcharity)
        cinfo['raised'] += amount
        cinfo['funds'] += amount
        cinfo['donations'] += 1
        await save_charity(fcharity)
        db['User Data'][userid]['economy']['money'] -= amount
        await cr.save.save_info(DIR, srvfolder, blog=f"{name} donated ${amount} to {fcharity}")
        await i.response.send_message("Donation successful. Thanks for supporting your fellow members!")
    elif basecmd == "edit":
        pass
    elif basecmd == "give":
        pass
    elif basecmd == "info":
        cinfo = await load_charity(fcharity)
    elif basecmd == "list":
        for root, dirs, files in os.walk(f"{srvfolder}"):
            pass
    elif basecmd == "pause":
        pass
    elif basecmd == "remove":
        pass
    elif basecmd == "resume":
        pass

@bot.command(description="Earns money for playing")
async def clockin(i: di):
    server, userid, name, srvfolder, db = await cr.load.get_info(i, DIR) 
    dt = datetime.datetime.now()
    timestamp, economy = int(round(dt.timestamp())), db['User Data'][userid]['economy']
    output = await rcon.command(f"give {name} air")
    if "No player was found" in output:
        await i.response.send_message("You need to be in Minecraft to run this command!")
        return
    if economy['clockin'] != 0:
        await i.response.send_message("You need to end your current shift first! `&clockOut`")
        return
    economy['clockin'], economy['clockout'] = timestamp, 0
    db['User Data'][userid]['economy'] = economy
    await cr.save.save_info(DIR, srvfolder, blog=f"{name} clocked into work", db=db)
    await i.response.send_message("You clocked into work!")

@bot.command(description="Ends your current session")
async def clockout(i: di):
    server, userid, name, srvfolder, db = await cr.load.get_info(i, DIR) 
    dt = datetime.datetime.now()
    timestamp, economy = int(round(dt.timestamp())), db['User Data'][userid]['economy']
    if economy['clockin'] == 0:
        await i.response.send_message("You need to start a shift first! `&clockIn`")
        return
    earned = timestamp - economy['clockin']
    mathstuff, tax = round((earned/60)*7.5, 2), round(earned*.02, 2)
    earnings = round(mathstuff-tax, 2)
    economy['bank'], economy['clockout'], economy['clockin'] = round(economy['bank']+earnings, 2), timestamp, 0
    db['User Data'][userid]['economy'] = economy
    db['Misc Data']['tax'] += tax
    await cr.save.save_info(DIR, srvfolder, blog=f"{name} clocked out of work and was paid ${earnings:,}")
    await cr.save.change_inflation(DIR, srvfolder, db)
    await i.response.send_message("You clocked out of work!")

@bot.command(description="Draws the winning lottery ticket")
@commands.has_any_role("Bot Admin", "Economy Admin")
async def drawlottery(i: di):
    server, userid, name, srvfolder, db = await cr.load.get_info(i, DIR) 
    entries, pool, udata = [], db['Misc Data']['lotto'], db['User Data']
    for player in db['User Data']:
        for q in range(udata[player]['lotteries']):
            entries.append(player)
        udata[player]['lotteries'] = 0
    if not entries:
        await i.response.send_message("No tickets have been purchased yet. Try again a different day.")
    else:
        winner = random.choice(entries)
        username = await commands.MemberConverter.convert(commands.MemberConverter, i, str(winner))
        await i.response.send_message(f"And the winner for the grand prize of ${pool:,} is:")
        await asyncio.sleep(3)
        await i.response.send_message("Wait for it...")
        await asyncio.sleep(3)
        await i.response.send_message(f"{username.mention}!!")
        udata[str(winner)]['economy']['money'] += pool
        db['Misc Data']['lotto'], db['User Data'] = 0, udata
        await cr.save.save_info(DIR, srvfolder, blog=f"{username.nick} won the lottery of ${pool:,}")
        await cr.save.change_inflation(DIR, srvfolder, db)
        await username.send(f"Congratulations on winning ${pool:,} from the lottery!")
        
@bot.command(description="Enchant your item if supported")
async def enchant(i: di, level: int, *, enchantment: str):
    await i.response.send_message("This command is currently deactivated for an update.")
    server, userid, name, srvfolder, db = await cr.load.get_info(i, DIR) 
    output = await rcon.command(f"data get entity {name} SelectedItem")
    nbt = output.split('data: ')[1]
    data_string = re.sub(r'(\d+)([bslfd])', r'\1', nbt)
    data_string = re.sub(r'\b(?!minecraft\b)(\w+)(?=\s*):', r'"\1":', data_string)
    data_string = data_string.replace("[", "").replace("]", "")
    jsons = json.loads(data_string)
    response = f"{output}\n\n{nbt}\n\n{jsons}\n\n{jsons['tag']['Enchantments']}\n\n{jsons['tag']['Enchantments']['id']}\n\n{jsons['tag']['Enchantments']['lvl']}"
    await i.response.send_message(response)

@bot.command(description="Forcefully ends a player's session")
@commands.has_any_role("Bot Admin", "Economy Admin")
async def forceclockout(i: di, player: discord.Member, keep: bool):
    server, userid, name, srvfolder, db = await cr.load.get_info(i, DIR) 
    playerid, username = await cr.load.get_user_info(player) 
    economy, dt = db['User Data'][playerid]['economy'], datetime.datetime.now()
    timestamp = int(round(dt.timestamp()))
    if economy['clockin'] == 0:
        await i.response.send_message("This player is already clocked out!")
        return
    elif keep == True:
        earned = timestamp - economy['clockin']
        mathstuff, tax = round((earned/60)*7.5, 2), round(earned*.02, 2)
        earnings = round(mathstuff-tax, 2)
        economy['bank'], economy['clockout'], economy['clockin'] = round(economy['bank']+earnings, 2), timestamp, 0
        db['User Data'][userid]['economy'] = economy
        blog = f"{username} was force clocked out of work and was paid ${earnings:,}"
        msg = f"Clocked {username} out, allowing them to keep their earnings."
        await cr.save.change_inflation(DIR, srvfolder, db)
    else:
        economy['clockout'], economy['clockin'] = timestamp, 0
        db['User Data'][userid]['economy'] = economy
        blog = f"{username} was force clocked out of work and was denied pay"
        msg = f"Clocked {username} out, removing their earnings."
    await cr.save.save_info(DIR, srvfolder, blog=blog)
    await i.response.send_message(msg)

@bot.command(description="Shows the current inflation rate")
async def inflation(i: di):
    server, userid, name, srvfolder, db = await cr.load.get_info(i, DIR) 
    inflate = db['Misc Data']['inflation']
    if inflate <= 0.75:
        Status = "low"
    elif inflate >= 1.25:
        Status = "high"
    else:
        Status = "normal"
    await i.response.send_message(f"The current inflation is `{round(inflate*100,2):,}%` which is {Status}.")

@bot.command(description="Buy lottery tickets")
async def lottery(i: di, amount: int):
    server, userid, name, srvfolder, db = await cr.load.get_info(i, DIR) 
    lotto, cost, userdata = db['Misc Data']['lotto'], round(20*amount, 2), db['User Data'][userid]
    if amount <= 0:
        await i.response.send_message("You need to buy at least 1 ticket")
        return
    elif userdata['economy']['money'] >= cost:
        userdata['lotteries'] += amount
        userdata['economy']['money'] -= cost
        pool, db['User Data'][userid] = round(lotto+cost), userdata
        db['Misc Data']['lotto'] = pool
        await i.response.send_message(f"The lottery has now risen to **${pool:,}**")
        await i.user.send(f"You bought {amount} lottery tickets! Good luck!")
        await cr.save.save_info(DIR, srvfolder, blog=f"{name} bought {amount} tickets worth ${cost:,}")
        await cr.save.change_inflation(DIR, srvfolder, db)
    else:
        remaining = round(cost-userdata['economy']['money'], 2)
        await i.user.send(f"You don't have enough cash. You need ${remaining:,} more. Perhaps try `&bank withdraw {remaining}`.")

@bot.command(description="Pay a player from your wallet")
async def pay(i: di, player: discord.Member, amount:float, *, reason: str = None):
    server, userid, name, srvfolder, db = await cr.load.get_info(i, DIR) 
    playerid, username = await cr.load.get_user_info(player) 
    peconomy, ueconomy = db['User Data'][playerid]['economy'], db['User Data'][userid]['economy']
    umoney = ueconomy['money']
    if userid == playerid:
        await i.response.send_message("You cannot pay yourself!")
        return
    if amount <= 0:
        await i.response.send_message("You cannot send less than $0.01.")
        return
    elif umoney < amount:
        await i.user.send(f"You have insufficiant cash. You still need ${round(amount-umoney, 2):,}. Try `&bank withdraw {round(amount-umoney, 2)}`")
        return
    ueconomy['money'] = round(umoney-amount, 2)
    peconomy['money'] += round(amount, 2)
    if not reason:
        await i.user.send(f"Payment of ${round(amount, 2):,} to {username} successful.")
        await player.send(f"You have received ${round(amount, 2):,} from {name} in {i.guild.name}")
        blog = f"{name} paid {username} ${round(amount, 2):,}."
    else:
        await i.user.send(f"Payment of ${round(amount, 2):,} to {username} successful. Payment reason: ```{reason}```")
        await player.send(f"You have received ${round(amount, 2):,} from {name} in {i.guild.name}. Payment reason: ```{reason}```")
        blog = f"{name} paid {username} ${round(amount, 2):,}. Reason: \"{reason}\""
    db['User Data'][playerid]['economy'], db['User Data'][userid]['economy'] = peconomy, ueconomy
    await cr.save.save_info(DIR, srvfolder, blog=blog, db=db)

@bot.command(description="Pay the government from your wallet")
async def paygovt(i: di, amount: float, reason: typing.Optional[str]):
    server, userid, name, srvfolder, db = await cr.load.get_info(i, DIR) 
    economy = db['User Data'][userid]['economy']
    money = economy['money']
    if amount <= 0:
        await i.response.send_message("You cannot send less than $0.01.", ephemeral=True)
        return
    elif money < amount:
        await i.user.send(f"You have insufficiant cash. You still need ${round(amount-money, 2):,}. Try `&bank withdraw {round(amount-money, 2)}`")
        return
    economy['money'], channel = round(money-amount, 2), discord.utils.get(i.message.guild.text_channels, name="server-finances")
    db["Misc Data"]["tax"] += round(amount, 2)
    if not reason:
        await i.response.send_message("You need a reason for paying the government. (It prevents against government corruption scamming you)")
        return
    else:
        await i.user.send(f"Payment of ${round(amount, 2):,} to the government successful. Payment reason: ```{reason}```")
        await channel.send(f"You have received ${round(amount, 2):,} from {name}. Payment reason: ```{reason}```")
        blog = f"{name} paid the government ${round(amount, 2):,}. Reason: \"{reason}\""
    db['User Data'][userid]['economy'] =  economy
    await cr.save.save_info(DIR, srvfolder, blog=blog)
    await cr.save.change_inflation(DIR, srvfolder, db)

@bot.command(description="Get the price of an item")
@app_commands.autocomplete(item=cr.load_prices_AutoComplete)
async def price(i: di, amount: typing.Optional[int] = None, *, item: str):
    server, userid, name, srvfolder, db = await cr.load.get_info(i, DIR) 
    with open(f"{DIR}/discord/Prices.json", "r+") as f:
        data = json.load(f)
        cost = db['Misc Data']['inflation']*data[item.title()]
    if not amount:
        await i.response.send_message(f"In the shop, the price of `{item.title()}` is `${round(cost*1.07, 2):,}`, and it will sell for `${round(cost*.95, 2):,}`.\nIn the void, the price of `{item.title()}` is `${round((cost*1.07)*250, 2):,}`, and it will sell for `${round((cost/4)*.95, 2):,}`.")
    else:
        await i.response.send_message(f"In the shop, the price for `{amount}` of `{item.title()}` is `${round((cost*amount)*1.07, 2):,}`, and will sell for `${round((cost*amount)*.95, 2):,}`.\nIn the void, the price for `{amount}` of `{item.title()}` is `${round(((cost*amount)*1.07)*250, 2):,}`, and will sell for `${round(((cost*amount)/4)*.95, 2):,}`.")

@bot.command(description="Gamble your money for a random item")
async def randomitem(i: di):
    with open(f"{DIR}/Discord/Prices.json", "r") as f:
        lines = json.load(f)
        global items
        items = []
        for q in lines:
            items.append(str(q))
    item = random.choice(items)
    await i.response.send_message(item)

@bot.command(description="Removes money from a player's wallet")
@commands.has_role("Economy Admin")
async def removemoney(i: di, player: discord.Member, amount: float):
    server, userid, name, srvfolder, db = await cr.load.get_info(i, DIR) 
    playerid, username = await cr.load.get_user_info(player) 
    economy = db['User Data'][str(playerid)]['economy']
    economy['bank'] -= round(amount, 2)
    db['User Data'][str(playerid)]['economy'] = economy
    await cr.save.save_info(DIR, srvfolder, blog=f"Removed ${round(amount,2):,} from {player.nick}'s bank account.", db=db)

@bot.command(description="Adds an item to your shop. Basic and All modes don't preserve the nbt data.")
@app_commands.autocomplete(item=cr.load_prices_AutoComplete)
async def sell(i: di, item: str, amount: int = 1, mode: typing.Literal["Basic", "Holding", "All"] = "Basic"):
    server, userid, name, srvfolder, db = await cr.load.get_info(i, DIR) 
    item, itemf = item.title(), item.lower().replace(" ", "_")
    online = await rcon.command(f"give {name} air")
    if "player not found" in online:
        await i.response.send_message("You need to be on Minecraft to use this feature.", ephemeral=True)
    async def get_amount(ID, snbt):
        output = await rcon.command(f"clear {name} {ID}{snbt} 0")
        try:
            possession = int(output.split(" ")[1])
            return possession
        except:
            await i.response.send_message(f"You don't have any of **{item}**.", ephemeral=True)
            return
    if amount < 1:
        await i.response.send_message("You can't sell less than 1 item silly!")
        return
    if mode == 'Basic':
        containers, container = ['shulker_box', 'bundle'], "]"
        for f in containers:
            if f in itemf:
                container = ",minecraft:container=[]|minecraft:bundle_contents=[]]"
                break
        snbt, ID = f"minecraft:{itemf}[minecraft:enchantments={{}},!minecraft:custom_name,!minecraft:lodestone_tracker,!minecraft:unbreakable,!minecraft:map_id{container}", ""
    elif mode == 'Holding':
        await i.response.send_message(f"This feature needs to be researched further. Check back later!")
        return
        # output = await rcon.command(f"data get entity {name} SelectedItem")
        # await i.channel.send(f"Output: {output}")
        # step = output.split("has the following entity data:")[-1].strip()
        # step2 = step.split(',')
        # step2.remove(step2[-2])
        # snbt, ID = ", ".join(step2), ""
        # await i.channel.send(f"{snbt}  --  {ID}")
    else:
        ID, snbt = f"minecraft:{itemf}", ""
    possession = await get_amount(ID, snbt)
    if possession < amount:
        await i.response.send_message(f"You do not have enough of **{item}**!", ephemeral=True)
        return
    await rcon.command(f'clear {name} {ID}{snbt} {amount}')
    shop = db['User Data'][str(userid)]['shop']
    if not item in shop:
        shop[item] = {"count": 0, "vars": {'nonbt': 0}}
    shop[item]["count"] += amount
    shop[item]["vars"]['nonbt'] += amount
    db['User Data'][str(userid)]['shop'] = shop
    await cr.save.save_info(DIR, srvfolder, slog=f"{name} added {amount:,} of {item} to their shop.", db=db)
    await i.response.send_message(f"Successfully added **{amount:,}** of `{item}` to your shop!", ephemeral=True)
    await rcon.command(f'tellraw {name} ["",{{"text":"You added ","color":"gray"}},{{"text":"{amount:,}","color":"aqua"}},{{"text":" of ","color":"gray"}},{{"text":"{item.title()}","color":"white"}},{{"text":" to your shop.","color":"gray"}}]')

@bot.command(description="Sets a player's wallet to a specific amount")
@commands.has_role("Economy Admin")
async def setmoney(i: di, player: discord.Member, amount: float):
    server, userid, name, srvfolder, db = await cr.load.get_info(i, DIR) 
    playerid, username = await cr.load.get_user_info(player) 
    db['User Data'][str(playerid)]['economy']['bank'] = round(amount, 2)
    await cr.save.save_info(DIR, srvfolder, blog=f"Set {username}'s bank account to ${round(amount,2):,}.", db=db)
    i.response.send_message(f"Set {username}'s bank account to **${round(amount),2}**.")
    
@bot.command(description="View shops or remove an item from your own")
@app_commands.autocomplete(item=cr.load_prices_AutoComplete)
async def shop(i: di, option:typing.Literal['Get', 'Remove'], player: typing.Optional[discord.Member] = None, amount: typing.Optional[int] = 1, *, item: str = None):
    server, userid, name, srvfolder, db = await cr.load.get_info(i, DIR) 
    playerid, username = await cr.load.get_user_info(player) 
    if option.lower() == "get":
        await i.response.send_message(f"https://data.someminegame.com/Shop/{username}")
    elif option.lower() == "remove":
        if not amount:
            amount = 1
        amount = int(amount)
        output = await rcon.command(f"give {name} air")
        if "No player was found" in output:
            await i.response.send_message("You need to be in Minecraft to run this command!")
            return
        data = db['User Data'][userid]['shop']
        if not item.title() in data:
            await rcon.command(f'tellraw {name} "You don\'t have any {item} in your shop."')
            return
        elif data[item.title()] < amount:
            await rcon.command(f'tellraw {name} "You do not have enough {item}. You need {amount-data[item.title()]} more."')
            return
        elif amount <= 0:
            await rcon.command(f'tellraw {name} "You cannot remove a negative amount of an item from your shop!"')
            return
        else:
            db['User Data'][userid]['shop'][item.title()] -= amount
        await rcon.command(f"give {name} {item.lower().replace(' ', '_')} {amount}")
        await rcon.command(f'tellraw {name} ["",{{"text":"You removed ","color":"gray"}},{{"text":"{amount:,}","color":"aqua"}},{{"text":" of ","color":"gray"}},{{"text":"{item.title()}","color":"white"}},{{"text":" to your shop.","color":"gray"}}]')
        await cr.save.save_info(DIR, srvfolder, blog=f"{name} removed {amount:,} of {item.title()} from their shop")
        await cr.save.change_inflation(DIR, srvfolder, db=db)      

@bot.command(description="See how much money the government has")
@commands.has_role("Government Finances")
async def taxbal(i: di):
    server, userid, name, srvfolder, db = await cr.load.get_info(i, DIR) 
    await i.response.send_message(f"The tax account has `${round(db['Misc Data']['tax'], 2):,}` in it.")
    
@bot.command(description="Pay a player with government funds")
@commands.has_role("Government Finances")
async def taxpay(i: di, player: discord.Member, amount: float, *, reason: str = None):
    server, userid, name, srvfolder, db = await cr.load.get_info(i, DIR) 
    playerid, username = await cr.load.get_user_info(player) 
    economy, tax, channel = db['User Data'][playerid]['economy'], db['Misc Data']['tax'], discord.utils.get(i.message.guild.text_channels, name="server-finances")
    if amount <= 0:
        await i.response.send_message("You cannot send less than $0.01.")
        return
    elif tax < amount:
        await channel.send(f"The tax account has insufficiant funds. You still need ${round(amount-tax, 2):,}.")
        return
    tax = round(tax-amount, 2)
    economy['money'] += round(amount, 2)
    if not reason:
        await channel.send("You need a reason for paying people.")
        return
    else:
        await channel.send(f"Payment of ${round(amount, 2):,} to {username} successful. Payment reason: ```{reason}```")
        await player.send(f"You have received ${round(amount, 2):,} from the government. Payment reason: ```{reason}```")
        blog = f"The government paid {username} ${round(amount, 2):,}. Reason: \"{reason}\""
    db['User Data'][playerid]['economy'], db['Misc Data']['tax'] = economy, tax
    await cr.save.save_info(DIR, srvfolder, blog=blog)
    await cr.save.change_inflation(DIR, srvfolder, db)

@bot.command(description="Buy from the void. Gives you any item")
@app_commands.autocomplete(item=cr.load_prices_AutoComplete)
async def voidbuy(i: di, item: str, amount: typing.Optional[int] = 1):
    server, userid, name, srvfolder, db = await cr.load.get_info(i)
    economy, inflation = db['User Data'][userid]['economy'], db['Misc Data']['inflation']
    with open(f"{DIR}/discord/Prices.json", "r+") as f:
        data = json.load(f)
    cost = round((inflation*data[item.title()])*amount,2)
    inflated = round(cost*1.07, 2)
    if economy['money'] < inflated:
        await rcon.command(f'tellraw {name} "You don\'t have enough money!"')
        return
    output = await rcon.command(f"give {name} {item.replace(' ', '_')} {amount}")
    if "No player was found" in output:
        await i.response.send_message("You need to be in Minecraft to run this command!", ephemeral=True)
        return
    db['Misc Data']['tax'] += cost*.07
    db['User Data'][userid]['economy']['money'] -= inflated
    await rcon.command(f'tellraw {name} ["",{{"text":"You paid","color":"gray"}},{{"text":" ${inflated:,}","color":"green"}},{{"text":" for ","color":"gray"}},{{"text":"{amount:,}","color":"aqua"}},{{"text":" of ","color":"gray"}},{{"text":"{item.title()}","color":"white"}}]')
    await cr.save.save_info(srvfolder, blog=f"{name} bought {amount} of {item} for ${inflated:,}, ${round(cost*.07, 2):,} of which was taxes.")
    await cr.save.change_inflation(srvfolder, db)

@bot.command(description="Sell to the void. Does not support NBT and reduced earnings.")
@app_commands.autocomplete(item=cr.load_prices_AutoComplete)
async def voidsell(i: di, item: str, amount: typing.Optional[int] = 1):
    server, userid, name, srvfolder, db = await cr.load.get_info(i)
    inflation = db['Misc Data']['inflation']
    with open(f"{DIR}/discord/Prices.json", "r+") as f:
        data = json.load(f)
    output = await rcon.command(f"minecraft:clear {name} {item.replace(' ', '_')} {amount}")
    ingamount = int(output.split()[1])
    if "No player was found" in output:
        await i.response.send_message("You need to be in Minecraft to run this command!", ephemeral=True)
        return
    elif ingamount < amount:
        await rcon.command(f'tellraw {name} "You don\'t have enough of {item.title()}!"')
        await rcon.command(f'give {name} {item.replace(" ", "_")} {ingamount}')
        return
    payment = round(((inflation*data[item.title()])*amount)/4, 2)
    tax = round(payment*.05, 2)
    db['Misc Data']['tax'] += tax
    db['User Data'][userid]['economy']['money'] += payment*.95
    await rcon.command(f'tellraw {name} ["",{{"text":"You made","color":"gray"}},{{"text":" ${round(payment*.95, 2):,}","color":"green"}},{{"text":" from ","color":"gray"}},{{"text":"{amount:,}","color":"aqua"}},{{"text":" of ","color":"gray"}},{{"text":"{item.title()}","color":"white"}}]')
    await cr.save.save_info(srvfolder, blog=f"{name} sold {amount:,} of {item.title()} for ${round(payment*.95, 2):,} and paid ${tax:,} in taxes")
    await cr.save.change_inflation(srvfolder, db=db)

@bot.command(description="View the top ten richest players")
async def wealthy(i: di):
    server, userid, name, srvfolder, db = await cr.load.get_info(i, DIR) 
    datalist, messagelist = [], []
    for player in db['User Data']:
        economy = db['User Data'][player]['economy']
        datalist.append([player, round(economy['money']+economy['bank'],2)])
    datalist.sort(reverse=True, key=lambda x: x[1])
    global index
    global message
    index, message = 0, "Here are the richest players!\n```"
    for q in range(10):
        try:
            messagelist.append(f"{index+1}: {db['User Data'][str(datalist[index][0])]['prison']['player']}             {datalist[index][1]:,}")
            index+=1
        except:
            pass
    for mline in messagelist:
        message+=f"\n{mline}"
    message+="```"
    await i.response.send_message(message)

#Miscellaneous Commands
@bot.command(description="Remotely run a Minecraft command")
@commands.has_role("Bot Admin")
async def cmd(i: di, command: str):
    server, userid, name, srvfolder, db = await cr.load.get_info(i, DIR) 
    output = await rcon.command(f"{command}")
    await i.response.send_message(output)
    await cr.save.save_info(DIR, srvfolder, rlog=f"{name} ran the command {command}' with the output: {output}")

@bot.command(description="See the current Miencraft day")
async def day(i: di):
    output = await rcon.command(f"time query day")
    command = output.split(' ')
    day = command[-1]
    await i.response.send_message(f"The current day is {day}")

@bot.command(description="Sends a link to the help page for a command")
async def help(i: di, command:str=None):
    if not command:
        await i.response.send_message("The help page can be found at https://someminegame.com/Main/Commands")
        return
    global index
    index = 0
    commands = ['addBase', 'addMoney', 'addSentence', 'addServer', 'addUser', 'bank', 'buy', 'charity', 'clockIn', 'clockOut', 'cmd', 'day', 'drawLottery', 'editBase', 'editSentence', 'enchant', 'enchantmentPlus', 'forceClockOut', 'help', 'ip', 'inflation', 'listOldServers', 'lottery', 'pay', 'payGovt', 'price', 'releasePrisoner', 'removeBase', 'removeMoney', 'reportIncident', 'resetServer', 'restoreServer', 'sell', 'setMoney', 'status', 'taxBal', 'taxPay', 'test', 'update', 'viewBase', 'viewSentence', 'voidBuy', 'voidSell', 'wealthy']
    for option in commands:
        if command.lower() == commands[index].lower():
            command = commands[index]
            break
        else:
            index += 1
    if command not in commands:
        await i.response.send_message("Your command wasn't found. Check your spelling and make sure the command isn't deprecated and try again.")
    else:
        await i.response.send_message(f"https://someminegame.com/Main/Commands/{command}")

@bot.command(description="List or edit the IPs")
async def ip(i: di, jip:str=None, bip:str=None, bp:int=None):
    server, userid, name, srvfolder, db = await cr.load.get_info(i, DIR) 
    ips = db['Misc Data']['ip']
    if not (jip and bip and bp):
        await i.response.send_message(f"The server IPs are\n\n**Java:** `{ips['JIP']}`\n**Bedrock**: `{ips['BIP']}     Port: {ips['BP']}`")
        return
    roles = i.user.roles
    admin = discord.utils.get(i.user.guild.roles, name='Bot Admin')
    if not admin in roles:
        await i.response.send_message("You need to be a Bot Admin to change this setting.")
        return
    if not bp:
        bp = 19132
    await i.response.send_message("The IPs have been changed.")
    ips['JIP'], ips['BIP'], ips['BP'] = jip, bip, bp
    db['Misc Data']['ip'] = ips
    await cr.save.save_info(DIR, srvfolder, db=db)
    
@bot.command(description="DW about it")
@commands.dm_only()
async def scam(i: di):
    username = i.message.author.nick
    if username != ("SomeMineGame" or "zoobleCar"):
        await i.response.send_message("I SAID, DON'T WORRY ABOUT IT.")
        return
    output = await rcon.command(f"clear {username:10,.2f} sugar")
    amount = int(str(output).split(" ")[1])
    await i.response.send_message(f'give {username} minecraft:sugar{{display:{{Name:\'["",{{"text":"Cocaine","italic":false,"color":"aqua"}}]\',Lore:[\'["",{{"text":"Purest Authentic Quality","italic":false,"color":"green"}}]\']}}}} {amount}')
    
@bot.command()
@commands.has_role("Bot Admin")
async def setup_channel_roles(i: di):
    msg = await i.channel.send("To help keep things organized, there are a few channels you need roles for. React to the role you want, and unreact to remove it again later.\n\n\n:warning: - Testing Server\n\n:tools: - Builds Server\n\n:desktop: - Videos (SomeMineGame & Playermade)\n\n:bell: - Notices (Status, Issues, Pings, & More)")
    await msg.add_reaction(reactiona)
    await msg.add_reaction(reactionb)
    await msg.add_reaction(reactionc)
    await msg.add_reaction(reactiond)

@bot.command(description="Tests if the Minecraft server is responding")
async def status(i: di):
    await i.response.send_message("Pinging the server...")
    local = minestat.MineStat(bt.MC.local_domain, bt.MC.local_query)
    Global = minestat.MineStat(bt.MC.global_domain, 25565)
    if local.online == True and Global.online == True:
        message = "online, and is"
    elif local.online == True and Global.online == False:
        message = "online, but is **NOT**"
    elif local.online == False and Global.online == False:
        message = "offline, and is **NOT**"
    elif local.online == False and Global.online == True:
        message = "likely due to testing offline, but somehow"
    await i.channel.send(f"The server is {message} available for players to join.")

@bot.command(description="Tests the Discord bot's response")
async def test(i: di):
    await bot.sync()
    await i.response.send_message(f"The bot is operational!")

#Legal Commands
@bot.command(description="Create a nation")
@commands.has_role("Bot Admin")
async def addnation(i: di, leader: discord.Member, name:str, motto:str, *, corners:int):
    server, userid, name, srvfolder, db = await cr.load.get_info(i, DIR)
    playerid, username = await cr.load.get_user_info(leader)
    nation_data = {name:{"leader": leader, "motto": motto, "corners": corners}}
    with open(f"{srvfolder}/nations.json", "r+"):
        pass

@bot.command(description="Creates a prison sentence for a player")
@commands.has_role("Prison Guard")
async def addsentence(i: di, player: discord.Member, length: int, *, reason: str):
    server, userid, name, srvfolder, db = await cr.load.get_info(i, DIR) 
    playerid, username = await cr.load.get_user_info(player) 
    prison = db['User Data'][playerid]['prison']
    output = await rcon.command(f"time query day")
    command = output.split(' ')
    day = int(command[-1])
    release = round(day+length)
    if prison['status'] == "Unreleased":
        await i.response.send_message(f"{username} is already in prison. If you'd like to make an edit, use `&editSentence {username} {round(prison['newrelease']-(length+day))}`, and if you're trying to release them, use `&releasePrisoner {username}`.")
        return
    db['User Data'][playerid]['prison'] = {"player": username, "length": length, "started": day, "release": release, "newrelease": release, "status": "Unreleased", "reason": reason, "times": round(prison['times']+1)}
    await cr.save.save_info(DIR, srvfolder, plog=f"{username} was sent to prison by {name} for the {round(prison['times']+1)} time for \"{reason}\" and will be released on day {release:,}", db=db)
    await i.response.send_message(f"Sentence for {username} created!")
    
@bot.command(description="Edits your nation")
@commands.has_role("Bot Admin")
async def editnation(i: di, name:str, motto:str, *, corners:int):
    pass

@bot.command(description="Edits a player's prison sentence")
@commands.has_role("Prison Guard")
async def editsentence(i: di, player: discord.Member, change: int):
    server, userid, name, srvfolder, db = await cr.load.get_info(i, DIR) 
    playerid, username = await cr.load.get_user_info(player) 
    prison = db['User Data'][playerid]['prison']
    if prison['status'] == "Released":
        await i.response.send_message(f"{username} is released from prison and therefore can't have their day edited.")
        return
    if change == 0:
        await i.response.send_message("Please use a whole number greator or less than 0")
        return
    schange = 1
    if change < 0:
        text, text1 = "removed", "from"
        schange = round(change*-1)
    else:
        text, text1 = "added", "to"
    db['User Data'][playerid]['prison']['newrelease'] = round(change+prison["newrelease"])
    await cr.save.save_info(DIR, srvfolder, plog=f"{name} {text} {schange:,} days {text1} {username}'s sentence", db=db)
    await i.response.send_message(f"Sentence for {username} updated!")

@bot.command(description="Ends a player's prison sentence")
@commands.has_role("Prison Guard")
async def releaseprisoner(i: di, player: discord.Member):
    server, userid, name, srvfolder, db = await cr.load.get_info(i, DIR) 
    playerid, username = await cr.load.get_user_info(player) 
    prison = db['User Data'][playerid]['prison']
    output = await rcon.command(f"time query day")
    command = output.split(' ')
    day = int(command[-1])
    if prison['status'] == "Released":
        await i.response.send_message(f"{username} is already released from prison.")
        return
    if prison['newrelease'] > day:
        await i.response.send_message(f"{username} still has {round(prison['newrelease']-day)} days left. If you need to change the release date, use `&editSentence {username} {day-round(prison['newrelease'])}`")
        return
    db['User Data'][playerid]['prison'] = {"player": username, "length": 0, "started": 0, "release": 0, "newrelease": 0, "status": "Released", "reason": "Not In Prison", "times": prison['times']}
    await cr.save.save_info(DIR, srvfolder, plog=f"{username} was released from prison by {name}", db=db)
    await i.response.send_message(f"{username} has been released!")

@bot.command(description="Creates a legal complaint against another player")
async def reportincident(i: di, player: discord.Member, details:str):
    username = i.user
    channel = discord.utils.get(i.message.guild.text_channels, name="incident-reports")
    await channel.send(f"{i.user.nick} reported {player.nick} for `{details}`")
    await i.user.send("Your report was sent.")

@bot.command(description="View a player's prison information")
async def viewsentence(i: di, player: discord.Member):
    server, userid, name, srvfolder, db = await cr.load.get_info(i, DIR) 
    playerid, username = await cr.load.get_user_info(player) 
    prison = db['User Data'][playerid]['prison']
    rgb1, rgb2, rgb3 = random.randint(1, 255), random.randint(1, 255), random.randint(1, 255)
    colour = discord.Colour.from_rgb(rgb1, rgb2, rgb3)
    embed=discord.Embed(title=f"{username}'s Prison Info", description=f"All of {username}'s prison statistics", colour=colour)
    embed.add_field(name="Player", value=prison['player'], inline=True)
    embed.add_field(name="Length", value=f"{prison['length']:,} Days", inline=True)
    embed.add_field(name="Started", value=f"Day {prison['started']:,}", inline=True)
    embed.add_field(name="Original Release", value=f"Day {prison['release']:,}", inline=True)
    embed.add_field(name="Current Release", value=f"Day {prison['newrelease']:,}", inline=True)
    embed.add_field(name="Status", value=prison['status'], inline=True)
    embed.add_field(name="Times", value=prison['times'], inline=True)
    embed.add_field(name="Reason", value=prison['reason'], inline=True)
    await i.response.send_message(embed=embed)

client.run(bt.token)
