import os, discord, json, datetime, typing, random, time, shutil, sys, calendar, asyncio, minestat, re
from asyncrcon import AsyncRCON
from discord.ext import bridge, commands, tasks
from dateutil.relativedelta import relativedelta

Dir = os.getcwd()

intents, intents.members, intents.guilds = discord.Intents.all(), True, True

AsyncRCON.__init__(AsyncRCON, '192.168.1.64:25563', 'VerySecure', max_command_retries=1)
rcon = AsyncRCON('192.168.1.64:25563', "VerySecure")

token = "MTI1OTM2MDAzNjY2NTI5NDkzOQ.G-Lvbq.zpUol7AmWZvqhYsln0ak91PHGmCEzJtLdqzR6A"
bot = bridge.Bot(command_prefix="&", help_command=None, case_insensitive=True, intents=intents, sync_commands=True)

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="Use &help for the wiki!"))
    await rcon.open_connection()
    print("Bot online!")
    
@bot.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, name="Applicant")
    await member.add_roles(role)

#Ease Of Use Commands
async def get_info(ctx):
    server, userid, name = ctx.guild.id, str(ctx.author.id), ctx.author.nick
    srvfolder = f"{Dir}/discord/{server}"
    with open(f"{srvfolder}/maindb.json", 'r+') as f:
        db = json.load(f)
    if not name:
        name = ctx.author.display_name
    return server, userid, name, srvfolder, db

async def get_user_info(user):
    playerid, username = str(user.id), user.nick
    if not username:
        username = user.display_name
    return playerid, username

async def save_info(srvfolder, blog=None, plog=None, rlog=None, slog=None, db=None):
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
        with open(f'{srvfolder}/shop.txt', 'a') as f:
            f.write(f"{dtprint}: {slog}\n")
    if db != None:
        with open(f'{srvfolder}/maindb.json', 'r+') as f:
            f.seek(0)
            json.dump(db, f)
            f.truncate()
            
async def change_inflation(srvfolder, db):
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
    averagebal=round(totalmoney/(len(datalist)-emptyuser),4)
    if averagebal >= 0:
        inflation = round((averagebal/50000)**.25,4)
    else:
        inflation = 0
    if inflation <= .01:
        inflation = .01
    db['Misc Data']['inflation'] = inflation
    await save_info(srvfolder, blog=f"Inflation rate changed to {round(inflation*100,2):,}%", db=db)

#Base Commands
@bot.command()
async def addbase(ctx, x: int, y: int, z: int, dimension = "Overworld"):
    server, userid, name, srvfolder, db = await get_info(ctx)
    base = db['User Data'][userid]['base']
    dimensions = ['Overworld', 'Nether', 'End', 'The End']
    if x == 0 and y == 0 and z == 0:
        await ctx.respond("You can't set your base there.")
    elif abs(x) >= 29999984 or y <= -64 or y >= 320 or abs(z) >= 29999984:
        await ctx.respond("Those coordinates are outside of the current build zone. (±29,999,984, -63/319, ±29,999,984).")
    elif not dimension.title() in dimensions:
        await ctx.respond("The current dimensions are: Overworld, Nether, End (or The End). Defaults to 'Overworld' if excluded from command.")
    elif base['x'] == 0 and base['y'] == 0 and base['z'] == 0:
        if dimension.title() == "End":
            dimension = 'The End'
        db['User Data'][userid]['base'] = {"x": x, "y": y, "z": z, "dimension": dimension.title()}
        await rcon.command(f'dmarker add icon:house id:{name} label:"{name}\'s Base" x:{x} y:{y} z:{z} world:SMG-SMP_{dimension.lower().replace(" ", "_")}')
        await save_info(srvfolder, db=db)
        await ctx.message.delete()
        await ctx.send(f"{ctx.author.mention}, your base cords are now set to `{x} {y} {z}` in the dimension `{dimension.title()}`.")
    else:
        await ctx.respond("You already have a base set up! Use &viewBase to see it, or &editBase to change it.")
        
@bot.command()
async def editbase(ctx, x: int, y: int, z: int, dimension = 'Overworld'):
    server, userid, name, srvfolder, db = await get_info(ctx)
    base = db['User Data'][userid]['base']
    dimensions = ['Overworld', 'Nether', 'End', 'The End']
    if dimension.title() == "End":
        dimension = 'The End'
    if x == 0 and y == 0 and z == 0:
        await ctx.respond("You can't set your base there.")
    elif abs(x) >= 29999984 or y <= -64 or y >= 320 or abs(z) >= 29999984:
        await ctx.respond("Those coordinates are outside of the current build zone. (±29,999,984, -63/319, ±29,999,984).")
    elif base['x'] == 0 and base['y'] == 0 and base['z'] == 0:
        await ctx.respond(f"You have no base to edit. Add one with `&addBase {x} {y} {z}`!")
    elif base['x'] == x and base['y'] == y and base['z'] == z and dimension.title() == base['dimension']:
        await ctx.respond("Your base is already set there!")
    elif not dimension.title() in dimensions:
        await ctx.respond("The current dimensions are: Overworld, Nether, End (or The End). Defaults to 'Overworld' if excluded from command.")
    else:
        db['User Data'][userid]['base'] = {"x": x, "y": y, "z": z, "dimension": dimension.title()}
        await rcon.command(f'dmarker delete id:{name}')
        await rcon.command(f'dmarker add icon:house id:{name} label:"{name}\'s Base" x:{x} y:{y} z:{z} world:SMG-SMP_{dimension.lower().replace(" ", "_")}')
        await save_info(srvfolder, db=db)
        await ctx.message.delete()
        await ctx.send(f"{ctx.author.mention}, your base cords are now set to `{x} {y} {z}` in the dimension `{dimension.title()}`.")

