import nextcord
from datetime import datetime
from sstate import *
from nextcord.ext import commands
from RethinkAPI import rethink

rethink.url = db["Options"]["RethinkURL"]

intents = nextcord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)
autodeleteAfter=120

class CurrentClasses(nextcord.ui.Select):
    def __init__(self, classes):
        selectoptions = []
        for c in classes:
            selectoptions.append(
                nextcord.SelectOption(label=c["classname"], value=c["classid"], description="["+datetime.strptime(c["date"], '%Y-%m-%d').strftime("%A")+" in "+c["room"]+"] "+c["firstname"]+" "+c["lastname"]+"'s class has "+c["openseats"]+" seats left")
            )
        super().__init__(placeholder="Select to remove", min_values=1, max_values=1, options=selectoptions)
    async def callback(self, interaction: nextcord.Interaction):
        try:
            rethink.removeClass(db["Users"][str(interaction.user.id)]["Auth"], self.values[0])
        except rethink.connectionFailed:
             await interaction.response.send_message("Server side error occured", ephemeral=True)
        except rethink.sessionAuthError:
            try:
                db["Users"][str(interaction.user.id)]["Auth"] = rethink.auth(db["Users"][str(interaction.user.id)]["Username"], db["Users"][str(interaction.user.id)]["Password"])
            except rethink.loginIncorrectErr:
                await interaction.response.send_message("Password seemed to have changed, try re-registering", ephemeral=True)
            except rethink.connectionFailed:
                await interaction.response.send_message("Server side error occured", ephemeral=True)
            else:
                try:
                    rethink.removeClass(db["Users"][str(interaction.user.id)]["Auth"], self.values[0])
                except:
                    await interaction.response.send_message("Could not log you in!", ephemeral=True)
                    raise("Thats no good")
                else:
                    saveState()
        except KeyError:
            await interaction.response.send_message("You don't seem to be logged in", ephemeral=True)
        await interaction.response.send_message("Removed class!", ephemeral=True)
        await interaction.edit(view=None)

class CurrentClassesView(nextcord.ui.View):
    def __init__(self, classes):
        super().__init__()
        self.add_item(CurrentClasses(classes))

class AddClasses(nextcord.ui.Select):
    def __init__(self, classes):
        selectoptions = []
        for c in classes:
            selectoptions.append(
                nextcord.SelectOption(label=c["classname"], value=c["classid"], description="["+datetime.strptime(c["date"], '%Y-%m-%d').strftime("%A")+" in "+c["room"]+"] "+c["firstname"]+" "+c["lastname"]+"'s class has "+c["openseats"]+" seats left")
            )
        super().__init__(placeholder="Select to add", min_values=1, max_values=1, options=selectoptions)
    async def callback(self, interaction: nextcord.Interaction):
        try:
            rethink.addClass(db["Users"][str(interaction.user.id)]["Auth"], self.values[0])
        except rethink.connectionFailed:
             await interaction.response.send_message("Server side error occured", ephemeral=True)
        except rethink.sessionAuthError:
            try:
                db["Users"][str(interaction.user.id)]["Auth"] = rethink.auth(db["Users"][str(interaction.user.id)]["Username"], db["Users"][str(interaction.user.id)]["Password"])
            except rethink.loginIncorrectErr:
                await interaction.response.send_message("Password seemed to have changed, try re-registering", ephemeral=True)
            except rethink.connectionFailed:
                await interaction.response.send_message("Server side error occured", ephemeral=True)
            else:
                try:
                    rethink.addClass(db["Users"][str(interaction.user.id)]["Auth"], self.values[0])
                except:
                    await interaction.response.send_message("Could not log you in!", ephemeral=True)
                    raise("Thats no good")
                else:
                    saveState()
        except KeyError:
            await interaction.response.send_message("You don't seem to be logged in", ephemeral=True)
        await interaction.response.send_message("Added class!", ephemeral=True)
        await interaction.edit(view=None)

class AddClassesView(nextcord.ui.View):
    def __init__(self, classes):
        super().__init__()
        self.add_item(AddClasses(classes))

