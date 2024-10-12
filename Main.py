import sys
import datetime

if len(sys.argv) != 2:
    print("Usage: python load_file.py <file_path>")
    sys.exit(1)

file_path = sys.argv[1]
parsestart = datetime.time
print ('starting parse...')

lines = []
linecount = 0
try:
    with open(file_path, 'r') as f:
        for line in f:
            lines.append(line[11:])
            linecount+=1

except FileNotFoundError:
    print(f"The file {file_path} does not exist.")
except Exception as e:
    print(f"An error occurred: {e}")  

linecount-=1
x=0
startx=0
for line in lines:
    if line.find('You hit')>0:
         startx=line.find('You hit')
         break
         
    if line.find('You hit')<=0:
        x+=x


starth = int(lines[startx][:2])
startm = int(lines[startx][:5][3:])
starts = int(lines[startx][:8][6:])


starttime = datetime.datetime(1970,1,1,starth, startm,starts)

endh = int(lines[linecount][:2])
endm = int(lines[linecount][:5][3:])
ends = int(lines[linecount][:8][6:])

endtime = datetime.datetime(1970,1,1,endh,endm,ends)


finaltime =  (endtime.minute * 60)-(starttime.minute*60) + endtime.second - starttime.second
print('Log time:', finaltime, 'seconds')

x = 0
for line in lines:
    lines[x]= line[9:]
    if x > linecount:
        break
    x+=1


attacks=[]
numattacks = 0
x = 0
for line in lines:
    if line[:7]=='You hit':
        attacks.append(line[8:].strip())
        numattacks+=1
    if x > linecount:
        break
    x+=1
numattacks-=1

print('Number of Attacks:', numattacks)
print('Actions per Second:',numattacks/finaltime)

x=0
temp=''
stage2=[]
for line in attacks:
    temp=line[line.find('with your')+9:]
    stage2.append(line[line.find('with your')+9:])
    if x > numattacks:
        break
    x+=1

x=0
stage3=[]