@bot.command()
async def removebase(ctx):
    server, userid, name, srvfolder, db = await get_info(ctx)
    base = db['User Data'][userid]['base']
    if base['x'] == 0 and base['y'] == 0 and base['z'] == 0:
        await ctx.respond("You already don't have a base saved.")
    else:
        db['User Data'][userid]['base'] = {"x": 0, "y": 0, "z": 0, "dimension": "Overworld"}
        await rcon.command(f'dmarker delete id:{name}')
        await save_info(srvfolder, db=db)
        await ctx.message.delete()
        await ctx.send(f"{ctx.author.mention}, you have successfully removed your base.")

@bot.command()
async def viewbase(ctx, player: discord.Member):
    server, userid, name, srvfolder, db = await get_info(ctx)
    playerid, username = await get_user_info(player)
    base = db['User Data'][str(playerid)]['base']
    if base['x'] == 0 and base['y'] == 0 and base['z'] == 0:
        await ctx.respond("This player doesn't have a base saved. Ask them to add it!")
    else:
        await ctx.message.delete()
        await ctx.send(f"{ctx.author.mention}, {username}'s base is `{base['x']} {base['y']} {base['z']}` in the dimension `{base['dimension']}`.")

#Database Commands
@bot.command()
@commands.has_role("Bot Admin")
async def addserver(ctx):
    path = f"{Dir}/discord/{ctx.guild.id}"
    if os.path.exists(f"{path}/maindb.json"):
        await ctx.respond("This server is already active.")
        return
    os.makedirs(path)
    open(f"{path}/banklog.txt", "x")
    open(f"{path}/prisonlog.txt", "x")
    open(f"{path}/rconlog.txt", "x")
    open(f"{path}/maindb.json", "x")
    with open(f"{path}/maindb.json", "r+") as f:
        data = {"Misc Data": {"day": 0, "inflation": 0, "ip": {"JIP": "Not Yet Setup", "BIP": "Not Yet Setup", "BP": 0}, "lotto": 0, "tax": 0}, "User Data": {}}
        json.dump(data, f)
        f.truncate()
    await ctx.send("Server added!")
    
@bot.command()
async def adduser(ctx, user: discord.Member):
    server, userid, name, srvfolder, db = await get_info(ctx)
    playerid, username = await get_user_info(user)
    if str(playerid) in db['User Data']:
        await ctx.send(f"{username} is already added!")
    else:  
        data = {str(playerid): {"base": {"x": 0, "y": 0, "z": 0, "dimension": "Overworld"}, "economy": {"bank": 0, "clockin": 0, "clockout": 0, "money": 0}, "lotteries": 0, "prison": {"player": f"{username}", "length": 0, "started": 0, "release": 0, "newrelease": 0, "status": "Released", "reason": "Not In Prison", "times": 0}, "shop": {}}}
        db['User Data'].update(data)
        await save_info(srvfolder, db=db)
        await ctx.send(f"Added {username} to the database!")

@bot.command()
@commands.has_role("Bot Admin")
async def listoldservers(ctx):
    pass

@bot.command()
@commands.has_role("Server Owner")
async def resetserver(ctx, username: str=None, *, resetname=None):
    server, userid, name, srvfolder, db = await get_info(ctx)
    if not username:
        await ctx.respond("You need your username as confirmation.")
        return
    if username != name:
        await ctx.respond("That username didn't match yours!")
        return
    if not resetname:
        dt = datetime.datetime.now()
        resetname = dt.strftime("%B %d, %Y")
    try:
        oldfolder = f"{srvfolder}/Old Data/{resetname}"
        os.makedirs(oldfolder)
    except:
        await ctx.respond("You can only use a name one time and symbols aren't allowed. You can try to add numbers at the end.")
        return
    for (root, dirs, files) in os.walk(f"{srvfolder}"):
        for file in files:
            shutil.move(f"{srvfolder}/{file}", f"{oldfolder}")
            await ctx.send(f"{file[:-4]} has been reset!")
        break
    await ctx.message.delete()
    await ctx.invoke(bot.get_command('addserver'))
        
@bot.command()
@commands.has_role("Bot Admin")
async def restoreserver(ctx, username, savename, resetname=None):
    pass

@bot.command()
@commands.has_role("Bot Admin")
async def update(ctx):
    server, userid, name, srvfolder, db = await get_info(ctx)
    for player in db['User Data']:
        db['User Data'][player]['base'].update({"dimension": "Overworld"})
        await save_info(srvfolder, db=db)
    await ctx.respond("Updated")
        
@bot.command()
async def updateuser(ctx, mcuser: discord.Member):
    server, userid, name, srvfolder, db = await get_info(ctx)
    playerid, username = await get_user_info(mcuser)
    if playerid != userid:
        await ctx.respond("You can only run this command on yourself.")
        return
    db['User Data'][userid]['prison']["player"] = name
    await save_info(srvfolder, db=db)

@updateuser.error
async def updateuser_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("No user with that name found. Make sure to set your nickname in Discord to that of your new Minecraft username.")

#Economy Commands
@bot.command()
@commands.has_role("Economy Admin")
async def addmoney(ctx, player: discord.Member, amount: float):
    server, userid, name, srvfolder, db = await get_info(ctx)
    playerid, username = await get_user_info(player)
    economy = db['User Data'][str(playerid)]['economy']
    economy['bank'] += round(amount, 2)
    db['User Data'][str(playerid)]['economy'] = economy
    await save_info(srvfolder, blog=f"Added ${round(amount,2):,} to {player.nick}'s bank account.", db=db)
    await ctx.message.delete()

