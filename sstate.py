import os, json
from time import sleep
from threading import Thread

shutdownsignal = False

if os.path.isfile("data.db"):
    db = json.load(open("data.db"))
    try:
        db = json.load(open("data.db"))
        db["Options"]["BotToken"]
        db["Options"]["RethinkURL"]
        db["Users"]
    except (ValueError, KeyError, json.decoder.JSONDecodeError):
        print("options.json not valid, fix the file or delete this file")
        exit()
else:
    db = {}
    print("File data.db doesn't exist, making new one")
    db["Options"] = {}
    db["Users"] = {}
    print("What is your bot token? You grab this from discord.com/developers/")
    db["Options"]["BotToken"] = input(">")
    print("What is the Rethink URL? Ex: https://rethinkurlhere.com/some/path/")
    db["Options"]["RethinkURL"] = input(">")
    json.dump(db, open("data.db", "w"), indent=4)

def saveState():
    json.dump(db, open("data.db", "w"), indent=4)

def saveLoopFunc():
    global shutdownsignal
    time=0
    while not shutdownsignal:
        if time > 60:
            saveState(db)
            time=0
        else:
            sleep(1)
    asyncio.run(client.close())
        
def saveLoop():
    save_daemon = Thread(target=saveLoopFunc, daemon=True, name='SaveLoop')
    save_daemon.start()

def save_and_exit(*args):
    print("Sent shutdown signal")
    shutdownsignal = True
    print("Saving...")
    saveState()
    print("Done")
    exit(1)