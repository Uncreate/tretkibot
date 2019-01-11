#!/usr/local/lib/ python

import praw, datetime, time, random, string, obot

#today = str(datetime.datetime.now().day) + "-" + str(datetime.datetime.now().month) + "-" + str(datetime.datetime.now().year)
now = datetime.datetime.now().astimezone(datetime.timezone(datetime.timedelta(days=-1, seconds=64800), 'Central Standard Time'))
today = str(now.day) + "-" + str(now.month) + "-" + str(now.year)

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
from messages import *

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
                recap += r"\#" + str(i) + " - /u/" + member + "\n\n"
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

                sourceList.append({'user':username,'sourcePost':c.link_id.replace("t3_",""),'sourceComment':c.id,'sourceSubreddit':postedSub})

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
                                sourceSubreddit_ = x['sourceSubreddit']
                                break
                recap += r"\#" + str(i) + " - /u/" + user + ' from [this comment](https://reddit.com/comments/' + sourcePost_ + '/comment/' + sourceComment_ + '?context=10000) in [r/' + sourceSubreddit_ + '](https://reddit.com/r/' + sourceSubreddit_ + ')\n\n'

if random.randint(0,1) == 1:
        recap += '-----\n\n' + welcomeMessages[random.randint(0,len(welcomeMessages)-1)]
else:
        pickedUser = newUsers[random.randint(0,len(newUsers)-1)]
        recap += '-----\n\n' + userWelcomeMessages[random.randint(0,len(userWelcomeMessages)-1)].format(pickedUser)

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
