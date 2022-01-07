import threading, time, discum, json

def preventRatelimit(discreply):
    if "retry_after" in discreply.text:
        jdata = json.loads(discreply.text)
        print(f">{jdata['retry_after']} TIMEOUT")
        # wait as long as discord said
        time.sleep(jdata['retry_after'])

class SendMessageTask:
    def execute(self, bot):
        discreply = bot.sendMessage(self.channel, self.content)
        preventRatelimit(discreply)
        time.sleep(0.4)

    def __init__(self, channel, content):
        self.channel = channel
        self.content = content

class EditMessageTask:
    def execute(self, bot):  
        discreply = bot.editMessage(self.channel, self.messageId, self.content)
        preventRatelimit(discreply)

    def __init__(self, channel, messageId, content):
        self.channel = channel
        self.messageId = messageId
        self.content = content

class AddReactionTask(EditMessageTask):
    def execute(self, bot):  
        discreply = bot.addReaction(self.channel, self.messageId, self.content)
        preventRatelimit(discreply)

class DeleteMessageTask:
    def execute(self, bot):
        discreply = bot.deleteMessage(self.channel, self.messageId)
        preventRatelimit(discreply)

    def __init__(self, channel, messageId):
        self.channel = channel
        self.messageId = messageId

class ctxSubclass:
    def __init__(self, ctxDict):
        for key in ctxDict:
            setattr(self, key, ctxDict[key])

class context:
    
    def __init__(self, ctxDict, bot):
        for key in ctxDict:
            if(key == "author" or key == "message_reference"):
                setattr(self, key, ctxSubclass(ctxDict[key]))
                continue

            setattr(self, key, ctxDict[key])

        self.bot = bot

    def sendMessage(self, content, priority = False):
        self.bot.addTask(SendMessageTask(self.channel_id, content), priority)

    def editMessage(self, content, priority = False):
        self.bot.addTask(EditMessageTask(self.channel_id, self.id, content), priority)
    
    def addReaction(self, content, priority = False):
        self.bot.addTask(AddReactionTask(self.channel_id, self.id, content), priority)

    def deleteMessage(self, priority = False):
        self.bot.addTask(DeleteMessageTask(self.channel_id, self.id), priority)


class Client(discum.Client):

    commands = {}
    onMessageFunctions = []
    prefix = "!"
    userId = ""
    tasks = []

    #task handling
    def taskHandler(self):
        while True:
            if(len(self.tasks) > 0):
                task = self.tasks.pop(0)
                task.execute(self)
            time.sleep(0.4)
                
    def addTask(self, task, priority):
            if(priority):
                self.tasks.insert(0, task)
                return

            self.tasks.append(task)

    def parseCommand(self, ctx):

        ctx.content = ctx.content.removeprefix(self.prefix)
        desiredCommand = ctx.content.split(" ")[0]
        ctx.content = ctx.content.removeprefix(desiredCommand + " ")
        
        for command in self.commands:
            if(desiredCommand in self.commands[command]):
                command(ctx)


    def messageHook(self, resp):

        if resp.event.ready_supplemental:  # ready_supplemental is sent after ready
            user = self.gateway.session.user
            print("Logged in as {}#{}".format(
                user['username'], user['discriminator']))
            self.userId = user['id']
            return

        if not resp.event.message:
            return       
        
        ctx = context(resp.parsed.auto(), self)

        for func in self.onMessageFunctions:
            func(ctx)

        if (ctx.author.id == self.userId and ctx.content.startswith(self.prefix)):
            self.parseCommand(ctx)

    def command(self, aliases = []):

        def decorator(func):

            for command in self.commands:
                if(func.__name__ in self.commands[command]):
                    raise Exception("Command already exists: " + func.__name__ )#I'm throwing exceptions, real stuff right here

            self.commands[func] = [func.__name__] + aliases
            return True
        
        return decorator
            
    def on_message(self, aliases = []): #simply pasted from def command

        def decorator(func):

            if(func in self.onMessageFunctions):
                raise Exception("function already exists: " + func.__name__)

            self.onMessageFunctions.append(func)
            return True

        return decorator
        
    def __init__(self, token, log=False, prefix = "!"):
        super(Client, self).__init__(token=token, log=log)

        self.prefix = prefix
        self.gateway._after_message_hooks.append(self.messageHook)

        threading.Thread(target = self.taskHandler).start() #starting the task handler