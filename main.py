import nextcord
import signal
from datetime import datetime
# sstate is a auto save that runs on another thread.
# This provides a dictonary called db and it saves and loads it
from sstate import *
from nextcord.ext import commands, menus
from RethinkAPI import rethink

# handles quiting the bot and saves
signal.signal(signal.SIGINT, save_and_exit)
print("Press CTRL+C to stop server")

rethink.url = db["Options"]["RethinkURL"]

intents = nextcord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)

class Register(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(
            "Link Rethink to your account",
            timeout=5 * 60,  # 5 minutes
        )

        self.username = nextcord.ui.TextInput(
            label="Username",
            placeholder="Username",
            style=nextcord.TextInputStyle.short,
            required=True,
        )
        self.add_item(self.username)

        self.password = nextcord.ui.TextInput(
            label="Password",
            placeholder="Password",
            style=nextcord.TextInputStyle.short,
            required=True,
        )
        self.add_item(self.password)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        try:
            auth = rethink.auth(self.username.value, self.password.value) 
        except rethink.loginIncorrectErr:
            await interaction.send("Credentials are incorrect")
        except rethink.connectionFailed:
            await interaction.send("A server side error happened")
        else:
            try:
                db["Users"][str(interaction.user.id)]
            except KeyError:
                db["Users"][str(interaction.user.id)] = {}
            db["Users"][str(interaction.user.id)]["Username"] = self.username.value
            db["Users"][str(interaction.user.id)]["Password"] = self.password.value
            db["Users"][str(interaction.user.id)]["Auth"] = auth
            response = f"{interaction.user.mention} has linked their Rethink account"
            await interaction.send(response)

class MySource(menus.ListPageSource):
    def __init__(self, data):
        super().__init__(data, per_page=4)

    async def format_page(self, menu, entries):
        offset = menu.current_page * self.per_page
        return '\n'.join(f'{i}. {v}' for i, v in enumerate(entries, start=offset))


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.slash_command(description="Manages Rethink classes")
async def rt(interaction: nextcord.Interaction):
    pass

@rt.subcommand(description="Links Rethink to your account")
async def login(interaction: nextcord.Interaction):
    modal = Register()
    await interaction.response.send_modal(modal)

@rt.subcommand(description="Unlinks Rethink from your account")
async def logout(interaction: nextcord.Interaction):
    try:
        del db["Users"][str(interaction.user.id)]
    except KeyError:
        await interaction.response.send_message("Can't log out a user who isn't even logged in")
    else:
        await interaction.response.send_message("Removed your account!")

@rt.subcommand(name='list', description="Lists Rethink classes")
async def _list(interaction: nextcord.Interaction):
    pass

@_list.subcommand(description="Shows enrolled classes")
async def local(interaction: nextcord.Interaction):
    try:
        classes = rethink.getEnrolledClasses(db["Users"][str(interaction.user.id)]["Auth"])
    except rethink.connectionFailed:
         await interaction.response.send_message("Server side error occured")
    except rethink.sessionAuthError:
        try:
            db["Users"][str(interaction.user.id)]["Auth"] = rethink.auth(db["Users"][str(interaction.user.id)]["Username"], db["Users"][str(interaction.user.id)]["Password"])
        except rethink.loginIncorrectErr:
            await interaction.response.send_message("Password seemed to have changed, try re-registering")
        except rethink.connectionFailed:
            await interaction.response.send_message("Server side error occured")
        else:
            try:
                classes = rethink.getEnrolledClasses(db["Users"][str(interaction.user.id)]["Auth"])
            except:
                await interaction.response.send_message("Server side error occured")
                raise("f")
    else:
        if len(classes) == 0:
            await interaction.response.send_message("No classes this week")
        else:
            finout = ""
            selday = ""
            for c in classes:
                if selday != c["date"]:
                    finout = finout + "**```"+datetime.strptime(c["date"], '%Y-%m-%d').strftime("%A")+" "+c["date"]+"```**\n"
                    selday = c["date"]
                finout = finout + "`"
                if c["type"].lower() != "open":
                    finout = finout+"["+c["type"]+"]"
                finout = finout+"("+c["classid"]+")"
                finout = finout+"["+c["firstname"]+" "+c["lastname"]+"] "
                finout = finout+c["classname"]
                finout = finout+" in "+c["room"]
                finout = finout + "`"
                finout = finout + "\n"
            temp = ""
            for peice in finout.split("\n"):
                if len(temp)+len(peice) > 1500:
                    await interaction.response.send_message(temp)
                    temp=""
                temp = temp + peice + "\n"
            if temp != "":
                await interaction.response.send_message(temp)

@_list.subcommand(description="Shows avaliable classes")
async def pub(interaction: nextcord.Interaction):
    try:
        classes = rethink.getAllClasses(db["Users"][str(interaction.user.id)]["Auth"])
    except rethink.connectionFailed:
         await interaction.response.send_message("Server side error occured")
    except rethink.sessionAuthError:
        try:
            db["Users"][str(interaction.user.id)]["Auth"] = rethink.auth(db["Users"][str(interaction.user.id)]["Username"], db["Users"][str(interaction.user.id)]["Password"])
        except rethink.loginIncorrectErr:
            await interaction.response.send_message("Password seemed to have changed, try re-registering")
        except rethink.connectionFailed:
            await interaction.response.send_message("Server side error occured")
        else:
            try:
                classes = rethink.getAllClasses(db["Users"][str(interaction.user.id)]["Auth"])
            except:
                await interaction.response.send_message("Server side error occured")
                raise("f")
    else:
        if len(classes) == 0:
            await interaction.response.send_message("No classes this week")
        else:
            finout = ""
            selday = ""
            for c in classes:
                if selday != c["date"]:
                    finout = finout + "**```"+datetime.strptime(c["date"], '%Y-%m-%d').strftime("%A")+" "+c["date"]+"```**\n"
                    selday = c["date"]
                finout = finout + "`"
                if c["type"].lower() != "open":
                    finout = finout+"["+c["type"]+"]"
                finout = finout+"("+c["classid"]+")"
                finout = finout+"["+c["firstname"]+" "+c["lastname"]+"] "
                finout = finout+c["classname"]
                finout = finout+" in "+c["room"]
                finout = finout + "`"
                finout = finout + "\n"
            await interaction.response.send_message("Creating thread...")
            thread = await interaction.channel.create_thread(name='All classes', type=nextcord.ChannelType.public_thread)
            await thread.send(interaction.user.mention)
            temp = ""
            for peice in finout.split("\n"):
                if len(temp)+len(peice) > 1500:
                    await thread.send(temp)
                    temp=""
                temp = temp + peice + "\n"
            if temp != "":
                await thread.send(temp)

bot.run(db["Options"]["BotToken"])
