#-*- coding: utf-8 -*-
class HtmlTag: #each little <> statement will be a tag. tags have a name
# (first thing in them), a bunch of value pairs (all the stuff that says
# (____ = _____,) and maybe some data (stuff that comes after the <>).
    def __init__(self,sendToTag): #a string gets passed to the tag called "sendToTag." Creative, right?
        self.name = '' #start empty
        self.valuePairs = [] #empty
        self.data = ''
        self.subTags = []
        self.magnitude = 1
        # self.raw = sendToTag #This is mostly for debugging
        self.isClosing = False
        self.isClosed = False
        self.isComment = False
        self.isUnclosed = False
        if len(sendToTag) > 1: #if there is a second character and it is a...
            if sendToTag[1] == '/': # ...'/', then this tag is a closing tag.
                self.isClosing = True
                self.isClosed = True
            if sendToTag[1] == '!': #...'!', then this tag is a comment
                self.isComment = True
                self.isClosed = True
                self.data = sendToTag
                self.name = "comment"
                return
            if sendToTag[-2] == '/': #if the last character is a '/', tag is self-closing
                self.isClosed = True
        letterGen = iter(sendToTag) #create an iterator from the sendToTag string
        while True: #look for the name. it's the first thing before a space
            try:
                letter = letterGen.next()
            except StopIteration:
                break
            if letter in ['<','>',"\n","\r","\t"]: #skip these characters
                continue 
            if letter == ' ': #stop if we get to a space
                break
            self.name += letter #keep adding chars to the name
        sendToPair = ''
        quoteOpen = False
        while True: #look for value pairs
            try:
                letter = letterGen.next()
            except StopIteration:
                if sendToPair:
                    sendToPair = sendToPair.rstrip('/')
                    self.valuePairs.append(ValuePair(sendToPair))
                break
            if letter in ['<','>',"\n","\r","\t"]: #skip these characters
                continue
            if letter in ['"',"'"]: #keep track of if there's an open quote mark
                if not quoteOpen:
                    quoteOpen = True
                else:
                    quoteOpen = False
            if letter != " ": #add all the characters before you reach a space
            # which is outside a quote to the value pair
                sendToPair += letter
            if letter == " " and quoteOpen:
                sendToPair += letter
            elif letter == " " and not quoteOpen: #when you find a space, send them and reset the sendToPair string for the next pair
                if sendToPair: #this line makes sure we don't send empty strings as value pairs, in case of
                # something like multiple " " characters in a row
                    self.valuePairs.append(ValuePair(sendToPair))
                    sendToPair = ''
        return
    def __repr__(self): #override this for printing
        if self.data:
            dataTag = 'D'
        else:
            dataTag = ''
        return "{0}({1})[{2}-{3}]{4}".format(self.name,len(self.valuePairs),len(self.subTags),self.magnitude,dataTag)
    def addData(self,sendToTag):
        self.data = sendToTag
        return
    def addSubTag(self,tag):
        self.subTags.append(tag)
        self.magnitude += tag.getMagnitude()
        return
    def makeClosed(self):
        self.isClosed = True
        return
    def makeUnclosed(self):
        self.isUnclosed = True
        return
    def getIsOpen(self):
        if self.isClosed:
            return False
        else:
            return True
    def getIsClosing(self):
        if self.isClosing:
            return True
        else:
            return False
    def getIsComment(self):
        if self.isComment:
            return True
        else:
            return False
    def getName(self):
        return self.name
    def getMagnitude(self):
        return self.magnitude
    def getPairNames(self):
        return [pair.getName() for pair in self.valuePairs]
    def getPairValues(self):
        return [pair.getValue() for pair in self.valuePairs]
    def getSubTags(self):
        return self.subTags
    def findValuePairByName(self,name):
        for valuePair in self.valuePairs:
            pairName = valuePair.getName()
            if pairName == name:
                return valuePair
        return False
class ValuePair: #every html tag has value pairs, which are of the form ____="________". This
# breaks those down into an object with a name (the first part) and the value (the second part)
    def __init__(self,sendToPair):
        split = sendToPair.split('=',1) #splits a string based on a character, in this case, '=', and returns a list of the split up parts. Html tags have these pairs all the time, like 'name=Alabama','font=Bold', etc.
        self.name = split[0]
        if len(split) > 1: #sometimes the strings don't have an =, in which case the "split" list is just one item long, so split[1] would raise an Exception
            self.value = split[1]
        return
    def __repr__(self): #overriding this method controls how the object is printed by the console
        return '{0} = {1}'.format(self.name,self.value)
    def getName(self):
        return self.name
    def getValue(self):
        return self.value
