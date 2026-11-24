from flask import Flask, render_template, request

app=Flask(__name__)


@app.route("/",methods=["GET", "POST"])
def home():
    if request.method == "POST":
        global formInput
        formInput = request.form['ipAddress']
        if Calculate() == False:
            return render_template(
                "index.html", 
                error=errorVariable
                )
        else:
            return render_template(
            "index.html", 
            ip=ipAddress, 
            subnet=subnetMask, 
            cidr=cidrPrefix, 
            host=hostCount, 
            network=networkAddress, 
            broadcast=broadcastAddress, 
            range=networkRange
            )
    return render_template("index.html")

# helper Functions
def clearVariables():
    global errorVariable, infoList, p2pCheck, oneAddressCheck
    p2pCheck = False
    oneAddressCheck = False
    infoList = []
    infoList.append("startup")
    errorVariable = "startup"
    return True
        
def validatePrefix(checkedvalue):
    global p2pCheck, oneAddressCheck, wholeRangeCheck, errorVariable #, infoList
    if checkedvalue == "":
        #infoList.append("apparently empty string triggered")
        return False
    else:
        #infoList.append("validatePrefix passed empty string check")
        try:
            checkedvalue = int(checkedvalue)
            if checkedvalue > 32 or checkedvalue < 0: # checks if prefix is negative or too high
                print("valPrefix returned False Number too high or low")
                #infoList.append("validatePrefix, number too high")
                return False
            elif checkedvalue == 0:
                wholeRangeCheck = True
                return True
            elif checkedvalue == 31: # the edge case
                p2pCheck = True
                return True
            elif checkedvalue == 32:
                oneAddressCheck = True
                return True
        except ValueError:
            errorVariable = "ValidatePrefix"
            return False
        return True

def validateIP(checkedIP):
    global errorVariable, ipStrList, ipIntList
    ipStrList = checkedIP.split(".")
    try:
        ipIntList = list(map(int, ipStrList)) # checks if it can be converted into an integer
        if len(ipStrList) != 4:
            errorVariable = "validateIP, bad length"
            return False
        elif any(octet < 0 or octet > 255 for octet in ipIntList): # checks whether the subnetmask parts are positive and max 8 bits 
            errorVariable = "validateIP, octet"
            return False
        else:
            return True
    except ValueError: 
        errorVariable = "validateIP, not an int"
        return False

def checkValidValues():
    global ipAddress, cidrPrefix, errorVariable #, infoList
    #infoList.append("checkValidValues Triggered")
    try:
        prefixStrList=formInput.split("/")
        ipAddress=prefixStrList[0]
        cidrPrefix=int(prefixStrList[1])
        if validatePrefix(cidrPrefix) and len(prefixStrList) == 2:
            #infoList.append("Prefix Valid")
            if validateIP(ipAddress):
                #infoList.append("checkValidIP Passed")
                return True
            else:
                errorVariable = "validateIP"
                return False
        else:
            errorVariable = "validatePrefix"
            return False
    except:
        errorVariable="bitchass wrong input"

def cidrConvert():
    global subnetMask, cidrBinList, subnetIntList, subnetBinList #, infoList
    cidrOctetList: list[str]=[]
    highCounter: int = cidrPrefix
    dotCounter: int = 8
    for octetCounter in range(32):
        dotCounter = dotCounter - 1
        highCounter = highCounter - 1
        if highCounter >= 0:
            cidrOctetList.append("1")
        else:
            cidrOctetList.append("0")
        if dotCounter == 0:
            dotCounter = 8
            if octetCounter == 31:
                #infoList.append("Break cidrBin")
                break
            cidrOctetList.append(".")
    cidrBinStr: str = "".join(cidrOctetList) 
    cidrBinList = cidrBinStr.split(".") 
    subnetIntList = [int(octet, 2) for octet in cidrBinList]
    subnetBinList = [format(i, '08b') for i in subnetIntList] 
    subnetStrList: list[str] = []
    for counter in range(4):
        subnetStrList.append(str(subnetIntList[counter]))
    subnetMask=".".join(subnetStrList)
    return True

def defineResults():
    global cidrPrefix, hostCount, broadcastAddress, networkAddress, networkRange #, infoList
    
    # hostcount
    hostCount = 0
    if cidrPrefix == 31:
        hostCount = 2
    elif cidrPrefix == 32:
        hostCount = 1
    else:
        subnetCount = 0
        for octet in cidrBinList:
            subnetCount += (octet.count("0"))
        hostCount = int((2 ** subnetCount) - 2)
    
    # network address & rangeLow
    networkAddress = ""
    networkAddressList: list[str] = []
    rangeLow = ""
    for counter in range(4):
        networkAddressList.append(subnetIntList[counter] & ipIntList[counter])
    rangeLowList = networkAddressList.copy()
    if p2pCheck or oneAddressCheck:
        pass
    else:
        rangeLowList[3] = rangeLowList[3] + 1
    rangeLow = ".".join(list(map(str, rangeLowList)))
    networkAddress = ".".join(list(map(str, networkAddressList)))

    # broadcast address & rangeHigh
    broadcastAddress = ""
    rangeHigh = ""
    subnetWildcardList = []
    broadcastAddressList = []
    for counter in range(4):
        subnetWildcard = subnetBinList[counter].replace("1", "2")
        subnetWildcard = subnetWildcard.replace("0", "1")
        subnetWildcard = subnetWildcard.replace("2", "0")
        subnetWildcardList.append(subnetWildcard)
    subnetWildcardList = [int(octet, 2) for octet in subnetWildcardList]
    for counter in range(4):
        broadcastAddressList.append(subnetWildcardList[counter] | ipIntList[counter])
    rangeHighList=broadcastAddressList.copy()
    if p2pCheck or oneAddressCheck:
        pass
    else:
        rangeHighList[3] = rangeHighList[3] - 1
    broadcastAddress = ".".join(list(map(str, broadcastAddressList)))
    rangeHigh = ".".join(list(map(str, rangeHighList)))
    networkRange = f"{rangeLow} - {rangeHigh}"
    cidrPrefix = "/"+str(cidrPrefix)
    return True


# main function
def Calculate():
    global errorVariable
    if not clearVariables():
        errorVariable = "clearVariables error"
        return False
    else:
        if not checkValidValues(): 
            errorVariable = "checkValidValues error"
            return False    
        else:
            if not cidrConvert():
                errorVariable = "cidrConvert error"
                return False
            else:
                if not defineResults():
                    errorVariable = "defineResults error"
                    return False
                else:
                    #infoList.append("script passed")
                    return True
                    
                


if __name__ == "__main__":
    app.run(debug=False)
