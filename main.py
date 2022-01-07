import os, sys, time, random, requests

import funcs, discum_white
import configs as cfg

bot = discum_white.Client(
    token=cfg.token, prefix=cfg.prefix, log=False)

gifs = funcs.loadGifs()
data = {'userid': {}, 'keyword': {}}

@bot.command()
def loadReactions():
    global data
    print(">Loading Reacts...")
    if not (os.path.isfile("reactspam.json")):
        print(">Reacts list does not exist. Creating...")
        funcs.writeJson("reactspam.json", data)
    else:
        data = funcs.loadJson("reactspam.json")

@bot.command(aliases=['s'])
def spam(ctx):
    content = ctx.content.split(" ")

    if(content[1].isnumeric()):
        amount = int(content[1])
    else:
        amount = 5

    if not (content[0] in gifs):
        content = content[0]
    else:
        content = gifs[content[0]]

    for i in range(amount):
        ctx.sendMessage(content)

@bot.command()
def slowPrint(ctx):
    currentMessage = ""
    for i in ctx.content:
        currentMessage += i
        ctx.editMessage(currentMessage)


def ascii(ctx):
    content = ctx.content.replace(" ", "+")
    request = requests.get(
        "https://artii.herokuapp.com/make?text=" + content.upper())
    ctx.editMessage(f"```{request.text}```")

@bot.command()
def binary(ctx):
    content = ctx.content.split(" ")
    content.pop(0)
    res = ""
    for word in content:
        for char in word:
            res += str(format(ord(char), '08b'))
            res += " "
        res += "\n"
    ctx.editMessage(res)

@bot.command()
def tochar(ctx):
    content = ctx.content.split(" ")
    content.pop(0)
    res = ""
    for word in content:
        res += chr(int(word, 2))
    ctx.editMessage(res)
    
@bot.command()
def addreactspam(ctx):
    global data
    content = ctx.content.split(" ")
    content.pop(0) # remove mention
    
    if not (len(ctx.mentions) > 0):
        return
    userId = ctx.mentions[0]['id']

    newKey = {userId: content}
    if not(os.path.exists("reactspam.json")):
        funcs.writeJson("reactspam.json", newKey)
    else:
        data = funcs.loadJson("reactspam.json")
        if not (userId in data['userid']):
            data['userid'][userId] = content
        else:
            data['userid'][userId] += content
        funcs.writeJson("reactspam.json", data)

@bot.command()
def removereactspam(ctx):
    global data
    if not (len(ctx.mentions) > 0):
        return
    userId = ctx.mentions[0]['id']

    data = funcs.loadJson("reactspam.json")
    if(userId in data):
        del data['userid'][userId]
    funcs.writeJson("reactspam.json", data)

@bot.command()
def clearreactspam():
    global data
    data = {'userid': {}, 'keyword': {}}
    funcs.writeJson("reactspam.json", data)

@bot.command()
def addkeyspam(ctx):
    global data
    content = ctx.content.split(" ")
    keyWord = content[0]
    theEmoji = content[1]

    newKey = {keyWord: theEmoji}
    if not(os.path.exists("reactspam.json")):
        funcs.writeJson("reactspam.json", newKey)
    else:
        data = funcs.loadJson("reactspam.json")
        if not (keyWord in data):
            data['keyword'][keyWord] = [theEmoji]
        else:
            data['keyword'][keyWord].append(theEmoji)
        funcs.writeJson("reactspam.json", data)

@bot.command()
def removekeyspam(ctx):
    msg = ctx.content.split(" ")
    global data
    keyWord = msg[1]
    data = funcs.loadJson("reactspam.json")
    if(keyWord in data['keyword']):
        del data['keyword'][keyWord]
    funcs.writeJson("reactspam.json", data)

@bot.command()
def addSpam(ctx):
    global gifs
    content = ctx.content.split(" ")
    keyWord = content[0]
    gif = content[1]
    newKey = {keyWord: gif}
    if not(os.path.exists("giflist.json")):
        funcs.writeJson("giflist.json", newKey)
    else:
        gifFileContentJson = funcs.loadJson("giflist.json")
        gifFileContentJson[keyWord] = gif
        funcs.writeJson("giflist.json", gifFileContentJson)

    gifs = funcs.loadJson("giflist.json")

@bot.command()
def remSpam(ctx):
    global gifs
    content = ctx.content.split(" ")
    keyWord = content[0]
    gifFileContentJson = funcs.loadJson("giflist.json")

    if(keyWord in gifFileContentJson):
        del gifFileContentJson[keyWord]
    funcs.writeJson("giflist.json", gifFileContentJson)

    gifs = funcs.loadJson("giflist.json")

@bot.on_message()
def logger(ctx):
    if not (hasattr(ctx, 'guild_id')):
        guildName = "Direct-messages"
        channelName = f"{ctx.author.username}-{ctx.author.id}"
        guildPath = f"logger\\{guildName}"
        channelPath = guildPath + f"\\{channelName}.{cfg.logFormat}"

    else:
        guildName = bot.gateway.session.guild(ctx.guild_id).name
        channelName = bot.gateway.session.guild(ctx.guild_id).channel(ctx.channel_id)['name']
        guildPath = f"logger\\{guildName}_{ctx.guild_id}"
        channelPath = guildPath + \
            f"\\{channelName}-{ctx.channel_id}.{cfg.logFormat}"

    if not(os.path.exists("logger")):
        os.makedirs("logger")

    if not(os.path.exists(guildPath)):
        os.makedirs(guildPath)

    if not(os.path.exists(channelPath)):
        with open(channelPath, "w") as f:
            f.write("==== BEGINNING ====\n")

    with open(channelPath, "a", encoding="utf-8") as f:
        timestamp = ctx.timestamp.replace("T", " ")
        timestamp = timestamp.split(".")
        timestamp = timestamp[0]

        if(hasattr(ctx, "message_reference")):  # checking if the message was a reply
            f.write(f"REPLY TO: {ctx.message_reference.message_id}\n")
        f.write(
            f"{ctx.author.username}#{ctx.author.discriminator} AT {timestamp} --- Message ID {ctx.id}\n{ctx.content}\n\n")

@bot.on_message()
def handleReactSpam(ctx):
    if(ctx.author.id in data['userid']):
        for emoji in data['userid'][ctx.author.id]:
            ctx.addReaction(emoji)

    for word in ctx.content.split(" "):
        if(word in data['keyword']):
            for emoji in data['keyword'][word]:
                ctx.addReaction(emoji)
            break

@bot.command()
def antivirus(ctx):
    ctx.editMessage("https://cdn.discordapp.com/attachments/862772809242509322/928032486880063499/796078795185717268-1.png")
    time.sleep(0.24) #shortest amount of time possible for us to edit the message
    ctx.deleteMessage(priority=True)












































while(True):
    print(">Connecting...")
    try:
        time.sleep(random.uniform(0.5, 2))
        bot.gateway.run(auto_reconnect=True)
    except KeyboardInterrupt:
        print(">Goodbye.")
        sys.exit(0)
