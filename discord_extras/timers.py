import json, aiomcrcon, os, datetime, discord, asyncio
from . import bot as bt
from . import common_resources as cr

global Worked
Worked = 5

rcon = aiomcrcon.Client(bt.MC.local_domain, bt.MC.port, bt.MC.password)    

# Bot Setup
class timers():                            
    async def checkstat(client:discord.Client, Dir, rcon: aiomcrcon.Client):  
        global Worked
        worked = Worked
        async def attempt():
            await rcon.send_cmd("time query day")
            global Worked
            Worked = True
        try:
            if worked == False:
                try:
                    await rcon.connect(5)
                    await attempt()
                except:
                    pass
            else:
                await attempt()
        except Exception as e:
            print(e)
            Worked = False
        role = discord.utils.get(client.get_guild(bt.IDS.main).roles, name="Notices")
        if worked == Worked:
            pass
        elif worked == 5:
            pass
        elif Worked == False:
            await rcon.close()
            msg = discord.utils.get(client.get_guild(bt.IDS.main).channels, name="status")
            await msg.send(f"The server is **Inaccessible!**\nConnection attempts will happen every 60 seconds.\n\n<t:{int(datetime.datetime.timestamp(datetime.datetime.now()))}:R>\n\n{role.mention}")
            #print((f"The server is **Inaccessible!**\nConnection attempts will happen every 60 seconds.\n\n<t:{int(datetime.datetime.timestamp(datetime.datetime.now()))}:R>"))
            
        elif Worked == True:
            msg = discord.utils.get(client.get_guild(bt.IDS.main).channels, name="status")
            await msg.send(f"The server is **accessible** again!\n\n{role.mention}")
            #print(f"The server is **accessible** again!")
            
    async def mc_irl_time(rcon: aiomcrcon.Client):
        dt = datetime.datetime.now()
        seconds = (dt - dt.replace(hour=0,minute=0,second=0)).total_seconds()
        converted = (seconds/3.6)-6000
        if converted < 0:
            converted+=24000
        try:
            await rcon.send_cmd(f"time set {int(converted)}")
        except:
            pass