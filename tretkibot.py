#!/usr/local/lib/ python

import praw, datetime, time, random, string, obot

today = str(datetime.datetime.now().day) + "-" + str(datetime.datetime.now().month) + "-" + str(datetime.datetime.now().year)


def log(m, show=True):
    #logs = open("C:\Users\Alex\Documents\TretkiBot\TretkiBot\Tretki\logs\logs"+ today +".txt", "a")
    #logs.write(m + "\n")

    if show==True:
        print(m)

    #logs.close()

# Setting up initial parameters
immunity = ["inclinedtothelie"]
handPicked = [""]
memberCap = 95
bannedSubs = [" "]
bannedUsers = ["PlaylisterBot", "AutoModerator", "PornOverlord", "Kebble", "Andrew-Mccutchen", "Threven"]
karmaDownLimit = 100  #minimum comment karma
karmaUpLimit = 100000000  #maximum comment karma
accountAgeLimit = 30 #minimum account age in days
wordsLimit = [" "]  #words we don't want in a username
recap = ""
welcomeMessages = [
        'Welcome to Tretki! Please report to your nearest station for duty assignment.',
        'Welcome newcomers, you have been selected on a very strict set of criteria, which we promptly threw out and selected you.\n\n'
        '--u/Judge_kaos',
        'Tretki has not imploded yet\n\n'
        'Don\'t make me ban the mods again\n\n'
        'Wait, I\'m different from other bots!\n\n'
        'Don\'t listen to Vatvay\'s lies!\n\n'
        '--u/DeadEspeon',
        'Welcome to Tretki, where we\'ll love you like a monkey loves a chicken\n\n'
        '--u/ZombieBoobies',
        'What are you waiting for? Make a post, say hello then check out the [discord](https://discord.gg/yn9PQSr)'
        ]

log("Signing in as TretkiBot...")

try:
    r = obot.login()
except:
    print("Wrong username/password combination")
else:
    s = r.subreddit("tretki")
    log("Done")

# functions
def kick(user):
    s.contributor.remove(user)
    flair(user,"[Kicked]",'kicked')
    log("Kicked " + user)

def add(user):
    s.contributor.add(user)
    log("Added " + user)

def getUserList():
    userList = []
    for contributor in r.subreddit('tretki').contributor():
        username = str(contributor)
        if username != "TretkiBot":
            userList.append(username)
    userList.reverse()
    return userList

def flair(user,flair,css):
    s.flair.set(user, flair,css_class='css')
    log("/u/"+user+"'s flair changed to '"+flair+"' (CSS "+css+")")

def postRecap(m):
    log("Posting the recap...")
    postTitle = str(today) +' - Bot Recap'
    r.subreddit("tretki").submit(postTitle, m)
    log("Done")


#Kicking...
memberList = getUserList()
recap += "Kicked users: \n\n"

log("Starting to kick inactive members...")

i = 0
n = 0

for member in memberList:
        i+=1
        log("#" + str(i) + " /u/" + member)

        if member in immunity:
                log("/u/" + member + " is in immunity list.")
                continue

        if member in handPicked:
                log("/u/" + member + " is in hand picked list.")
                continue

        overview = r.redditor(member).new(limit=None)

        latestPost = 50000.0 #hours
        hoursLimit = 180.0 #hours

        for post in overview:
                postedSub = post.subreddit.display_name
                hoursAgo = (time.time()-post.created_utc)/3600.0

                if postedSub == "tretki":
                        if hoursAgo < latestPost:
                                latestPost = hoursAgo

                if hoursAgo>hoursLimit:
                        break

        if latestPost <= hoursLimit:
                log("[OK] Latest post was " + str(latestPost) + " hours ago.")
        else:
                log("[NOT OK] No post in /r/tretki in the last 7 days.")
                recap += "\#" + str(i) + " - /u/" + member + "\n\n"
                n+=1
                kick(member)

#Adding...

nbAdded = memberCap-len(memberList)+n
newUser = ""
log("Adding " + str(nbAdded) + " users...")
newUser = ""
recap += "\nAdded users:  \n\n"
sourceList = []

if nbAdded<0:
        nbAdded=0