class Page:
    def __init__(self,urlLibReadPage): #urlLibReadPage is an html file
        self.tags = [] #each page consists of a bunch of html tags
        lineGen = iter(urlLibReadPage) #create an iterable called lineGen that lets you go through the file line by line
        sendToTag = '' #create an empty string to serve as a character buffer. Important characters will go to this buffer one by one; it will be saved/cleared once they form a coherent set (like an html "word")
        while True: #while [condition] loops go on so long as a certain condition is met. If you simply make the condition "True," like I did, they will go on indefinitely. Inside the while loop are "break" commands which break out of the loop when certain criterion are met. I use this construction where I create an iterable and use a while True loop to iterate through it because it lets me mimic a for loop, but gives me more control on skipping items in the loop when certain criterion are met.
            try:
                line = lineGen.next() #take the next line of the file (if there is one)
                letterGen = iter(line) #create an iterable called letterGen that lets you go through the line letter by letter
            except StopIteration: #if there isn't a next line of the file...
                break #...then stop iterating and move on outside the while loop.
            while True: #same "while True" construction again, this time going letter by letter instead of line by line
                try:
                    letter = letterGen.next() #take the next letter (if there is one)
                except StopIteration: #if there isn't a next letter...
                    break #break out of this while loop and move onto the next line
                if letter in ["\n","\r","\t"]: #if the letter is a tab or new line character
                    continue #then ignore it
                if letter == " ": #if the letter is a space
                    if not sendToTag: #and we haven't recorded any important letters in the buffer
                        continue #then skip the letter
                    if sendToTag[-1] == " ": #also, if the most recent character was a space (indicated there were multiple spaces in a row)
                        continue #then skip the letter
                if letter == '<' and self.tags: #if the letter is a '<', and there are already closed tags, then that indicates the opening of a new html tag. If we have any important letters already in the buffer, then they belong as data to the most recently closed tag. This is because every time a closing '>' is reached, the buffer is flushed. So, if the buffer is NOT empty, it means there were characters occurring AFTEr a closing '>' but BEFORE an opening '<'. 
                    if sendToTag: #If there are letters in the buffer...
                        # print sendToTag
                        self.tags[-1].addData(sendToTag) #...then send them as data to the most recently created tag.
                    sendToTag = ''
                if letter == '>': #if you hit a closing '>'...
                    sendToTag += '>' #add a '>' character to the end of the buffer
                    self.tags.append(HtmlTag(sendToTag)) #create a new HtmlTag object with the letters in the buffer, and add that HtmlTag object to the list of tags in this page object
                    sendToTag = '' #clear the buffer
                    continue
                sendToTag += letter #if you reach this line, it means the letter was not skipped nor was it an opening/closing '<'/'>', so add it to the buffer.
        self.tags2 = [tag for tag in self.tags] #once you've iterated through all the lines, make a copy of the tags called tags2. I don't remember why I made it have this. Weird.
        self.closeTags() #this runs the closeTags function
        return
    def closeTags(self): #this function will sort the input tags into their heirarchy and pair opening tags with their appropriate closing tags. html tags usually occur in nested pairs; the indentation makes it easy to read by eye but not so much in a computer. A tag for sarcasm might look like this "<sarcasm>if only there was some way people knew a written sentence was sarcastic</sarcasm>". This function pairs up <>'s with the appropriate </>'s.
        #Look for the first closing tag
        parsedTags = []
        tags = self.tags
        i = 0
        subjugated = [False for tag in tags] #create a list of the "subjugation" statuses of each tag; subjugation refers to if the tags have been appropriately grouped into their parent-child relationships (made subject of another tag). Each tag can have a bunch of subtags, which in turn can also have subtags. This organization makes sense if you open an html file because it reflects (mostly) the indentation of the lines.
        while i < len(tags): #this is another tricky way to iterate through a list in a nonstandard fashion. i is the index of the element in the list we're accessing. it starts at 0, so that's the first tag in the list.
            tag = tags[i] #take a tag, starting with the first and ending with the last
            if tag.getIsClosing(): #if the tag is a closing tag (</> kind)...
                closingTag = tag #then search for it's corresponding opening tag by iterating BACKWARDS through the list of tags, starting at the most recent tag.
                j = i-1
                while j >= 0:
                    if subjugated[j]: #skip tags which have already been subjugated to another tag
                        j -= 1
                        continue
                    tag = tags[j] 
                    if tag.getIsOpen() and '/'+tag.getName() == closingTag.getName(): #if the tag is open and the tag name matches (i.e., <sarcasm> and </sarcasm>)
                        tag.makeClosed() #close the tag
                        subjugated[i] = True #indicate that the closing tag is now a subject of its corresponding opening tag
                        for k in range(j+1,i):
                            if not subjugated[k]: #indicate that all the un-subjugated tags between the opening and closing tag are now subtags of the opening tag.
                                tag.addSubTag(tags[k])
                                subjugated[k] = True #record the chanegs in subjugation status
                        break
                    j -= 1 #j iterates backwards (gets smaller each loop)
            i += 1 #i iterates forwards (gets bigger each loop)
        for i,tag in enumerate(tags):
            if not subjugated[i]:
                parsedTags.append(tag) #the remaining tags which haven't become subjects of another tag are now the "tags" of the page. Their subjects are stored in the tags "subtag" objects.
        self.tags = parsedTags
        return

