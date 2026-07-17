import time 
from utils.Databaseop import getemail,changepwd
import secrets
Data={}
Email={}
USERIDS={}
allowed=(60*10)+10
def __inputval(email,otp):
    try:
        global Data
        Data[email]={"OTP":otp,"ALLOW":int(time.time())+(allowed)}
        return 1
    except Exception as e:
        return 0
    
    
def __Validator(email,otp):
    global Data
    curnt=int(time.time())
    statuscode=400
    if email not in Data:
        return [0,{"return":"No Record of that email"}]
    values= Data[email]
    if values["OTP"]!=otp:
        return [0,{"return":"Wrong OTP"}]
    if values["ALLOW"]<curnt:     
        del Data[email]
        return [0,{"return":"Time Exceeded"}]
    statuscode=200
    #Now i need to check the db for the availablity of the users email
    
    code=getemail(email=email)
    if not code[0]:
        return[ 0,{"return":f"There has been an error: {code[1]}"}]
    ##save the userids
    global USERIDS
    USERIDS[email]=code[1]
    return [1,1]

def __savetoken(email):
        token=secrets.token_urlsafe(32)
        global  Email
        Email[email]={"token":token,"ALLOW":int(time.time())+(allowed)} ##tokensave
        return token


def __verifytoken(email,token,password):
    global Email
    act=Email.get(email)
    if act is None:
        return [0,"Email Not found"]
    #Now compare the token
    root=Email[email]
    if token!=root["token"]:
        return [0,"Wrong token sent by the client"]
    #verify the time now
    curnt=int(time.time())
    if  curnt > root["ALLOW"]:
        del Email[email]
        return [0,"Time Over, please verify the otp once again"]
    ##Edge cases done now real game
    #get the Userid to save time
    ##retrieve the user
    global USERIDS
    id=USERIDS[email]
    val=changepwd(useid=id,password=password)
    return [val[0],val[1]]
    
    
    
    

def STORAGE(email,otp=None,action="Create",password=None,token=None):
    if action=="check":
        info=__Validator(email,otp)
        if not info[0]:
            return [info[0],info[1]]
        sestoken=__savetoken(email)
        return [info[0],{"return":sestoken}]
    if action=="token":
        result=__verifytoken(email,token,password)
        return [result[0],{"return":result[1]}]
    values=__inputval(email,otp)
    if not values:
        return "There has been an error! Please try again.",401
    return "code has been sent to your email",200


