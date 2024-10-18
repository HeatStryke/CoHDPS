import sys
import datetime as dt
from datetime import timedelta
from datetime import date
import re
import pandas as pd
from pytimeparse.timeparse import timeparse
#import dash
#from dash import Dash, dcc, html, Input, Output, callback, dash_table
#import plotly.express as px
#import dash_bootstrap_components as dbc



def ParseFunction(file_path,tba):
    
    parsestart = dt.time
    outputstring='starting parse...\n'
    lines = []
    linecount = 0


    try:
        with open(file_path, 'r') as f:
            for line in f:
                lines.append(line[11:])
                linecount+=1

    except FileNotFoundError:
        return "The file {file_path} does not exist."
    except Exception as e:
        return f"An error occurred: {e}"
    
    linecount-=1
    x=0
    startx=0
    dmgorheal=[]
    timedata=[]
    source=[]
    attack=[]
    amount=[]
    healing = []
    damagetype=[]
    damageclass=[]
    next=0
    lasttime=''
    Chunk=[]
    chunkcount=1
    timetest=0
    target=[]
    temp=0
    endpos=-1
    dmgpos=0
    temptype=''
    datacount=0
    testtype=[]
    badline=0
    y=0

    #parse text file
    for line in lines:

        #Determine source
        if line[8:16].strip()=='You hit' and line.find('endurance')==-1:
            source.append('You')
            next=17
            temptype='hurt'
        elif line[8:17].strip()=='You heal':
            source.append('You')
            next=18
            temptype='heal'
        elif line.find(':  You hit')!=-1:
            endpos = line.find(':  You hit') 
            if endpos != -1:
                source.append(line[8:endpos].strip())
                next=endpos+10
            temptype='hurt'
        else:
            badline+=1
            continue
    
        
         

        #Get Time, getting time after source to ensure we're pulling only combat data
        timedata.append(line[:8])
        thistime=timeparse(line[:8])

        #break fights up into chunks if 90 seconds have passed between combat
        if lasttime!='':
            timetest=thistime-lasttime
            if timetest>=tba:
                chunkcount+=1

        lasttime=thistime
        Chunk.append(chunkcount)

        #back to comabt data, finding attack target.
        if temptype=='hurt':
            temp=line.find('with your')
            target.append(line[next:temp].strip())
            next=temp
            dmgorheal.append(temptype)
        elif temptype=='heal':
            temp=line.find('with')
            target.append(line[next:temp].strip())
            next=temp
            dmgorheal.append(temptype)
        else:
            continue
            y+=1

        testtype.append(temptype)
        #pulling attack/ability name
        if temptype=='hurt':
            templine = line[next+9:]
            first_digit = re.search(r"\d", templine)
            attack.append(templine[:first_digit.start()-4].strip())
            next=+temp+4
            
        if temptype=='heal':
            templine = line[next+4:]
            first_digit = re.search(r"\d", templine)
            attack.append(templine[:first_digit.start()-4].strip())
            next=+next+4

        #damage amount time!

        temp = re.findall(r"[-+]?(?:\d*\.*\d+)",  line[next:])
        
        tempdmg =float(''.join(map(str, temp)))
        amount.append(tempdmg)
        next+=len(str(tempdmg))+10
        
        #damage class and type
        
        templine=line[next:]
        if temptype == 'hurt':
        
            if line[-8:].strip()=='damage.':
                x+=1
                pos=line[next:].find('of')
                damageclass.append('Damage')
                damagetype.append(templine[pos+2:-8].strip())
            elif line[-18:].strip()=='damage over time.':
                x+=1
                pos=line[next:].find('of')
                damageclass.append('DOT')
                damagetype.append(templine[pos+2:-18].strip())
            else:
                damageclass.append('n/a')
                damagetype.append('n/a')
                
        elif temptype=='heal':
            x+=1        
            damageclass.append('Healing')
            damagetype.append('n/a')
        else:
            outputstring= outputstring ,'error'
            continue
        datacount+=1

        


    data = {'Chunk':Chunk, 'Time':timedata,'Source':source, 'Attack':attack,'Target':target, 'Amount':amount, 'Damage_Type':damagetype,'Damage_Class':damageclass}
    #print (len(Chunk),len(timedata),len(source),len(attack),len(target),len(amount),len(amount),len(damagetype),len(damageclass))
    df=pd.DataFrame(data)

    #END FUNCTION HERE

    #determine time by chunk
    time1=0
    time2=0
    timeloc1=0
    timeloc2=0
    chunktime=0
    conditions=''
    tf=pd.DataFrame()
    
    for i in range(1,chunkcount+1):

        outputstring= outputstring+ 'Combat ' + str(i) + "\n"
        timeloc1=df[df['Chunk'] ==i].iloc[0]
        timeloc2=df[df['Chunk'] ==i].iloc[-1]
        
        time1=timeparse(timeloc1['Time'])
        time2=timeparse(timeloc2['Time'])

        chunktime=time2-time1
        outputstring=outputstring +"\nDuration in Seconds: " + str(chunktime) +"\n"
        
        #DPS by chunk
        condition = (df['Chunk']==i) & ((df['Damage_Class']=='Damage') | (df['Damage_Class']=='DOT'))
        tf=df.loc[condition]
        totaldamage=tf['Amount'].sum()

        outputstring= outputstring +"\nTotal DPS: "+ str(round(totaldamage/chunktime,2))+"\n"

        #HPS by Chunk
        condition = (df['Chunk']==i) & (df['Damage_Class']=='Healing')
        tf=df.loc[condition]
        totaldamage=tf['Amount'].sum()

        outputstring= outputstring +"Total HPS: "+ str(round(totaldamage/chunktime,2))+"\n"

        #DPS by Source and Chunk
        
        outputstring= outputstring + "\nDPS by Source\n"
        namelist = df['Source'].unique()

        for item in namelist:
            
            condition = (df['Chunk']==i) & (df['Source']==item)& ((df['Damage_Class']=='Damage') | (df['Damage_Class']=='DOT'))
            tf=df.loc[condition]
            totaldamage=tf['Amount'].sum()
            if totaldamage!=0:
                outputstring= outputstring +str(item) +": "+ str(round(totaldamage/chunktime,2)) +"\n"
        #HPS by Source and Chunk
        
        outputstring= outputstring +"\nHPS by Source\n"

        for item in namelist:
            
            condition = (df['Chunk']==i) & (df['Source']==item)& (df['Damage_Class']=='Healing')
            tf=df.loc[condition]
            totaldamage=tf['Amount'].sum()
            if totaldamage!=0:
                outputstring= outputstring +str(item)+": "+str(round(totaldamage/chunktime,2))+"\n"

        #DPS by Type(element) and Chunk

        typelist=df['Damage_Type'].unique()
        #print(typelist)
        outputstring= outputstring +"\nDPS by Type\n"

        for item in typelist:
            if item != 'n/a':
                condition = (df['Chunk']==i) & (df['Damage_Type']==item)& ((df['Damage_Class']=='Damage') | (df['Damage_Class']=='DOT'))
                tf=df.loc[condition]
                totaldamage=tf['Amount'].sum()
                if totaldamage!=0:
                    outputstring= outputstring +str(item)+": "+str(round(totaldamage/chunktime,2))+"\n"

        #DPS/HPS by Ability name
        abilitylist=df['Attack'].unique()
        
        outputstring= outputstring +"\nDPS by Attack\n"
        
        for item in abilitylist:
            if item != 'n/a':
                condition = (df['Chunk']==i) & (df['Attack']==item)& ((df['Damage_Class']=='Damage') | (df['Damage_Class']=='DOT'))
                tf=df.loc[condition]
                totaldamage=tf['Amount'].sum()
                if totaldamage!=0:
                    outputstring= outputstring +str(item)+": "+str(round(totaldamage/chunktime,2))+"\n"
       
        outputstring= outputstring +"\nHPS by Ability:\n"

        for item in abilitylist:
            if item != 'n/a':
                condition = (df['Chunk']==i) & (df['Attack']==item)& (df['Damage_Class']=='Healing')
                tf=df.loc[condition]
                totaldamage=tf['Amount'].sum()
                if totaldamage!=0:
                    outputstring= outputstring +str(item)+": "+str(round(totaldamage/chunktime,2))+"\n"


    
    outputstring= outputstring +"parse complete..."
    
    return outputstring

