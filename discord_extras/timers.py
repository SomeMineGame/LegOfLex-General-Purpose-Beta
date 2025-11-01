import json, asyncrcon, os, datetime, discord
from . import bot as bt
from . import common_resources as cr

global Worked
Worked = 5

class timers():
    async def autoclockout(client: discord.Client, Dir, rcon: asyncrcon.AsyncRCON):
        for files, dirs, root in os.walk(f"{Dir}/discord"):
            for q in dirs:
                with open(f"{Dir}/discord/{q}/maindb.json", "r+") as f:
                    data = json.load(f)
                    for player in data['User Data']:
                        if data["User Data"][player]['economy']['clockin'] != 0:
                            guild = client.get_guild(int(q))
                            username = guild.get_member(int(player)).nick
                            output = await rcon.command(f"give {username} air")
                            if "No player was found" in output:
                                economy, dt = data['User Data'][player]['economy'], datetime.datetime.now()
                                timestamp = int(round(dt.timestamp()))
                                earned = timestamp - economy['clockin']
                                mathstuff, tax = round((earned/60)*7.5, 2), round(earned*.02, 2)
                                earnings = round(mathstuff-tax, 2)
                                economy['bank'], economy['clockout'], economy['clockin'] = round(economy['bank']+earnings, 2), timestamp, 0
                                data['User Data'][player]['economy'] = economy
                                blog = f"{username} was automatically clocked out of work and was paid ${earnings:,}"
                                channel = discord.utils.get(guild.text_channels, name="bot-commands")
                                await channel.send(f"{guild.get_member(int(player)).mention}, you have been clocked out automatically.")
                                await cr.save.change_inflation(Dir, f"{Dir}/discord/{q}", data)
                                await cr.save.save_info(Dir, f"{Dir}/discord/{q}", blog, data)
            break
                                
    async def checkstat(client:discord.client, Dir, rcon: asyncrcon.AsyncRCON):  
        global Worked
        worked = Worked
        async def attempt():
            await rcon.command("time query day")
            global Worked
            Worked = True
        try:
            if worked == False:
                try:
                    await rcon.open_connection()
                    await attempt()
                except:
                    pass
            else:
                await attempt()
        except:
            Worked = False
        if worked == Worked:
            pass
        elif worked == 5:
            pass
        elif Worked == False:
            rcon.close()
            # msg = discord.utils.get(client.get_guild(sr.IDS.hub).text_channels, name="status")
            # msg = await msg.send(f"The server is **Inaccessible!**\nConnection attempts will happen every 10 seconds.\n\n<t:{int(datetime.datetime.timestamp(datetime.datetime.now()))}:R>")
            print((f"The server is **Inaccessible!**\nConnection attempts will happen every 10 seconds.\n\n<t:{int(datetime.datetime.timestamp(datetime.datetime.now()))}:R>"))
            # await msg.publish()
            
        elif Worked == True:
            # msg = discord.utils.get(client.get_guild(sr.IDS.hub).text_channels, name="status")
            # msg = await msg.send(f"The server is **accessible** again!")
            print(f"The server is **accessible** again!")
            # await msg.publish()