while nbAdded>0:
        for c in r.subreddit("all").comments():
                username = str(c.author)
                linkId = c.link_id.replace("t3_","")+"/"+c.id
                karma = c.author.comment_karma
                postedSub = c.subreddit.display_name
                accountAge = (time.time()-c.author.created_utc)/86400.0

                log("Considering /u/" + username + " from post " + linkId + ".")

                if username in bannedUsers:
                        log("[NOT OK] Banned user.")
                        continue

                if postedSub in bannedSubs:
                        log("[NOT OK] Posted in a banned subreddit")
                        continue

                if karma < karmaDownLimit:
                        log("[NOT OK] Comment karma too low.")
                        continue

                if karma > karmaUpLimit:
                        log("[NOT OK] Comment karma too high.")
                        continue

                if accountAge < accountAgeLimit:
                        log("[NOT OK] Account too recent.")
                        continue

                if any(word in username for word in wordsLimit):
                        log("[NOT OK] Username contains banned word.")
                        continue

                if random.randint(0,1) == 1:
                        log("[NOT OK] Not lucky enough.")
                        continue

                sourceList.append({'user':username,'sourcePost':c.link_id.replace("t3_",""),'sourceComment':c.id})

                nbAdded-=1

                print(nbAdded)
                add(username)

                if newUser == "":
                        newUser = username

                if nbAdded==0:
                        break

#Change flairs...
new=""
i=0
newUsers = []
for user in getUserList():
        i+=1
        if user==newUser:
                new="new"

        flair(user,'#'+str(i),'number'+new)

        if new=="new":
                newUsers.append(user)
                for x in sourceList:
                        if user == x['user']:
                                sourcePost_ = x['sourcePost']
                                sourceComment_ = x['sourceComment']
                                break
                recap += "\#" + str(i) + " - /u/" + user + ' from [this comment](https://reddit.com/comments/' + sourcePost_ + '/comment/' + sourceComment_ + ')\n\n'

if random.randint(0,1) == 1:
        recap += '-----\n\n' + welcomeMessages[random.randint(0,len(welcomeMessages)-1)]