#dft = pd.DataFrame

dft=ParseFunction(sys.argv[1],45)
print(dft)


# chunkcount = df[df.columns[0]].count()
# #GUI goes here :)

# app = Dash()
# app.layout = html.Div(
#     [
#         html.H4("City of Heroes DPS/HPS Parser"),
#         dcc.Graph(id="graph"),
#         html.P("Combat:"),
#         OptionList = [{'label': i, 'value': i} for i in dft.unique()]
#         dcc.Dropdown(
#             id="combat",
#             options=[],
#             value="DPS",
#             clearable=False,
#         ),
#         html.P("DPS/HPS:"),
#         dcc.Dropdown(
#             id="class",
#             options=["Damage", "Healing"],
#             value="DPS",
#             clearable=False,
#         ),
#         html.P("Graph Type:"),
#         dcc.Dropdown(
#             id="type",
#             options=["By Source", "By Attack", "By Type"],
#             value="By Source",
#             clearable=False,
#         ),
#     ]
# )

# @app.callback(
#     Output("combat", "class","type"),
#     Input("combat", "value"),
#     Input("class", "value"),
#     Input("type", "value"),
# )


# def generate_chart(combat, dclass, type,df):
#     if dclass != 'Healing'
#     tf = df.loc[df['Chunk'==combat, 'Damage Class'==dclass]]
#     fig = px.pie(df, , hole=0.3)
#     return fig


# # Run the app
# if __name__ == '__main__':
#     app.run(debug=True)
