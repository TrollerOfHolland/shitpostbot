import os, time, json

def loadEmotes():
    global emoteDictionary
    f = open('emojis.json', 'r')
    emoteDictionary = json.load(f)
    f.close()

def loadGifs():
    print(">Loading Gifs...")
    if not (os.path.isfile("giflist.json")):
        print(">Gif list does not exist. Creating...")
        with open("giflist.json", "w") as gifFile:
            gifs = {
                "nigger": "https://media.discordapp.net/attachments/911923982821904427/924651985024720956/image0-16-1.gif"}
            json.dump(gifs, gifFile)
    else:
        with open("giflist.json", "r") as gifFile:
            gifs = json.loads(gifFile.read())
    return gifs

def getEmojis(bot, ctx):
    emojiList = {}
    for guild in bot.gateway.session.guilds:
        emojis = bot.gateway.session.guild(guild).emojis
        for emojiId in emojis.keys():
            if f":{emojis[emojiId]['name']}:" in emojiList:
                emojiList[f":{emojis[emojiId]['name']}:"][1].append(guild)
                continue

            emojiList[f":{emojis[emojiId]['name']}:"] = [
                f"https://cdn.discordapp.com/emojis/{emojiId}.png?size=64", [guild]]

    if(os.path.exists('emojis.json')):
        os.remove('emojis.json')

    f = open('emojis.json', 'w')
    json.dump(emojiList, f)
    f.close()
    loadEmotes()

def loadJson(filename, enctype='utf-16'):
    playlist_file = open(filename, encoding=enctype)
    playlists = json.load(playlist_file)
    playlist_file.close()
    return playlists

def writeJson(file, data, enctype='utf-16'):
    playlist_file = open(file, 'w', encoding=enctype)
    json.dump(data, playlist_file, indent=4, ensure_ascii=False)
    playlist_file.close()