@bot.command()
async def bank(ctx, transaction, amount: float=None):
    server, userid, name, srvfolder, db = await get_info(ctx)
    economy = db['User Data'][userid]['economy']
    money, Bank = economy['money'], economy['bank']
    if amount < 0.01:
        await ctx.respond("You can only transfer a minimum of 1 cent.")
        return
    if transaction.lower() == "deposit":
        if money < round(amount, 2):
            missing = round(amount-money,2)
            await ctx.author.send(f"You don't have enough cash to put into your bank account. You need `${missing:,}` more.")
            await ctx.message.delete()
        else:
            nmoney, nbank = round(money-amount,2), round(Bank+amount,2)
            economy['money'], economy['bank'] = nmoney, nbank
            db['User Data'][userid]['economy'] = economy
            await save_info(srvfolder, blog=f"{name} deposited ${round(amount,2):,}")
            await change_inflation(srvfolder, db)
            await ctx.message.delete()
    elif transaction.lower() == "view":
        await ctx.author.send(f"You have `${round(Bank, 2):,}` in the bank and `${round(money, 2):,}` in cash for a total of `${round(money+Bank, 2):,}`.")
    elif transaction.lower() == "withdraw":
        if Bank < round(amount, 2):
            missing = round(amount-Bank,2)
            await ctx.author.send(f"You don't have enough money in your bank account to take cash out. You need `${missing:,}` more.")
            await ctx.message.delete()
        else:
            nmoney, nbank = round(money+amount,2), round(Bank-amount,2)
            economy['money'], economy['bank'] = nmoney, nbank
            db['User Data'][userid]['economy'] = economy
            await save_info(srvfolder, blog=f"{name} withdrew ${round(amount,2):,}")
            await change_inflation(srvfolder, db)
            await ctx.message.delete()
    else:
        await ctx.respond("The options for this command are `deposit <amount>`, `withdrawal <amount>`, or `view`. *Replace `<amount>` with the number you want.*")

@bot.command()
async def buy(ctx, seller: typing.Optional[discord.Member], amount: typing.Optional[int], *, item: str):
    server, userid, name, srvfolder, db = await get_info(ctx)
    economy, inflation = db['User Data'][userid]['economy'], db['Misc Data']['inflation']
    with open(f"{Dir}/discord/Prices.json", "r+") as f:
        data = json.load(f)
    cost = round((inflation*data[item.title()])*amount,2)
    inflated = round(cost*1.07, 2)
    output = await rcon.command(f"give {name} air")
    if "No player was found" in output:
        await ctx.respond("You need to be in Minecraft to run this command!")
        return
    elif economy['money'] < inflated:
        await rcon.command(f'tellraw {name} "You don\'t have enough money!"')
        return
    async def get_sellers(progress, db, preference = None):
        global datalist
        global total
        users, peeps, datalist, total = db['User Data'], [], [], progress
        for i in users:
            if item.title() in users[i]['shop']:
                if users[i]['shop'][item.title()] > 0:
                    peeps.append(i)
        if preference != None:
            peeps.remove(preference)
            datalist.append([preference, users[preference]['shop'][item.title()]])
        random.shuffle(peeps)
        for person in peeps:
            total += users[person]['shop'][item.title()]
            if round(total) < amount:
                datalist.append([person, users[person]['shop'][item.title()]])
            elif round(total) == amount:
                datalist.append([person, users[person]['shop'][item.title()]])
                break
            else:
                datalist.append([person, amount-(total-users[person]['shop'][item.title()])])
                break
        if round(total) < amount:
            await ctx.respond(f"There isn't enough {item.title()} available. You requested {amount}, but there's only {total}, meaning the shop is {amount-total} short.")
            return "error"
        for row in datalist:
            profit, tax = round(((inflation*data[item.title()])*row[1])*.95, 2), round(((inflation*data[item.title()])*row[1])*.05, 2)
            db['User Data'][row[0]]['shop'][item.title()] -= row[1]
            db['User Data'][row[0]]['economy']['money'] += profit
            db['Misc Data']['tax'] += tax
            salesman = await commands.MemberConverter.convert(commands.MemberConverter, ctx, str(row[0]))
            pid, pname = await get_user_info(salesman)
            await save_info(srvfolder, blog=f"{pname} sold {row[1]} of {item.title()} to {name} for ${profit:,} with ${tax:,} in taxes paid")
        return db
    if not seller:
        txt = None
        db = await get_sellers(0, db)
        if db == "error":
            return
    else:
        playerid, username = await get_user_info(seller)
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
            await save_info(srvfolder, blog=f"{username} sold {amount} of {item.title()} to {name} for ${profit:,} with ${tax:,} in taxes paid")
            txt = None
    await rcon.command(f"give {name} {item.lower().replace(' ', '_')} {amount}")
    db['Misc Data']['tax'] += cost*.07
    db['User Data'][userid]['economy']['money'] -= inflated
    if txt != None:
        await rcon.command(f'tellraw {name} "{txt}"')
    await rcon.command(f'tellraw {name} ["",{{"text":"You paid","color":"gray"}},{{"text":" ${inflated:,}","color":"green"}},{{"text":" for ","color":"gray"}},{{"text":"{amount:,}","color":"aqua"}},{{"text":" of ","color":"gray"}},{{"text":"{item.title()}","color":"white"}}]')
    await save_info(srvfolder, blog=f"{name} bought {amount} of {item} for ${inflated:,}, ${round(cost*.07, 2):,} of which was taxes.")
    await change_inflation(srvfolder, db)

@bot.command()
async def charity(ctx, option1, name=None, option2=None, person: typing.Optional[discord.Member]=None, *, option3=None):
    pass

