import sys
import datetime
import re
import pandas as pd


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

#Parsing
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
attackname=[]
alen =0
dmgpos=0
for line in stage2:
    dmgpos = re.search(r"\d", line)
    attackname.append(line[:dmgpos.start()-4].strip())
    if x >= numattacks:
        break
    x+=1

damage=[]
x=0
dmgpos=[]




for line in stage2:
    dmgpos = list(map(int, re.findall(r'\d+', line)))
   
    if len(dmgpos) != 1:
        print(dmgpos)
        damage.append(dmgpos[0]+(dmgpos[1]/100))
    else:
        
        damage.append(dmgpos[0])
    if x >= numattacks:
        break
    x+=1

Atktype=[]
x=0
pos=0
dmgtype=[]
atype=''
for line in stage2:
    pos=line[20:].find('of')+20
    
    atype=line[pos+3:]
    Atktype.append(atype)

    if atype.find('time')>0:
        dmgtype.append("dot")
    else:
        dmgtype.append("normal")
    
    if x >= numattacks:
        break
    x+=1

#Final Sorting
atknames = list(set(attackname))
al = pd.Series(attackname)
dmg = pd.Series(damage)
dt = pd.Series(dmgtype)
dc = pd.Series(Atktype)
x=0
atkdmgdf = pd.DataFrame()
atkdmgdf['Atkname'] = al
atkdmgdf['damage'] = dmg
atkdmgdf['dmgtype'] = dt
atkdmgdf['atktype']=dc

data = {'Attack':al,'Damage':dmg,'Damage Type':dc,'Damage Class':dt}

atkdps = pd.DataFrame(data)
atkdps = atkdps[atkdps['Damage Type'].str.contains('damage')==True]

agg_functions = {'Attack':'first','Damage Type':'first', 'Damage': 'sum'}
newdps = pd.DataFrame()
newdps = atkdps.groupby(['Attack','Damage Type'])['Damage'].sum().reset_index

adps = pd.DataFrame()
adps = atkdps.groupby(['Attack'])['Damage'].sum().div(finaltime).reset_index
print('DPS per Attack:')
print(adps)
print('')
print('')
tdps = pd.DataFrame()
tdps = atkdps.groupby(['Damage Type'])['Damage'].sum().div(finaltime).reset_index

print('DPS per Type:')
print(tdps)
print('')
print('')
totdps = atkdps['Damage'].sum()
totdps = totdps/finaltime
print('Total DPS:')
print(totdps)
