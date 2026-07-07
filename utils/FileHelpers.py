from .Storage import get_storage

Fileoperation=get_storage()

def CreateDir(Userid,Directory,Filename):
    try:
        DIR=Fileoperation.source
        Userid=str(Userid)
        if Directory is None:
            DIR=Fileoperation.joinpath(DIR,Userid)
        else:
            DIR=Fileoperation.joinpath(DIR,[Userid,Directory])
        Fileoperation.Createfolder(userid=Userid,filepath=DIR)        
        Filename=Fileoperation.getfilename(userid=Userid,filepath=Filename)
        return str(Fileoperation.joinpath(DIR,Filename)) #Returnt the paths where the file is supposed to store
    
            

    except Exception as e:
        print(e)
        return 0    


def filedetails(userid,filepath):
    Source=Fileoperation.source 
    orginalfile=filepath
    filepath=Fileoperation.joinpath(Source,[str(userid),filepath])

    try:
        Filesize=Fileoperation.Filesize(userid=userid,filepath=orginalfile)
    except FileNotFoundError as e:
        return [None]*3
    if Fileoperation.isdirectory(filepath):
        Fileextenstion='application/zip'
    else:
        Fileextenstion=Fileoperation.getextenstion(filepath=filepath)
    return [filepath,Filesize,Fileextenstion]


def checkchangesinstats(userid):
       # Createfilestructure(Userid)  ##Just for the timebeing
    PATH=Fileoperation.getstatsfile(userid)
    try:
        data=Fileoperation.jsonread(userid=userid,path=PATH)
        return not  data["update"] # 1 is file chnage 
       
    except (FileNotFoundError,TypeError,Exception) as e:
        return 0 #mesan file is not here 
    


if __name__=="__main__":
    print(CreateDir(Directory=None,Filename=r"Live.mp4",Userid="1"))
    import shutil
#     shutil.rmtree(
#     os.path.join(
#         r"D:\CODE\PYTHON\CODE\Projects\Personaldrive\test",
#         "1",
#         "1"
#     )
# )
    