@bot.command()
async def clockin(ctx):
    server, userid, name, srvfolder, db = await get_info(ctx)
    dt = datetime.datetime.now()
    timestamp, economy = int(round(dt.timestamp())), db['User Data'][userid]['economy']
    if economy['clockin'] != 0:
        await ctx.respond("You need to end your current shift first! `&clockOut`")
        return
    economy['clockin'], economy['clockout'] = timestamp, 0
    db['User Data'][userid]['economy'] = economy
    await save_info(srvfolder, blog=f"{name} clocked into work", db=db)
    await ctx.respond("You clocked into work!")

@bot.command()
async def clockout(ctx):
    server, userid, name, srvfolder, db = await get_info(ctx)
    dt = datetime.datetime.now()
    timestamp, economy = int(round(dt.timestamp())), db['User Data'][userid]['economy']
    if economy['clockin'] == 0:
        await ctx.respond("You need to start a shift first! `&clockIn`")
        return
    earned = timestamp - economy['clockin']
    mathstuff, tax = round((earned/60)*7.5, 2), round(earned*.02, 2)
    earnings = round(mathstuff-tax, 2)
    economy['bank'], economy['clockout'], economy['clockin'] = round(economy['bank']+earnings, 2), timestamp, 0
    db['User Data'][userid]['economy'] = economy
    await save_info(srvfolder, blog=f"{name} clocked out of work and was paid ${earnings:,}")
    await change_inflation(srvfolder, db)
    await ctx.respond("You clocked out of work!")

@bot.command()
@commands.has_any_role("Bot Admin", "Economy Admin")
async def drawlottery(ctx):
    server, userid, name, srvfolder, db = await get_info(ctx)
    entries, pool, udata = [], db['Misc Data']['lotto'], db['User Data']
    for player in db['User Data']:
        for i in range(udata[player]['lotteries']):
            entries.append(player)
        udata[player]['lotteries'] = 0
    if not entries:
        await ctx.respond("No tickets have been purchased yet. Try again a different day.")
    else:
        winner = random.choice(entries)
        username = await commands.MemberConverter.convert(commands.MemberConverter, ctx, str(winner))
        await ctx.respond(f"And the winner for the grand prize of ${pool:,} is:")
        await asyncio.sleep(3)
        await ctx.send("Wait for it...")
        await asyncio.sleep(3)
        await ctx.send(f"{username.mention}!!")
        udata[str(winner)]['economy']['money'] += pool
        db['Misc Data']['lotto'], db['User Data'] = 0, udata
        await save_info(srvfolder, blog=f"{username.nick} won the lottery of ${pool:,}")
        await change_inflation(srvfolder, db)
        await username.send(f"Congratulations on winning ${pool:,}!")
        
@bot.command()
async def enchant(ctx, level: int, *, enchantment: str):
    server, userid, name, srvfolder, db = await get_info(ctx)
    output = await rcon.command(f"data get entity {name} SelectedItem")
    nbt = output.split('data: ')[1]
    await ctx.respond(nbt)
    data_string = re.sub(r'(\d+)([bslfd])', r'\1', nbt)
    await ctx.respond(data_string)
    data_string = re.sub(r'\b(?!minecraft\b)(\w+)(?=\s*):', r'"\1":', data_string)
    await ctx.respond(data_string)
    data_string = data_string.replace("[", "").replace("]", "")
    await ctx.respond(data_string)
    jsons = json.loads(data_string)
    await ctx.respond(jsons)
    response = f"{output}\n\n{nbt}\n\n{jsons}\n\n{jsons['tag']['Enchantments']}\n\n{jsons['tag']['Enchantments']['id']}\n\n{jsons['tag']['Enchantments']['lvl']}"
    await ctx.respond(response)

@bot.command()
async def enchantmentplus(ctx, level: int, *, enchantment: str):
    pass

@bot.command()
@commands.has_any_role("Bot Admin", "Economy Admin")
async def forceclockout(ctx, player: discord.Member, keep: bool):
    server, userid, name, srvfolder, db = await get_info(ctx)
    playerid, username = await get_user_info(player)
    economy, dt = db['User Data'][playerid]['economy'], datetime.datetime.now()
    timestamp = int(round(dt.timestamp()))
    if economy['clockin'] == 0:
        await ctx.respond("This player is already clocked out!")
        return
    elif keep == True:
        earned = timestamp - economy['clockin']
        mathstuff, tax = round((earned/60)*7.5, 2), round(earned*.02, 2)
        earnings = round(mathstuff-tax, 2)
        economy['bank'], economy['clockout'], economy['clockin'] = round(economy['bank']+earnings, 2), timestamp, 0
        db['User Data'][userid]['economy'] = economy
        blog = f"{username} was force clocked out of work and was paid ${earnings:,}"
        msg = f"Clocked {username} out, allowing them to keep their earnings."
        await change_inflation(srvfolder, db)
    else:
        economy['clockout'], economy['clockin'] = timestamp, 0
        db['User Data'][userid]['economy'] = economy
        blog = f"{username} was force clocked out of work and was denied pay"
        
        msg = f"Clocked {username} out, removing their earnings."
    await save_info(srvfolder, blog=blog)
    await ctx.respond(msg)

@bot.command()
async def inflation(ctx):
    server, userid, name, srvfolder, db = await get_info(ctx)
    inflate = db['Misc Data']['inflation']
    if inflate <= 0.75:
        Status = "low"
    elif inflate >= 1.25:
        Status = "high"
    else:
        Status = "normal"
    await ctx.respond(f"The current inflation is `{round(inflate*100,2):,}%` which is {Status}.")

