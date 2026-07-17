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
        return str(Fileoperation.joinpath(DIR,Filename)) #Return the path where the file is supposed to be stored
    
            

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
        Fileextension='application/zip'
    else:
        Fileextension=Fileoperation.getextenstion(filepath=filepath)
    return [filepath,Filesize,Fileextension]


def checkchangesinstats(userid):
       # Createfilestructure(Userid)  ##Just for the timebeing
    PATH=Fileoperation.getstatsfile(userid)
    try:
        data = Fileoperation.jsonread(userid=userid, path=PATH)
        if isinstance(data, dict):
            return not data.get("update", 0) # 1 is file change 
        return 0
    except Exception:
        return 0
    


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
    