def findTags(tags,name,pairName='',pairValue=''): #this function will return all tags with the
#specified name and, if included, pair name, and pair value
    tagsToReturn = []
    for tag in tags: #iterate through all the tags given
        addTheTag = False
        if tag.getName() == name: #if the name of the tag matches the given name...
            if pairName: #...and a pair name was specified
                pairNames = tag.getPairNames() #...then get the list of pair names in the tag
                if pairName in pairNames: #if the pair name specified is in the tag's list of pair names...
                    if pairValue: #...and if a pair value was specified...
                        pairValues = tag.getPairValues() #...then get the list of pair values in the tag
                        if pairValue in pairValues: #if the pair value we want is in the list of pair values...
                            if pairNames.index(pairName)==pairValues.index(pairValue): #...then check if the index of the pair name specified matches the index of the pair value specified, indicating that that pair name has that pair value. If it does, then add the tag. Otherwise, don't.
                                addTheTag = True
                    else: #otherwise, if a pair value was not specified, just add the tag
                        addTheTag = True
            else: #otherwise, if a pair name was not specified, just add the tag
                addTheTag = True
        if addTheTag:
            tagsToReturn.append(tag) #if we're gonna add the tag, put it in the list of tags to add.
        if tag.getSubTags(): #if the tag we're gonna add has any subtags, conduct a search on those subtags using this same function! Recursion is awesome!
            tagsToReturn.extend(findTags(tag.getSubTags(),name,pairName,pairValue))
    return tagsToReturn

def findTagsAll(tags,name,pairName='',pairValue='',startsWith=False): #this function returns all tags and subtags alike which match the criterion, without respect for tag/subtag hierarchy
    tagsToReturn = []
    tagsToReturn.extend(findTags(tags,name,pairName,pairValue,startsWith))
    for tag in tags:
        if tag.subTags:
            tagsToReturn.extend(findTagsAll(tag.subTags,name,pairName,pairValue,startsWith))
    return tagsToReturn

def superFindTags(tags,superTagName,name,superPairName='',superPairValue='',pairName='',pairValue=''):
    #this function is very similar to the one above, so it won't be annotated much. The idea here is that, instead of just searching for tags with specific names that may have a specific name/value pair in them, you can search for tags that are subtags of specified tags, and these "super" tags must be specified by name but can also be further specified by name/value pairs in them.
    tagsToReturn = [] #will return a list of tuples (X,Y) where X is the matching tag
    #and Y is the list of matching subtags
    for tag in tags:
        considerTheTag = False
        if tag.getName() == superTagName:
            if superPairName:
                superPairNames = tag.getPairNames()
                if superPairName in superPairNames:
                    if superPairValue:
                        superPairValues = tag.getPairValues()
                        if superPairValue in superPairValues:
                            if superPairNames.index(superPairName)==superPairValues.index(superPairValue):
                                considerTheTag = True
                    else:
                        considerTheTag = True
            else:
                considerTheTag = True
        if considerTheTag:
            subTags = tag.getSubTags()
            if subTags:
                foundTags=findTags(subTags,name,superPairName,superPairValue,pairName,pairValue)                
            if foundTags:
                tagsToReturn.append((tag,tagsToReturn))
        else:
            subTags = tag.getSubTags()
            if subTags:
                tagsToReturn.extend(superfindTags(subTags,superTagName,name,pairName,pairValue))
    return tagsToReturn

#this file contains three classes and two methods that I use to build a scraping script for a specific application.
#First I create the a page object from an html file, then I look through the html file and figure out where the information I want is.
#It may be the value in a name/value pair, but often it's tag "data", or the stuff that occurs between <>'s.
#In either case, I use the searching methods findTags and superFindTags to find all the tags which have the data I want, then copy it to text or csv files.
                    
                        