@bot.command()
async def lottery(ctx, amount: int):
    server, userid, name, srvfolder, db = await get_info(ctx)
    lotto, cost, userdata = db['Misc Data']['lotto'], round(20*amount, 2), db['User Data'][userid]
    await ctx.message.delete()
    if amount <= 0:
        await ctx.send("You need to buy at least 1 ticket")
        return
    elif userdata['economy']['money'] >= cost:
        userdata['lotteries'] += amount
        userdata['economy']['money'] -= cost
        pool, db['User Data'][userid] = round(lotto+cost), userdata
        db['Misc Data']['lotto'] = pool
        await ctx.send(f"The lottery has now risen to **${pool:,}**")
        await ctx.author.send(f"You bought {amount} lottery tickets! Good luck!")
        await save_info(srvfolder, blog=f"{name} bought {amount} tickets worth ${cost:,}")
        await change_inflation(srvfolder, db)
    else:
        remaining = round(cost-userdata['economy']['money'], 2)
        await ctx.author.send(f"You don't have enough cash. You need ${remaining:,} more. Perhaps try `&bank withdraw {remaining}`.")

@bot.command()
async def pay(ctx, player: discord.Member, amount:float, *, reason: str = None):
    server, userid, name, srvfolder, db = await get_info(ctx)
    playerid, username = await get_user_info(player)
    peconomy, ueconomy = db['User Data'][playerid]['economy'], db['User Data'][userid]['economy']
    umoney = ueconomy['money']
    if userid == playerid:
        await ctx.send("You cannot pay yourself!")
        return
    if amount <= 0:
        await ctx.send("You cannot send less than $0.01.")
        return
    elif umoney < amount:
        await ctx.message.delete()
        await ctx.author.send(f"You have insufficiant cash. You still need ${round(amount-umoney, 2):,}. Try `&bank withdraw {round(amount-umoney, 2)}`")
        return
    await ctx.message.delete()
    ueconomy['money'] = round(umoney-amount, 2)
    peconomy['money'] += round(amount, 2)
    if not reason:
        await ctx.author.send(f"Payment of ${round(amount, 2):,} to {username} successful.")
        await player.send(f"You have received ${round(amount, 2):,} from {name} in {ctx.guild.name}")
        blog = f"{name} paid {username} ${round(amount, 2):,}."
    else:
        await ctx.author.send(f"Payment of ${round(amount, 2):,} to {username} successful. Payment reason: ```{reason}```")
        await player.send(f"You have received ${round(amount, 2):,} from {name} in {ctx.guild.name}. Payment reason: ```{reason}```")
        blog = f"{name} paid {username} ${round(amount, 2):,}. Reason: \"{reason}\""
    db['User Data'][playerid]['economy'], db['User Data'][userid]['economy'] = peconomy, ueconomy
    await save_info(srvfolder, blog=blog, db=db)

@bot.command()
async def paygovt(ctx, amount: float, reason=None):
    server, userid, name, srvfolder, db = await get_info(ctx)
    economy = db['User Data'][userid]['economy']
    money = economy['money']
    if amount <= 0:
        await ctx.send("You cannot send less than $0.01.")
        return
    elif money < amount:
        await ctx.message.delete()
        await ctx.author.send(f"You have insufficiant cash. You still need ${round(amount-money, 2):,}. Try `&bank withdraw {round(amount-money, 2)}`")
        return
    await ctx.message.delete()
    economy['money'], channel = round(money-amount, 2), discord.utils.get(ctx.message.guild.text_channels, name="server-finances")
    db["Misc Data"]["tax"] += round(amount, 2)
    if not reason:
        await ctx.send("You need a reason for paying the government. (It prevents against government corruption scamming you)")
        return
    else:
        await ctx.author.send(f"Payment of ${round(amount, 2):,} to the government successful. Payment reason: ```{reason}```")
        await channel.send(f"You have received ${round(amount, 2):,} from {name}. Payment reason: ```{reason}```")
        blog = f"{name} paid the government ${round(amount, 2):,}. Reason: \"{reason}\""
    db['User Data'][userid]['economy'] =  economy
    await save_info(srvfolder, blog=blog)
    await change_inflation(srvfolder, db)

@bot.command()
async def price(ctx, amount: typing.Optional[int] = None, *, item: str):
    server, userid, name, srvfolder, db = await get_info(ctx)
    with open(f"{Dir}/discord/Prices.json", "r+") as f:
        data = json.load(f)
        cost = db['Misc Data']['inflation']*data[item.title()]
    if not amount:
        await ctx.respond(f"In the shop, the price of `{item.title()}` is `${round(cost*1.07, 2):,}`, and it will sell for `${round(cost*1.05, 2):,}`.\nIn the void, the price of `{item.title()}` is `${round((cost*1.07)*250, 2):,}`, and it will sell for `${round((cost/4)*.95, 2):,}`.")
    else:
        await ctx.respond(f"In the shop, the price for `{amount}` of `{item.title()}` is `${round((cost*amount)*1.07, 2):,}`, and will sell for `${round((cost*amount)*1.05, 2):,}`.\nIn the void, the price for `{amount}` of `{item.title()}` is `${round(((cost*amount)*1.07)*5, 2):,}`, and will sell for `${round(((cost*amount)/2)*.95, 2):,}`.")

@bot.command()
async def randomitem(ctx):
    with open(f"{Dir}/Discord/Prices.json", "r") as f:
        lines = json.load(f)
        global items
        items = []
        for i in lines:
            items.append(str(i).split(":")[0].replace('"', ""))
    item = random.choice(items)
    await ctx.respond(item)

@bot.command()
@commands.has_role("Economy Admin")
async def removemoney(ctx, player: discord.Member, amount: float):
    server, userid, name, srvfolder, db = await get_info(ctx)
    playerid, username = await get_user_info(player)
    economy = db['User Data'][str(playerid)]['economy']
    economy['bank'] -= round(amount, 2)
    db['User Data'][str(playerid)]['economy'] = economy
    await save_info(srvfolder, blog=f"Removed ${round(amount,2):,} from {player.nick}'s bank account.", db=db)
    await ctx.message.delete()