else:
        pickedUser = newUsers[random.randint(0,len(newUsers)-1)]
        userWelcomeMessages = [
                'Are you drunk, u/' + pickedUser + '? This isn\'t Arby\'s!\n\n'
                '--u/Ghostronic',
                'Welcome to tretki, u/' + pickedUser + '. It\'s a lot like Las Vegas: what happens here, stays here.\n\n'
                '--u/Ghostronic',
                'Oh u/' + pickedUser + ', I don\'t think we\'re in Kansas anymore.\n\n'
                '--u/Ghostronic',
                'Well gee, where are you, u/' + pickedUser + '? Guess you should have made a left at Albuquerque.\n\n'
                '--u/Ghostronic',
                'All non-residents must follow the blue signs for customs.\n\n'
                '--u/Alas-I-Cannot-Swim',
                'Please step aside, u/' + pickedUser + ', you\'ve been selected for random screening.\n\n'
                '--u/Alas-I-Cannot-Swim',
                'u/' + pickedUser + ', please present your passport at check-in.\n\n'
                '--u/Alas-I-Cannot-Swim',
                'Congratulations, u/' + pickedUser + ', you\'ve been nominated for the newbie of the week award. Then again, so was everyone else.\n\n'
                '--u/Alas-I-Cannot-Swim',
                'According to our census data u/' + pickedUser + 'ingested the most muenster out of all the residents in their town last quarter.\n\n'
                '--u/Alas-I-Cannot-Swim',
                'Hey u/' + pickedUser + ', don\'t make it bad.~ Take a sad soooong, and make it better.~\n\n'
                '--u/Alas-I-Cannot-Swim',
                'Jack and u/' + pickedUser + ' went up the hill to fetch a pail of water.\n\n'
                '--u/Alas-I-Cannot-Swim',
                'Welcome to the party, u/' + pickedUser + '. Party hats on the table to the left.\n\n'
                '--u/Alas-I-Cannot-Swim',
                'You have been initiated, u/' + pickedUser + '. To celebrate your commencement, please consume this cookie: [unicode cookie].\n\n'
                '--u/Alas-I-Cannot-Swim',
                'Warning: Your password must not contain the phrase \'' + pickedUser + '.\'\n\n'
                '--u/Alas-I-Cannot-Swim',
                'Well, here we are, u/' + pickedUser + '. I hope you remembered your pants this time.\n\n'
                '--u/Alas-I-Cannot-Swim',
                'Attention Tretkittens. This is an urgent message from your moderators. u/' + pickedUser + ' has usurped the throne. Seek refuge in a neighboring sovereignty until further notice.\n\n'
                '--u/Alas-I-Cannot-Swim',
                'Attention Tretkittens. This is a message from your moderators. All Tretki tax money is now being diverted into u/' + pickedUser + '\'s cookie fund.\n\n'
                '--u/Alas-I-Cannot-Swim',
                'Attention Tretkittens. The recent outbreak of Vatvitis can be cured by the presence of a rare genetic mutation in u/' + pickedUser + '\'s blood. Please consult them for a DNA sample.\n\n'
                '--u/Alas-I-Cannot-Swim',
                'Attention Tretkittens. This is a message from your moderators. Due to a bureaucratic discrepancy, u/' + pickedUser + ' has been elected our new Minister of Propaganda.\n\n'
                '--u/Alas-I-Cannot-Swim',
                'Attention Tretkittens. Due to a clerical error, u/' + pickedUser + ' has been elected our new Secretary of Defense, and will head the pitchfork budget for the time being.\n\n'
                '--u/Alas-I-Cannot-Swim',
                'Hey, u/' + pickedUser + ', you\'re that person! From that place! Remember when you did that one thing that one time? That was too cool!\n\n'
                '--u/Alas-I-Cannot-Swim',
                'We were supposed to have one of those custom celebratory balloons for you, u/' + pickedUser + ', but /u/Ghostronic\'s dog popped it with his teeth. Sorry.\n\n'
                '--u/Alas-I-Cannot-Swim',
                'Warning, u/' + pickedUser + ', proceed with caution. You are now entering a radioactive zone.\n\n'
                '--u/Alas-I-Cannot-Swim',
                'Something wicked this way comes.\n\n'
                '--u/Alas-I-Cannot-Swim',
                'Greetings, u/' + pickedUser + '. You are among those chosen by the Great Vatvay on this glorious day. Please submit your tithe by the end of the week.\n\n'
                '--u/Alas-I-Cannot-Swim',
                'Attention all Tretkittens. u/' + pickedUser + ' is in great danger, and they need your help. All they need is your credit card number, the three digits on the back, and the expiration month and year.\n\n'
                '--u/Alas-I-Cannot-Swim',
                'u/' + pickedUser + ' aims to misbehave.\n\n'
                '--u/Alas-I-Cannot-Swim',
                'Long ago, the four nations lived together in harmony. Then, everything changed when u/' + pickedUser + ' attacked.\n\n'
                '--u/Alas-I-Cannot-Swim',
                'We had a cookie for you, u/' + pickedUser + ', but /u/Alas-I-Cannot-Swim totally stole it. What a jerk.\n\n'
                '--u/Alas-I-Cannot-Swim',
                'You were supposed to get some witty welcome message, u/' + pickedUser + ', but we ran out of ideas. Sorry to break the fourth wall, but you get the short stick.\n\n'
                '--u/Alas-I-Cannot-Swim',
                'It\'s a brave wide wacky world we live in, u/' + pickedUser + '. Out of all the millions of redditors, it was you who ended up here. Pretty neat, huh?\n\n'
                '--u/Alas-I-Cannot-Swim',
                'I hope you\'re not on a week-long vacation right now, u/' + pickedUser + '. Otherwise you\'ll miss your chance and get booted from this place forever before you even know it exists. So it goes.\n\n'
                '--u/Alas-I-Cannot-Swim',
                'Oh no. Not this guy again.\n\n'
                '--u/Alas-I-Cannot-Swim',
                'Hey, you sass that hoopy u/' + pickedUser + '? There\'s a frood who really knows where their towel is.\n\n'
                '--u/Alas-I-Cannot-Swim'
        ]
        recap += '-----\n\n' + userWelcomeMessages[random.randint(0,len(userWelcomeMessages)-1)]

#Posting the recap...
postRecap(recap)
## lastRecap = r.get_redditor("TretkiBot").get_submitted(limit=None)

## for recap in lastRecap:
##    recapLink = "["+today+"](" + recap.permalink + ")"
##   break

## fContent = ""
## f = open("/usr/bin/tretki/tretki/Bots/RecapLinks.txt", "r")
## content = f.read()
## f.close()

## f = open("/usr/bin/tretki/tretki/Bots/RecapLinks.txt", "w")
## f.write(recapLink + '\n\n' + content)
## f.close()

## f = open("/usr/bin/tretki/tretki/Bots/RecapLinks.txt", "r")
## fContent = f.read()
## f.close()

## wiki = r.get_wiki_page("tretki","botrecaps")
## editPage = r.edit_wiki_page("tretki", "botrecaps","#Bot Recap log\n\nThis page includes all of /u/TretkiBot's recaps of kicked and added users. It does not include /u/Vatvay's recaps at the time being.\n\n" + fContent, reason=u'')
