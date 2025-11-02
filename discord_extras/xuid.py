# All Credit For This Script Goes To Den Delimarsky (@DenDev on YouTube)
# GitHub Source: https://github.com/OpenSpartan/xuid-resolver/tree/main
#
# Minor Modifications Were Made Below

from msal import PublicClientApplication, SerializableTokenCache
import os, atexit, requests
import discord_extras.bot as bt

CLIENT_ID = bt.entraID
SCOPES = ["Xboxlive.signin", "Xboxlive.offline_access"]
XBL_VERSION = "3.0"
TOKEN_CACHE_PATH = "cache.bin"
cache = SerializableTokenCache()

def get(target_gamertag):
    def save_cache():
        if cache.has_state_changed:
            with open(TOKEN_CACHE_PATH, "w") as token_cache_file:
                token_cache_file.write(cache.serialize())

    def request_user_token(access_token):
        ticket_data = {
            "RelyingParty": "http://auth.xboxlive.com",
            "TokenType": "JWT",
            "Properties": {
                "AuthMethod": "RPS",
                "SiteName": "user.auth.xboxlive.com",
                "RpsTicket": f"d={access_token}"}}
        headers = {"x-xbl-contract-version": "1",
            "Content-Type": "application/json"}
        response = requests.post(
            url="https://user.auth.xboxlive.com/user/authenticate",
            json=ticket_data,
            headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def request_xsts_token(user_token):
        ticket_data = {
            "RelyingParty": "http://xboxlive.com",
            "TokenType": "JWT",
            "Properties": {
                "UserTokens": [user_token],
                "SandboxId": "RETAIL"}}
        headers = {
            "x-xbl-contract-version": "1",
            "Content-Type": "application/json"}
        url = "https://xsts.auth.xboxlive.com/xsts/authorize"
        response = requests.post(url, json=ticket_data, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def search_for_user(gamertag, token):
        headers = {
            "x-xbl-contract-version": "3",
            "Content-Type": "application/json",
            "Authorization": token,
            "Accept-Language": "en-us"}
        url = f"https://peoplehub.xboxlive.com/users/me/people/search/decoration/detail,preferredColor?q={gamertag}&maxItems=25"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def get_gamertags(data):
        if 'people' in data:
            for person in data['people']:
                gamertag = person.get('gamertag', 'Unknown Gamertag')
                xuid = person.get('xuid', 'Unknown XUID')
                if xuid == None:
                    return None, None
                else:
                    return hex(int(xuid))[2:], gamertag
    if os.path.exists(TOKEN_CACHE_PATH):
        with open(TOKEN_CACHE_PATH, "r") as token_cache_file:
            cache.deserialize(token_cache_file.read())     
    atexit.register(save_cache)
    app = PublicClientApplication(
        CLIENT_ID,
        authority="https://login.microsoftonline.com/consumers",
        token_cache=cache)
    accounts = app.get_accounts()
    result = None
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
    else:
        result = app.acquire_token_interactive(SCOPES)
    if result and 'access_token' in result:
        ticket = request_user_token(result['access_token'])
        if ticket:
            user_token = ticket.get('Token')
            user_hash = ticket.get('DisplayClaims', {}).get('xui', [{}])[0].get('uhs')
            xsts_ticket = request_xsts_token(user_token)
            if xsts_ticket:
                xsts_token = xsts_ticket.get('Token')
                xbl_token = f'XBL{XBL_VERSION} x={user_hash};{xsts_token}'
                user_data = search_for_user(target_gamertag, xbl_token)
                if user_data:
                    return get_gamertags(user_data)