class Register(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(
            "Link Rethink to your account",
            timeout=5 * 60,
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
            await interaction.send("Credentials are incorrect", ephemeral=True)
        except rethink.connectionFailed:
            await interaction.send("A server side error happened", ephemeral=True)
        else:
            try:
                db["Users"][str(interaction.user.id)]
            except KeyError:
                db["Users"][str(interaction.user.id)] = {}
            db["Users"][str(interaction.user.id)]["Username"] = self.username.value
            db["Users"][str(interaction.user.id)]["Password"] = self.password.value
            db["Users"][str(interaction.user.id)]["Auth"] = auth
            saveState()
            response = f"{interaction.user.mention} has linked their Rethink account"
            await interaction.send(response, ephemeral=True)
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
        await interaction.response.send_message("Can't log out a user who isn't even logged in", ephemeral=True)
    else:
        await interaction.response.send_message("Removed your account!", ephemeral=True)
        saveState()

@rt.subcommand(description="Adds Rethink classes")
async def add(interaction: nextcord.Interaction):
    try:
        classes = rethink.getAllClasses(db["Users"][str(interaction.user.id)]["Auth"])
    except rethink.connectionFailed:
         await interaction.response.send_message("Server side error occured", ephemeral=True)
    except rethink.sessionAuthError:
        try:
            db["Users"][str(interaction.user.id)]["Auth"] = rethink.auth(db["Users"][str(interaction.user.id)]["Username"], db["Users"][str(interaction.user.id)]["Password"])
        except rethink.loginIncorrectErr:
            await interaction.response.send_message("Password seemed to have changed, try re-registering", ephemeral=True)
        except rethink.connectionFailed:
            await interaction.response.send_message("Server side error occured", ephemeral=True)
        else:
            try:
                classes = rethink.getAllClasses(db["Users"][str(interaction.user.id)]["Auth"])
            except:
                await interaction.response.send_message("Could not log you in!", ephemeral=True)
                raise("Thats no good")
            else:
                saveState()
    except KeyError:
        await interaction.response.send_message("You don't seem to be logged in", ephemeral=True)
    else:
        if len(classes) == 0:
            await interaction.response.send_message("No classes this week", ephemeral=True)
        else:
            await interaction.response.send_message("Generating... (Frick you discord for limiting dropdowns)", delete_after=5)
            def divide_chunks(_list, chuncksize):
                for i in range(0, len(_list), chuncksize):
                    yield _list[i:i + chuncksize]
            pagelist = divide_chunks(classes, 24)
            for num, clist in enumerate(pagelist):
                view = AddClassesView(clist)
                await interaction.channel.send(view=view, delete_after=autodeleteAfter)
            await interaction.channel.send('Done!', delete_after=5)
            

@rt.subcommand(description="Removes Rethink classes")
async def remove(interaction: nextcord.Interaction):
    try:
        classes = rethink.getEnrolledClasses(db["Users"][str(interaction.user.id)]["Auth"])
    except rethink.connectionFailed:
         await interaction.response.send_message("Server side error occured", ephemeral=True)
    except rethink.sessionAuthError:
        try:
            db["Users"][str(interaction.user.id)]["Auth"] = rethink.auth(db["Users"][str(interaction.user.id)]["Username"], db["Users"][str(interaction.user.id)]["Password"])
        except rethink.loginIncorrectErr:
            await interaction.response.send_message("Password seemed to have changed, try re-registering", ephemeral=True)
        except rethink.connectionFailed:
            await interaction.response.send_message("Server side error occured", ephemeral=True)
        else:
            try:
                classes = rethink.getEnrolledClasses(db["Users"][str(interaction.user.id)]["Auth"])
            except:
                await interaction.response.send_message("Could not log you in!", ephemeral=True)
                raise("Thats no good")
            else:
                saveState()
    except KeyError:
        await interaction.response.send_message("You don't seem to be logged in", ephemeral=True)
    else:
        if len(classes) == 0:
            await interaction.response.send_message("No classes this week", ephemeral=True)
        else:
            view = CurrentClassesView(classes)
            await interaction.response.send_message(interaction.user.mention+"'s Classes", view=view, ephemeral=True)

@bot.user_command(name="See their classes")
async def gettheirclasses(interaction: nextcord.Interaction, member: nextcord.Member):
    try:
        classes = rethink.getEnrolledClasses(db["Users"][str(member.id)]["Auth"])
    except rethink.connectionFailed:
         await interaction.response.send_message("Server side error occured", ephemeral=True)
    except rethink.sessionAuthError:
        try:
            db["Users"][str(member.id)]["Auth"] = rethink.auth(db["Users"][str(member.id)]["Username"], db["Users"][str(member.id)]["Password"])
        except rethink.loginIncorrectErr:
            await interaction.response.send_message("Their password seemed to have changed, try re-registering", ephemeral=True)
        except rethink.connectionFailed:
            await interaction.response.send_message("Server side error occured", ephemeral=True)
        else:
            try:
                classes = rethink.getEnrolledClasses(db["Users"][str(member.id)]["Auth"])
            except:
                await interaction.response.send_message("Could not log that user in!", ephemeral=True)
                raise("Thats no good")
            else:
                saveState()
    except KeyError:
        await interaction.response.send_message("They don't seem to be logged in", ephemeral=True)
    else:
        if len(classes) == 0:
            await interaction.response.send_message("They have no classes this week", ephemeral=True)
        else:
            finout = "**```"+member.name+"'s Classes```**\n"
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
            await interaction.response.send_message(finout, ephemeral=True)

@bot.user_command(name="Clone their classes")
async def cloneclasses(interaction: nextcord.Interaction, member: nextcord.Member):
    try:
        classes = rethink.getEnrolledClasses(db["Users"][str(member.id)]["Auth"])
    except rethink.connectionFailed:
         await interaction.response.send_message("Server side error occured")
    except rethink.sessionAuthError:
        try:
            db["Users"][str(member.id)]["Auth"] = rethink.auth(db["Users"][str(member.id)]["Username"], db["Users"][str(member.id)]["Password"])
        except rethink.loginIncorrectErr:
            await interaction.response.send_message("Their password seemed to have changed, try re-registering")
        except rethink.connectionFailed:
            await interaction.response.send_message("Server side error occured")
        else:
            try:
                classes = rethink.getEnrolledClasses(db["Users"][str(member.id)]["Auth"])
            except:
                await interaction.response.send_message("Could not log that user in!", ephemeral=True)
            else:
                saveState()
    except KeyError:
        await interaction.response.send_message("They don't seem to be logged in")
    else:
        try:
            rethink.removeClass(db["Users"][str(interaction.user.id)]["Auth"], "0 OR 1=1")
        except rethink.connectionFailed:
             await interaction.response.send_message("Server side error occured")
        except rethink.sessionAuthError:
            try:
                db["Users"][str(interaction.user.id)]["Auth"] = rethink.auth(db["Users"][str(interaction.user.id)]["Username"], db["Users"][str(interaction.user.id)]["Password"])
            except rethink.loginIncorrectErr:
                await interaction.response.send_message("Their password seemed to have changed, try re-registering")
            except rethink.connectionFailed:
                await interaction.response.send_message("Server side error occured")
            else:
                try:
                    rethink.removeClass(db["Users"][str(interaction.user.id)]["Auth"], "0 OR 1=1")
                except:
                    await interaction.response.send_message("Could not log you in!", ephemeral=True)
                    raise("Thats no good")
                else:
                    saveState()
        except KeyError:
            await interaction.response.send_message("They don't seem to be logged in")
        else:
            for c in classes:
                curclass = c["classid"]
                try:
                    rethink.addClass(db["Users"][str(interaction.user.id)]["Auth"], curclass)
                except rethink.connectionFailed:
                     await interaction.response.send_message("Server side error occured")
                except rethink.sessionAuthError:
                    try:
                        db["Users"][str(interaction.user.id)]["Auth"] = rethink.auth(db["Users"][str(interaction.user.id)]["Username"], db["Users"][str(interaction.user.id)]["Password"])
                    except rethink.loginIncorrectErr:
                        await interaction.response.send_message("Their password seemed to have changed, try re-registering")
                    except rethink.connectionFailed:
                        await interaction.response.send_message("Server side error occured")
                    else:
                        try:
                            rethink.addClass(db["Users"][str(interaction.user.id)]["Auth"], curclass)
                        except:
                            await interaction.response.send_message("Could not log you in!", ephemeral=True)
                            raise("Thats no good")
                        else:
                            saveState()
                except KeyError:
                    await interaction.response.send_message("They don't seem to be logged in")
            await interaction.response.send_message("Cloned!")

bot.run(db["Options"]["BotToken"])
save_and_exit()