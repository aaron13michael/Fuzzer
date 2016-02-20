import bs4
import requests
import sys

"""
Release 1 -- Discover
Jeremy Friedman
Aaron Stadler
"""

"""
Partial validation. 
@args userArgs -- user input
@return: number of inputs. 0 if invalid
"""
def validateInput(userArgs):
    try:
        fuzzArg = userArgs[1] == "fuzz"
        fuzzMode = userArgs[2] == "discover"
        url = userArgs[3] 
        customAuth = False
        commonWords = False
        if len(userArgs) == 5:
            commonWords = "--common-words=" in userArgs[4]
            return (len(userArgs))
        elif len(userArgs) == 6:
            customAuth = "--custom-auth=" in userArgs[4]
            commonWords = "--common-words=" in userArgs[5]
            return (len(userArgs))
    except IndexError:
        print("***Invalid args*** \nUsage: fuzz discover <url> [--custom-auth=<string>] --common-words=<filename>")
        return 0

"""
Uses the common words file to guess all pages that can be reached
from the given url. 
"""
def guessPages(url, commonWords, session):
    pages = []
    extensions = ["", ".php", ".jsp"]
    for word in open(commonWords):
        for extension in extensions:
            page = url + "/" + word.strip("\n") + extension
            request = session.get(page)
            if (request.status_code == requests.codes.ok):
                pages.append(page)
            print("PAGE GUESSED -->  " + page + "\tSTATUS CODE --> " + str(request.status_code))
    return pages

"""
Returns all discoverable links from a given root url.
"""
def discoverLinks(url, session):
    neighborLinks = []
    html = session.get(url).text
    
    for link in bs4.BeautifulSoup(html, "html.parser", parse_only = bs4.SoupStrainer('a')):
        if link.has_attr("href"):
            neighborLinks.append(link.get("href"))
    return neighborLinks

"""
Returns a requests.Response object.
"""
def authenticate(authTo, session):
    #hard-coded
    if (authTo == "dvwa"):
        session.put("http://127.0.0.1/dvwa/login.php", data = {"username" : "admin", "password" : "password"})
    elif (authTo == "bodgeit"):
        pass
"""
Returns all url inputs discovered
"""
def parseURL(url):
    plainUrl, inputs = url.split("?", 1)
    inputs = inputs.split("&")
    discoveredInputs = list()
    for field in inputs:
        fieldName = field.split("=")[0]
        discoveredInputs.append(fieldName)

    print("BASE URL: " + plainUrl)
    return discoveredInputs

"""
Returns discovered cookies
"""

def fuzz(userArgs):
    #validate input, init vars
    numArgs = validateInput(userArgs)
    if (numArgs != 0):
        customAuth = ""
        url = userArgs[-2]
        commonWords = userArgs[-1].split("=")[1]
        if (numArgs == 6):
            customAuth = userArgs[-2].split("=")[1]
            url = userArgs[-3]
            
    #session used in entire fuzzer        
    session = requests.session()      

    #discover
    guessedPages = []
    if (userArgs[2] == "discover"):
        if (customAuth != ""):
            authenticate(userArgs[4].split('=')[1], session)
        guessedPages = guessPages(url, commonWords, session)
        print("GUESSED PAGES: " + str(guessedPages) + "\n")
        print("DISCOVERED LINKS: " + str(discoverLinks(url, session)))
        print("DISCOVERED URL INPUTS" + str(parseURL(url)))
    
    elif (userArgs[2] == "test"):
        pass #do test stuff
        



if __name__ == "__main__":
    fuzz(sys.argv)
    