import os
from pathlib import Path



# Destination=Path(os.path.join(Currrent,"test"))
MB=1024*1024


# This will send the file in parts
def ReciveFiles(Destination,Filename):
    with open(file=os.path.join(Destination,Filename),mode="rb") as Source:
        
            Part=1
            while True: #Data in the file 
                FileContent=Source.read(16*MB)
                if not FileContent:
                    break  #File is done
                filename=os.path.join(Destination,f"test{Part}.mp4")
                with open(file=filename,mode="wb") as Output:
                    Output.write(FileContent)
                    Output.close()
                print(f"Created:Part{Part}")
                Part+=1
    return Part

#This will extract the contents now and then delete the parts
def AppendFiles(Destination,Filename,Part):
    with open(file=os.path.join(Destination,Filename),mode="+ab") as Output:
        for filePart in range (1,Part):
            filename=os.path.join(Destination,f"test{filePart}.mp4")
            with open(file=filename,mode="rb") as Data:
                FileContent=Data.read()
                Output.write(FileContent)
                Data.close()
                os.remove(filename)
                print(f"Deleted:Part{Part}")
            print(f"Appended:Part{Part}")
                

