import os 
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

def CreateDir(Userid,Directory,Filename):
    # DIR=Path(os.getenv("DestinationFolder")) #FEZ
    try:
        DIR=Path(r"D:\CODE\PYTHON\CODE\Projects\Personaldrive\test")
        #Check if Userid exists
        Userid=str(Userid)    
        if Directory is None:
            DIR=os.path.join(DIR,Userid)
        else:
            DIR=os.path.join(DIR,Userid,Directory)
        # print(DIR)
        Path(DIR).mkdir(parents=True, exist_ok=True)
        return os.path.join(DIR,Filename)
    except Exception as e:
        return 0
    
if __name__=="__main__":
    print(CreateDir(Directory=None,Filename="1",Userid="1"))
    import shutil
#     shutil.rmtree(
#     os.path.join(
#         r"D:\CODE\PYTHON\CODE\Projects\Personaldrive\test",
#         "1",
#         "1"
#     )
# )
    