@bot.command()
async def sell(ctx, amount: int, *, item: str):
    server, userid, name, srvfolder, db = await get_info(ctx)
    output = await rcon.command(f"minecraft:clear {name} {item.replace(' ', '_')} {amount}")
    ingamount = int(output.split()[1])
    await ctx.message.delete()
    if "No player was found" in output:
        await ctx.respond("You need to be in Minecraft to run this command!")
        return
    elif ingamount < amount:
        await rcon.command(f'tellraw {name} "You don\'t have enough of {item.title()}!"')
        await rcon.command(f'give {name} {item.replace(" ", "_")} {ingamount}')
        return
    try:
        db['User Data'][userid]['shop'][item.title()] += amount
    except:
        db['User Data'][userid]['shop'].update({item.title(): amount})
    await rcon.command(f'tellraw {name} ["",{{"text":"You added ","color":"gray"}},{{"text":"{amount:,}","color":"aqua"}},{{"text":" of ","color":"gray"}},{{"text":"{item.title()}","color":"white"}},{{"text":" to your shop.","color":"gray"}}]')
    await save_info(srvfolder, blog=f"{name} added {amount:,} of {item.title()} to their shop", db=db)

@bot.command()
@commands.has_role("Economy Admin")
async def setmoney(ctx, player: discord.Member, amount: float):
    server, userid, name, srvfolder, db = await get_info(ctx)
    playerid, username = await get_user_info(player)
    economy = db['User Data'][str(playerid)]['economy']
    economy['bank'] = round(amount, 2)
    db['User Data'][str(playerid)]['economy'] = economy
    await save_info(srvfolder, blog=f"Set {player.nick}'s bank account to ${round(amount,2):,}.", db=db)
    await ctx.message.delete()
    
@bot.command()
async def shop(ctx, option, player: typing.Optional[discord.Member] = None, amount: typing.Optional[int] = 1, *, item: str = None):
    server, userid, name, srvfolder, db = await get_info(ctx)
    if player != None:
        playerid, username = await get_user_info(player)   
    if option.lower() == "list":
        shop = db['User Data'][playerid]['shop']
        global msg
        msg = f"Starting with the letter \"{item.upper()}\", {username} has:\n"
        for Object in shop:
            if Object[0] == item.upper():
                msg += f"{Object}: {shop[Object]}\n"
        await ctx.respond(msg)
    elif option.lower() == "remove":
        amount = int(amount)
        output = await rcon.command(f"give {name} air")
        if "No player was found" in output:
            await ctx.respond("You need to be in Minecraft to run this command!")
            return
        data = db['User Data'][userid]['shop']
        if not item.title() in data:
            await rcon.command(f'tellraw {name} "You don\'t have any {item} in your shop."')
        elif data[item.title()] < amount:
            await rcon.command(f'tellraw {name} "You do not have enough {item}. You need {data[item]-amount} more."')
        elif amount <= 0:
            await rcon.command(f'tellraw {name} "You cannot remove a negative amount of an item from your shop!"')
        else:
            db['User Data'][userid]['shop'][item.title()] -= amount
        await rcon.command(f"give {name} {item} {amount}")
        await rcon.command(f'tellraw {name} ["",{{"text":"You removed ","color":"gray"}},{{"text":"{amount:,}","color":"aqua"}},{{"text":" of ","color":"gray"}},{{"text":"{item.title()}","color":"white"}},{{"text":" to your shop.","color":"gray"}}]')
        await save_info(srvfolder, blog=f"{name} removed {amount:,} of {item.title()} to their shop")
        await change_inflation(srvfolder, db=db)      
    elif option.lower() == "search":
        global datalist
        global messagelist
        users, datalist, messagelist = db['User Data'], [], []
        for person in users:
            if item.title() in users[person]['shop']:
                datalist.append([person, users[person]['shop'][item.title()]])
        global index
        global message
        index, message = 0, f"Here are the players with {item.title()}: ```"
        for row in datalist:
            username = await commands.MemberConverter.convert(self=commands.MemberConverter, ctx=ctx, argument=str(row[0]))
            messagelist.append(f"{username.nick} has {datalist[index][1]:,}")
            index+=1
        for mline in messagelist:
            message+=f"\n{mline}"
        message+="```"
        await ctx.respond(message)

@bot.command()
@commands.has_role("Government Finances")
async def taxbal(ctx):
    server, userid, name, srvfolder, db = await get_info(ctx)
    await ctx.respond(f"The tax account has `${round(db['Misc Data']['tax'], 2):,}` in it.")
    
@bot.command()
@commands.has_role("Government Finances")
async def taxpay(ctx, player: discord.Member, amount: float, *, reason: str = None):
    server, userid, name, srvfolder, db = await get_info(ctx)
    playerid, username = await get_user_info(player)
    economy, tax, channel = db['User Data'][playerid]['economy'], db['Misc Data']['tax'], discord.utils.get(ctx.message.guild.text_channels, name="server-finances")
    if amount <= 0:
        await ctx.send("You cannot send less than $0.01.")
        return
    elif tax < amount:
        await channel.send(f"The tax account has insufficiant funds. You still need ${round(amount-tax, 2):,}.")
        return
    await ctx.message.delete()
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
    await save_info(srvfolder, blog=blog)
    await change_inflation(srvfolder, db)

