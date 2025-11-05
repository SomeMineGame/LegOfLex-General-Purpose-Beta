import json, asyncrcon, os, datetime, discord
from . import bot as bt
from . import common_resources as cr

class timers():

    async def mc_irl_time(rcon: asyncrcon.AsyncRCON):
            dt = datetime.datetime.now()
            seconds = (dt - dt.replace(hour=0,minute=0,second=0)).total_seconds()
            converted = (seconds/3.6)-6000
            if converted < 0:
                converted+=24000
            try:
                await rcon.command(f"time set {int(converted)}")
            except:
                pass
            
    async def permit_removal(Dir):
        dt = datetime.datetime.now()
        if dt.hour == 0 and dt.minute == 0:
            current = dt.strftime("%m-%d")
            for _, servers, _ in os.walk(f"{Dir}/discord"):
                for server in servers:
                    with open(f"{Dir}/discord/{server}/maindb.json", 'r+') as f:
                        data = json.load(f)
                    for player in data['User Data']:
                        for permit in data['User Data'][player]['Permits']:
                            pd = data['User Data'][player]['Permits'][permit]
                            if pd['length'] == 0:
                                return
                            cs, ps = current.split("-"), pd['last-removed'].split("-")
                            if (ps[0] != cs[0]) and (ps[1] == cs[1]):
                                pd['length'] -= 1
                                pd['last-removed'] = current
                            data['User Data'][player]['Permits'][permit] = pd
                            await cr.save.save_info(Dir, srvfolder=f"{Dir}/discord/{server}", db=data)