@bot.command()
async def voidbuy(ctx, amount: typing.Optional[int] = 1, *, item: str):
    server, userid, name, srvfolder, db = await get_info(ctx)
    economy, inflation = db['User Data'][userid]['economy'], db['Misc Data']['inflation']
    with open(f"{Dir}/discord/Prices.json", "r+") as f:
        data = json.load(f)
    cost = round(((inflation*data[item.title()])*amount)*250,2)
    inflated = round(cost*1.07, 2)
    if economy['money'] < inflated:
        await rcon.command(f'tellraw {name} "You don\'t have enough money!"')
        return
    output = await rcon.command(f"give {name} {item.replace(' ', '_')} {amount}")
    if "No player was found" in output:
        await ctx.respond("You need to be in Minecraft to run this command!")
        return
    db['Misc Data']['tax'] += cost*.07
    db['User Data'][userid]['economy']['money'] -= inflated
    await rcon.command(f'tellraw {name} ["",{{"text":"You paid","color":"gray"}},{{"text":" ${inflated:,}","color":"green"}},{{"text":" for ","color":"gray"}},{{"text":"{amount:,}","color":"aqua"}},{{"text":" of ","color":"gray"}},{{"text":"{item.title()}","color":"white"}}]')
    await ctx.message.delete()
    await save_info(srvfolder, blog=f"{name} bought {amount} of {item} for ${inflated:,}, ${round(cost*.07, 2):,} of which was taxes.")
    await change_inflation(srvfolder, db)

@bot.command()
async def voidsell(ctx, amount: typing.Optional[int] = 1, *, item: str):
    server, userid, name, srvfolder, db = await get_info(ctx)
    inflation = db['Misc Data']['inflation']
    with open(f"{Dir}/discord/Prices.json", "r+") as f:
        data = json.load(f)
    output = await rcon.command(f"minecraft:clear {name} {item.replace(' ', '_')} {amount}")
    ingamount = int(output.split()[1])
    if "No player was found" in output:
        await ctx.respond("You need to be in Minecraft to run this command!")
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
    await ctx.message.delete()
    await save_info(srvfolder, blog=f"{name} sold {amount:,} of {item.title()} for ${round(payment*.95, 2):,} and paid ${tax:,} in taxes")
    await change_inflation(srvfolder, db=db)

@bot.command()
async def wealthy(ctx):
    server, userid, name, srvfolder, db = await get_info(ctx)
    datalist, messagelist = [], []
    for player in db['User Data']:
        economy = db['User Data'][player]['economy']
        datalist.append([player, round(economy['money']+economy['bank'],2)])
    datalist.sort(reverse=True, key=lambda x: x[1])
    global index
    global message
    index, message = 0, "Here are the richest players!\n```"
    for i in range(10):
        try:
            messagelist.append(f"{index+1}: {db['User Data'][str(datalist[index][0])]['prison']['player']}             {datalist[index][1]:,}")
            index+=1
        except:
            pass
    for mline in messagelist:
        message+=f"\n{mline}"
    message+="```"
    await ctx.respond(message)
    
#Miscellaneous Commands
@bot.bridge_command()
@commands.has_role("Bot Admin")
async def amendpoll(ctx, title: str, message: str):
    await ctx.message.delete()
    message = await ctx.send(f"```\n{title}\n```\n```\n{message}\n```\nUse ✅ for Yay, ⚠ to change, and ❎ for Nay")
    await message.add_reaction("✅")
    await message.add_reaction("⚠")
    await message.add_reaction("❎")

@bot.bridge_command()
@commands.has_role("Bot Admin")
async def cmd(ctx, *, command):
    server, userid, name, srvfolder, db = await get_info(ctx)
    output = await rcon.command(f"{command}")
    await save_info(srvfolder, rlog=f"{name} ran the command {command}' with the output: {output}")
    await ctx.respond(output)

@bot.bridge_command()
async def day(ctx):
    output = await rcon.command(f"minecraft:time query day")
    command = output.split(' ')
    day = command[-1]
    await ctx.respond(f"The current day is {day}")

@bot.bridge_command()
async def help(ctx, command=None):
    if not command:
        await ctx.respond("The help page can be found at http://someminegame.com/Main/Commands")
        return
    global index
    index = 0
    commands = ['addBase', 'addMoney', 'addSentence', 'addServer', 'addUser', 'amendPoll', 'bank', 'buy', 'charity', 'clockIn', 'clockOut', 'cmd', 'day', 'drawLottery', 'editBase', 'editSentence', 'enchant', 'enchantmentPlus', 'forceClockOut', 'help', 'ip', 'inflation', 'listOldServers', 'lottery', 'pay', 'payGovt', 'poll', 'price', 'releasePrisoner', 'removeBase', 'removeMoney', 'reportIncident', 'resetServer', 'restoreServer', 'sell', 'setMoney', 'status', 'taxBal', 'taxPay', 'test', 'update', 'viewBase', 'viewSentence', 'voidBuy', 'voidSell', 'wealthy']
    for option in commands:
        if command.lower() == commands[index].lower():
            command = commands[index]
            break
        else:
            index += 1
    if command not in commands:
        await ctx.respond("Your command wasn't found. Check your spelling and make sure the command isn't deprecated and try again.")
    else:
        await ctx.respond(f"https://someminegame.com/Main/Commands/{command}")

@bot.command()
async def ip(ctx, JIP=None, BIP=None, BP:int=None):
    server, userid, name, srvfolder, db = await get_info(ctx)
    ips = db['Misc Data']['ip']
    if not JIP:
        await ctx.respond(f"The server IPs are\n\n Java: `{ips['JIP']}`\nBedrock: `{ips['BIP']}      {ips['BP']}`")
        return
    roles = ctx.author.roles
    admin = discord.utils.get(ctx.message.guild.roles, name='Bot Admin')
    if not admin in roles:
        await ctx.respond("You need to be a Bot Admin to change this setting.")
        return
    if not BP:
        BP = 19132
    await ctx.respond("The ports have been changed.")
    ips['JIP'], ips['BIP'], ips['BP'] = JIP, BIP, BP
    db['Misc Data']['ip'] = ips
    await save_info(srvfolder, db=db)

@bot.bridge_command()
@commands.has_role("Bot Admin")
async def poll(ctx, title: str, message: str, *options):
    if len(options) < 2:
        await ctx.respond("You need at least 2 options!")
        return
    elif len(options) > 10:
        await ctx.respond("You can only have up to 10 options!")
        return
    message_content = f"```{title.upper()}\n\n{message}```\n"
    for option in options:
        message_content += f"```{option}```\n"
    message = await ctx.send(message_content)
    reactions = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    for i in range(len(options)):
        await message.add_reaction(reactions[i])
    
@bot.bridge_command()
@commands.dm_only()
async def scam(ctx):
    output = await rcon.command("minecraft:clear SomeMineGame sugar")
    amount = int(str(output).split(" ")[1])
    await rcon.command(f'minecraft:give SomeMineGame minecraft:sugar{{display:{{Name:\'["",{{"text":"Cocaine","italic":false,"color":"aqua"}}]\',Lore:[\'["",{{"text":"Purest Authentic Quality","italic":false,"color":"green"}}]\']}}}} {amount}')

@bot.bridge_command()
async def status(ctx):
    local = minestat.MineStat('192.168.1.64', 25564)
    Global = minestat.MineStat('java.someminegame.net', 25565, query_protocol="All")
    if local.online == True and Global.online == True:
        message = "online, and is"
    elif local.online == True and Global.online == False:
        message = "online, but is **NOT**"
    elif local.online == False and Global.online == False:
        message = "offline, and is **NOT**"
    await ctx.respond(f"The server is {message} available for people.")

@bot.bridge_command()
async def test(ctx):
    await ctx.respond("The bot is operational!")

#Legal Commands
@bot.command()
@commands.has_role("Prison Guard")
async def addsentence(ctx, player: discord.Member, length: int, *, reason: str):
    server, userid, name, srvfolder, db = await get_info(ctx)
    playerid, username = await get_user_info(player)
    prison = db['User Data'][playerid]['prison']
    output = await rcon.command(f"minecraft:time query day")
    command = output.split(' ')
    day = int(command[-1])
    release = round(day+length)
    if prison['status'] == "Unreleased":
        await ctx.respond(f"{username} is already in prison. If you'd like to make an edit, use `&editSentence {username} {round(prison['newrelease']-(length+day))}`, and if you're trying to release them, use `&releasePrisoner {username}`.")
        return
    db['User Data'][playerid]['prison'] = {"player": username, "length": length, "started": day, "release": release, "newrelease": release, "status": "Unreleased", "reason": reason, "times": round(prison['times']+1)}
    await save_info(srvfolder, plog=f"{username} was sent to prison by {name} for the {round(prison['times']+1)} time for \"{reason}\" and will be released on day {release:,}", db=db)
    await ctx.respond(f"Sentence for {username} created!")

@bot.command()
@commands.has_role("Prison Guard")
async def editsentence(ctx, player: discord.Member, change: int):
    server, userid, name, srvfolder, db = await get_info(ctx)
    playerid, username = await get_user_info(player)
    prison = db['User Data'][playerid]['prison']
    if prison['status'] == "Released":
        await ctx.respond(f"{username} is released from prison and therefore can't have their day edited.")
        return
    if change == 0:
        await ctx.respond("Please use a whole number greator or less than 0")
        return
    schange = 1
    if change < 0:
        text, text1 = "removed", "from"
        schange = round(change*-1)
    else:
        text, text1 = "added", "to"
    db['User Data'][playerid]['prison']['newrelease'] = round(change+prison["newrelease"])
    await save_info(srvfolder, plog=f"{name} {text} {schange:,} days {text1} {username}'s sentence", db=db)
    await ctx.respond(f"Sentence for {username} updated!")

@bot.command()
@commands.has_role("Prison Guard")
async def releaseprisoner(ctx, player: discord.Member):
    server, userid, name, srvfolder, db = await get_info(ctx)
    playerid, username = await get_user_info(player)
    prison = db['User Data'][playerid]['prison']
    output = await rcon.command(f"minecraft:time query day")
    command = output.split(' ')
    day = int(command[-1])
    if prison['status'] == "Released":
        await ctx.respond(f"{username} is already released from prison.")
        return
    if prison['newrelease'] > day:
        await ctx.respond(f"{username} still has {round(prison['newrelease']-day)} days left. If you need to change the release date, use `&editSentence {username} {day-round(prison['newrelease'])}`")
        return
    db['User Data'][playerid]['prison'] = {"player": username, "length": 0, "started": 0, "release": 0, "newrelease": 0, "status": "Released", "reason": "Not In Prison", "times": prison['times']}
    await save_info(srvfolder, plog=f"{username} was released from prison by {name}", db=db)
    await ctx.respond(f"{username} has been released!")

@bot.command()
async def reportincident(ctx, player: discord.Member, *, details):
    username = ctx.author
    await ctx.message.delete()
    channel = discord.utils.get(ctx.message.guild.text_channels, name="incident-reports")
    await channel.send(f"{ctx.author.nick} reported {player.nick} for `{details}`")
    await ctx.author.send("Your report was sent.")

@bot.command()
async def viewsentence(ctx, player: discord.Member):
    server, userid, name, srvfolder, db = await get_info(ctx)
    playerid, username = await get_user_info(player)
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
    await ctx.respond(embed=embed)

bot.run(token)