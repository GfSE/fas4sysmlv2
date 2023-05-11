#   Copyright 2022 Gesellschaft fuer Systems Engineering e.V. (GfSE)
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#        http://www.apache.org/licenses/LICENSE-2.0  
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
#   This is the main py file of the FAS plugin for SysML v2
#   When calling as a script, pass the project ID as an optional first parameter
#
#   This script requires the tkinter for GUI and sympy for symbolic computation
# 
#   Based on the following paper in german language : Lamm, J.G.: "Eine schlanke 
#   Formel fuer den Kern der FAS-Methode, zur einfachen Werkzeug-Umsetzung 
#   der Methode", in Koch, W.; Wilke, D.; Dreiseitel, S.; Kaffenberger, R. (Eds.): 
#   Tag des Systems Engineering - Paderborn 16.-18. November 2022, 
#   Gesellschaft fuer Systems Engineering e.V. (GfSE Verlag), Bremen, Germany, 
#   2022, pp. 127-131
#
#   English Translation of the above paper: 
#   https://github.com/GfSE/fas4sysmlv2/blob/main/doc/tech-docs/fas/FAS-as-a-formula-2022.odt             
#

import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter import scrolledtext
from tkinter import ttk
from functools import partial
import sys

from sympy import *

import requests 


#### BEGIN TEMP The following part needs to be solved more clever

def strfind_zerobased(cStringtoSearch, cCharToFind):
    return [nCounter for nCounter, currentChar in enumerate(cStringtoSearch) if currentChar == cCharToFind]

def SubFlow(sFlowString,nPort):
     sCurrentFlowName = sFlowString.strip()
     POS = strfind_zerobased(sCurrentFlowName,'+')
     if len(POS) > 0:      
         if nPort == 0:
             sTempStr = sCurrentFlowName[:POS[nPort]]
             sCurrentFlowName = sTempStr.strip();
         elif nPort >= len(POS):
             sTempStr = sCurrentFlowName[(POS[nPort-1]+1):]
             sCurrentFlowName = sTempStr.strip();
         else:
             sTempStr = sCurrentFlowName[(POS[nPort-1]+1):POS[nPort]]
             sCurrentFlowName = sTempStr.strip();
      
     return sCurrentFlowName


def parseGroupLine (sLine):
      
     iCount=0
     clGroup = []
     sGroupName = ''
    
     sComposedString = ''
    
     for nIndex in range(len(sLine)):
         if sLine[nIndex]==':' or sLine[nIndex]==';':
             iCount = iCount + 1;
             if iCount == 1:
                 sGroupName = sComposedString
             else:
                 clGroupNew = ['' for col in range(len(clGroup)+1)]
                 for nFillIndex in range(len(clGroup)):
                     clGroupNew[nFillIndex] = clGroup[nFillIndex][0] 
                 clGroupNew[len(clGroupNew)-1] = sComposedString 
                 clGroup = clGroupNew 
             sComposedString = '';
         else:
            if sLine[nIndex] != ' ':
                 sTempString = sComposedString + sLine[nIndex]
                 sComposedString = sTempString.replace('.','_')
    
     if len(sComposedString)>0:
         clGroupNew = ['' for col in range((len(clGroup)+1))]
         for nFillIndex in range(len(clGroup)):
             clGroupNew[nFillIndex] = clGroup[nFillIndex]
       
         #print('sComposedString: ' + sComposedString)
         clGroupNew[len(clGroupNew)-1] = sComposedString 
         clGroup = clGroupNew
    
     return sGroupName, clGroup


def parseFlowLine (sLine):
    
     sSourceObject =''
     sFlow = ''
     sTargetObject = ''
    
     iCount=0
    
     sComposedString = ''
    
     for nIndex in range(len(sLine)):
         if sLine[nIndex]==':' or sLine[nIndex]==';':
             iCount = iCount + 1
             if iCount == 1:
                 sSourceObject = sComposedString
             elif iCount == 2:
                 sFlow = sComposedString;
             else:
                 sTargetObject = sComposedString;
          
          
             sComposedString = '';
         else:
             if sLine[nIndex] != ' ':
                 sTempString = sComposedString + sLine[nIndex]
                 sComposedString = sTempString.replace('.','_')

     if iCount == 2:
         sTargetObject = sComposedString;
    
     return sSourceObject,sFlow,sTargetObject

def GetIndexOfStringInCellArray(clIn,sContent):
     # iIndex = -1 if not found        
     iIndex = -1
     for iCount in range (len(clIn)):
         if clIn[iCount]==sContent:
             iIndex = iCount
             break
     return iIndex  


def UpdateUniqueContentCellArray (clIn, sContent):
     iIndex = GetIndexOfStringInCellArray(clIn,sContent)

     if iIndex == -1:
         clOut = ['' for col in range((len(clIn)+1))]
         for nFill in range(len(clIn)):
             clOut[nFill]=clIn[nFill]
         clOut[len(clOut)-1]=sContent
     else:
         clOut = clIn

     return clOut

#### END TEMP



def SymbolicUpdateMatrixWithFlow(clDomainObjects,clActivities,mMatrixO, sLineToParse):
     sSourceObject,sFlow,sTargetObject = parseFlowLine(sLineToParse)
     clActivities = UpdateUniqueContentCellArray (clActivities, sSourceObject)
     clActivities = UpdateUniqueContentCellArray (clActivities, sTargetObject)
     clDomainObjects = UpdateUniqueContentCellArray (clDomainObjects, sFlow)
     M = len(clActivities);
     mNewMatrixO = Matrix([[0 for col in range(M)] for row in range(M)])
     for nInitIndex1 in range(M):
         for nInitIndex2  in range(M):
             mShape=mMatrixO.shape
             if nInitIndex1 < mShape[0] and nInitIndex2 < mShape[0]:
                 mTemp = [[0 for col in range(M)] for row in range(M)]
                 mTemp[nInitIndex1][nInitIndex2] = mMatrixO[nInitIndex1,nInitIndex2]
                 mNewMatrixO = mNewMatrixO + Matrix(mTemp)
             if GetIndexOfStringInCellArray(clActivities,sSourceObject) == nInitIndex1 and GetIndexOfStringInCellArray(clActivities,sTargetObject) == nInitIndex2 :
                 mTemp = [[0 for col in range(M)] for row in range(M)]
                 sFlowSymbolic = symbols(sFlow)
                 mTemp[nInitIndex1][nInitIndex2] = sFlowSymbolic
                 mNewMatrixO = mNewMatrixO + Matrix(mTemp)

    
     return clDomainObjects,clActivities,mNewMatrixO 
 
 
def RenderFunctionalArchitecture(F,clFunctionalBlockNames):
  
     cSysMLstring = '   part FunctionalSystem{' + '\r\n'

    
     clSourcePortNames = [['' for col in range(F.shape[0])] for row in range(F.shape[0])]
     clTargetPortNames = [['' for col in range(F.shape[0])] for row in range(F.shape[0])]
     for nBlock in range(F.shape[0]):
         cCurrentBlock = clFunctionalBlockNames[nBlock]
         cSysMLstring = cSysMLstring + '      part ' + cCurrentBlock + '{' + '\r\n'
         iPortNo = 0
         for nPortOut in range(F.shape[0]):
             if F[nBlock,nPortOut]!= 0: 
                 if nPortOut != nBlock:
                     sFlowName = str(F[nBlock,nPortOut])
                     iNumPorts = max(1,sFlowName.strip().count('+')+1)
                     clPortCell = ['' for col in range(iNumPorts)]
                     for nPort in range(iNumPorts):
                         iPortNo = iPortNo  + 1
                         cPortName = 'p' + str(iPortNo)
                         cSysMLstring = cSysMLstring + '         port ' + cPortName + ';' + '\r\n'
                         clPortCell[nPort]=cPortName
            
                         clSourcePortNames[nBlock][nPortOut]=clPortCell
                 
         for nPortIn in range(F.shape[0]):
             if F[nPortIn, nBlock]!= 0: 
                 if nPortIn != nBlock:
                     sFlowName = str(F[nPortIn,nBlock])
                     iNumPorts = max(1,sFlowName.strip().count('+')+1)
                     clPortCell = ['' for col in range(iNumPorts)]
                     for nPort in range(iNumPorts):
                         iPortNo = iPortNo + 1
                         cPortName = 'p' + str(iPortNo)
                         cSysMLstring = cSysMLstring + '         port ' + cPortName + ';' + '\r\n'
                         clPortCell[nPort]=cPortName
               
                         clTargetPortNames[nPortIn][nBlock]=clPortCell
         cSysMLstring = cSysMLstring + '      }' + '\r\n'
   
    
    ## Connect the blocks with flows
     cItemString = ''
    
     for nBlock1 in range(F.shape[0]):
         for nBlock2 in range(F.shape[0]):
             cFlow=F[nBlock1,nBlock2]
             if nBlock1 != nBlock2 and cFlow != 0: 
                 sFlowName = str(cFlow)
                 clSourcePorts = clSourcePortNames[nBlock1][nBlock2]
                 clTargetPorts = clTargetPortNames[nBlock1][nBlock2]
                 for nPort in range(len(clSourcePorts)):
                     sCurrentFlowName = SubFlow(sFlowName,nPort)
                     cSysMLstring = cSysMLstring + '      flow of ' + sCurrentFlowName + ' from ' + clFunctionalBlockNames[nBlock1] + '.' + clSourcePorts[nPort] + ' to ' + clFunctionalBlockNames[nBlock2] + '.' + clTargetPorts[nPort] + ';' + '\r\n'
                     cItemString = cItemString + '   item def ' + sCurrentFlowName + ';' + '\r\n'
           
    
    ## Trace Functional Blocks to Functional Groups
     if False: #This cannot be done in SysML notation; it needs to be done directly in the database, using the correct element IDs of elements to trace to
         for nBlock in range(F.shape[0]):
             sCurrentName = clFunctionalBlockNames[nBlock]
             cItemString = cItemString + '   dependency from FunctionalSystem::' + sCurrentName + ' to UseCaseActivities::FunctionalGroups::' + sCurrentName + ';' + '\r\n'
    
      
     cSysMLstring = cSysMLstring + '   }' + '\r\n' + cItemString 
   
     return  cSysMLstring



def run_fas(clActivitiesAndObjectFlows, clFunctionalGroups):

     cSysMLString=''
     cFormulaOutput = ''
    
     ### Process Activities and Object Flows
     clLinesToParse =  clActivitiesAndObjectFlows
     clDomainObjects = []
     clActivities = []
     mSymbolicMatrixO = Matrix([])
  
     for nIndex in range(len(clLinesToParse)):
         sLineToParse = clLinesToParse[nIndex]
         clDomainObjects,clActivities,mSymbolicMatrixO = SymbolicUpdateMatrixWithFlow(clDomainObjects,clActivities,mSymbolicMatrixO, sLineToParse)
     
     
     cFormulaOutput = cFormulaOutput  + 'O = (symbolic ' + str(mSymbolicMatrixO.shape[0]) + 'x' + str(mSymbolicMatrixO.shape[1]) + ' matrix)'
     cFormulaOutput = cFormulaOutput  + '\r\n' 
     cFormulaOutput = cFormulaOutput  + '\r\n' +pretty(mSymbolicMatrixO)
     cFormulaOutput = cFormulaOutput  + '\r\n' 
     
     M=mSymbolicMatrixO.shape[0]

    
     ### Process Functional Groupings
     clLinesToParse =  clFunctionalGroups  
     N = len(clLinesToParse)
     mSymbolicMatrixG = Matrix([[0 for col in range(M)] for row in range(N)])

     clGroupName = ['' for col in range(N)]
     for n in range(N):
         sLineToParse = clLinesToParse[n]
         sGroupName, clGroup = parseGroupLine(sLineToParse)
         clGroupName[n]=sGroupName
         for m in range(M):
             if GetIndexOfStringInCellArray(clGroup,clActivities[m]) > -1:
                 mTemp = [[0 for col in range(M)] for row in range(N)]
                 mTemp[n][m] = 1;
                 mSymbolicMatrixG = mSymbolicMatrixG + Matrix(mTemp)
          
   
     cFormulaOutput = cFormulaOutput  + '\r\n' + 'G = (symbolic ' + str(mSymbolicMatrixG.shape[0]) + 'x' + str(mSymbolicMatrixG.shape[1]) + ' matrix)'
     cFormulaOutput = cFormulaOutput  + '\r\n' 
     cFormulaOutput = cFormulaOutput  + '\r\n' +pretty(mSymbolicMatrixG)
     cFormulaOutput = cFormulaOutput  + '\r\n'     
    
     
     ### Compute the functional architecture via FAS-as-a-formula
     ### F = G*O*G.T;
     mSymbolicMatrixF=mSymbolicMatrixG*mSymbolicMatrixO*mSymbolicMatrixG.T;
     
     cFormulaOutput = cFormulaOutput  + '\r\n' + '---------------------------------'
     cFormulaOutput = cFormulaOutput  + '\r\n' 'Applying FAS-as-a-formula:'
     cFormulaOutput = cFormulaOutput  + '\r\n' ''
     # Explanation of "FAS-as-a-formula": https://github.com/GfSE/fas4sysmlv2/blob/main/doc/tech-docs/fas/FAS-as-a-formula-2022.odt"
     GOG,T,F = symbols('GOG, T, F')
     #This is a work-around to print the formula F=G*O*G**T in nice formatting:
     cFormulaOutput = cFormulaOutput  + '\r\n' + pretty(Eq(F, GOG**T))
     cFormulaOutput = cFormulaOutput  + '\r\n' 
     cFormulaOutput = cFormulaOutput  + '\r\n'  + '---------------------------------'
     cFormulaOutput = cFormulaOutput  + '\r\n' 
     
     cFormulaOutput = cFormulaOutput  + '\r\n' + 'F = (symbolic ' + str(mSymbolicMatrixF.shape[0]) + 'x' + str(mSymbolicMatrixF.shape[1]) + ' matrix)'
     cFormulaOutput = cFormulaOutput  + '\r\n' 
     cFormulaOutput = cFormulaOutput  + '\r\n' +pretty(mSymbolicMatrixF)
     cFormulaOutput = cFormulaOutput  + '\r\n'     
     
     ### FAS method says that names of functional blocks are equal to names of functional groups
     clFunctionalBlockNames = clGroupName
     
     ### Print the functional architecture
     cSysMLString = RenderFunctionalArchitecture(mSymbolicMatrixF,clFunctionalBlockNames)
    
     return cSysMLString, cFormulaOutput    
  

def format_servername(cName):
     if len(cName)>0:
         if cName[len(cName)-1] == '/':
            cName = cName[0:(len(cName)-1)]
         
         if cName.find('http') == -1:
            cName = 'http://' + cName
     
     return cName
  
def read_activities_and_functional_groups(strProjectID,strServerName):
     bSuccess = True
     cErrorMessage = ''
     cProjectID=strProjectID.get()
     cServerName=format_servername(strServerName.get())
     print(cProjectID)
     print(cServerName)
    
     try:
         response = requests.get(cServerName + "/projects/" + cProjectID)
     except  requests.exceptions.ConnectionError:
         bSuccess = false
         cErrorMessage = 'Error: Could not connect to server'
         print(cErrorMessage)

         
     if bSuccess and str(response)!='<Response [200]>':
         bSuccess = false
         cErrorMessage = 'Error: Could not find project on stated host'
         print('Error: Could not find project on stated host')

     
     if bSuccess:
         data = response.json()
         oDefaultBranch = data.get('defaultBranch')
         sDefaultBranchId=oDefaultBranch.get('@id')
     
         if str(type(oDefaultBranch)) == "<class 'NoneType'>":
             bSuccess = False
             cErrorMessage = 'Error: No default branch.'
             print (cErrorMessage)
     
     if bSuccess:
         response = requests.get(cServerName + "/projects/" + cProjectID + "/branches/" + sDefaultBranchId)
         data = response.json()
         oHeadCommit = data.get('head')
         if str(type(oHeadCommit)) == "<class 'NoneType'>":
             bSuccess = False
             cErrorMessage = 'Error: No commit found.'
             print (cErrorMessage)
         else:
             sHeadCommit = oHeadCommit.get('@id')

     clActions=[]
     clActionIds=[]
     clFlowIds=[]
     clFlowTargets=[]
     clFlowItems=[]
     clItemFeatureIds=[]
     clItemFeatureTypes=[]
     clItemDefs=[]
     clItemDefIds=[]
     if bSuccess:
         response = requests.get(cServerName + "/projects/" + cProjectID + "/commits/"+sHeadCommit+"/elements")
         data = response.json()
     
         for response in data:
             #if response.get("@type") == "ItemFlowEnd" or response.get("@type") == "ItemDefinition" or response.get("@type") == "FeatureMembership" or response.get("@type") == "ActionUsage" or response.get("@type") == "FlowConnectionUsage":
             #if response.get('@id')=='234bc46f-9cd3-4409-8c62-e33e5e96217b':
             #    print(response.get('name'))
             #    print(response)
             if response.get("@type") == "ActionUsage":
                 clActions.append(response.get("name"))
                 clActionIds.append(response.get("elementId"))
             if response.get("@type") == "ItemDefinition":
                 #print('ItemDefinition')
                 #print(response)                 
                 clItemDefs.append(response.get("name"))
                 clItemDefIds.append(response.get("elementId"))
             if response.get("@type") == "FlowConnectionUsage":
                 clFlowIds.append(response.get("elementId"))
                 clFlowTargets.append(response.get("relatedElement"))
                 clFlowItems.append(response.get("itemFeature"))
             if response.get("@type") == "ItemFeature":
                 #print('ItemFeature')
                 #print(response)
                 clItemFeatureIds.append(response.get("elementId"))
                 clItemFeatureTypes.append(response.get("type"))
         
         #print(data)
         
         clActivitiesAndObjectFlows = []           
         
         
         for iFlow in range(len(clFlowIds)):
             vFlowTarget = clFlowTargets[iFlow]
            
             cFlowEnd1=vFlowTarget[0].get('@id')
             cFlowEnd2=vFlowTarget[1].get('@id')
             if clActionIds.count(cFlowEnd1) > 0:
                 cFlowEndActionName=clActions[clActionIds.index(cFlowEnd1)]
                 cFlowEndOtherId=vFlowTarget[1].get('@id')
             else:
                 cFlowEndActionName=clActions[clActionIds.index(cFlowEnd2)]
                 cFlowEndOtherId=vFlowTarget[0].get('@id')
                 
             print(cFlowEndActionName + ' - ' + cFlowEndOtherId)
             print(clFlowItems[iFlow])
             print('ItemFeature: ' + clFlowItems[iFlow].get('@id'))
             if clItemFeatureIds.count(clFlowItems[iFlow].get('@id'))>0:
                 cItemFeatureTypeId=clItemFeatureTypes[clItemFeatureIds.index(clFlowItems[iFlow].get('@id'))]
                 print (cItemFeatureTypeId)
                 if clItemDefIds.count(cItemFeatureTypeId[0].get('@id'))>0:
                     cItemDefinitionName = clItemDefs[clItemDefIds.index(cItemFeatureTypeId[0].get('@id'))]
                 else:
                     cItemDefinitionName = ''
                 print('ItemDef name: ' + cItemDefinitionName)
                 
             print('-----------')
     ## BEGIN TEMP Hard-code some data until this function is implemented
     ## When implementing the final version of the function, the data structure for the following two variables needs to be made more clean.
     ## The structure is still based on the initial idea of reading input from hand-written cards via OCR
     #clActivitiesAndObjectFlows = ['GetMoney:money:MonitorPayment', 'MonitorPayment:clearance:ProvideMusicTrack', 'ProvideMusicTrack:music_track:PlayMusicTrack', 'PlayMusicTrack:audio_signal:ProduceSound']
     clFunctionalGroups = ['MusicPlayer:PlayMusicTrack', 'Storage:ProvideMusicTrack', 'Accounting:MonitorPayment', 'IO_Customer:GetMoney:ProduceSound']
     ## END TEMP Hard-code
     return bSuccess, cErrorMessage, clActivitiesAndObjectFlows, clFunctionalGroups


def write_functional_architecture(cProjectID,cServerName,cSysMLString):
     bSuccess = False
     print(cProjectID.get())
     print(cServerName.get())
     print(cSysMLString)
     cErrorMsg = "write_functional_architecture is not implemented"
     return bSuccess, cErrorMsg

def render_transform_formula(cFormulaOutput):
     renderingWindow= Tk()
     renderingWindow.title("FAS Plugin")
     #renderingWindow.state('zoomed')
     ttk.Label(renderingWindow, text="FAS-as-a-formula").grid(column=0, row=0)
     scr = scrolledtext.ScrolledText(renderingWindow, width = 200, height = 40, font = ("Courier", 9))
     scr.grid(column = 0, pady = 10, padx = 10)
     scr.focus()
     scr.insert(tk.INSERT,cFormulaOutput)
     scr.configure(state ='disabled')
     renderingWindow.mainloop()

def fas_transform(cProjectID,cServerName):
     bSuccess, cErrorMsg, clActivitiesAndObjectFlows, clFunctionalGroups = read_activities_and_functional_groups(cProjectID,cServerName)
     if bSuccess == False:
         messagebox.showerror("FAS Plugin","Reading from the repository failed with the following error message: " + cErrorMsg)
     else:
         cSysMLString, cFormulaOutput = run_fas(clActivitiesAndObjectFlows, clFunctionalGroups)
         render_transform_formula(cFormulaOutput)
         bSuccess, cErrorMsg = write_functional_architecture(cProjectID,cServerName,cSysMLString)
         if bSuccess == False:
             messagebox.showerror("FAS Plugin","Writing to the repository failed with the following error message: " + cErrorMsg)
     
     messagebox.showwarning("FAS Plugin","fas_transform is missing functionality for tracing functional blocks to functional groups")


def processProjectSelection(listWindow,theCombo,cProjectID):
     selectedProject = theCombo.get()
     posOpeningParenthesis = selectedProject.find('(')
     posClosingParenthesis = selectedProject.find(')')
     cProjectID.set(selectedProject[(posOpeningParenthesis+1):posClosingParenthesis])
     listWindow.destroy()

    
def selectproject(cProjectID, cServerName):
     tdata = []
     cProjectID.set("")
     cProjectID.set("")
     try:
         response = requests.get(format_servername(cServerName.get()) + "/projects")
         data = response.json()
         for response in data:
             tdata.append(response.get("name") + " (" + response.get("@id") + ")" )
     except  requests.exceptions.ConnectionError:
         cProjectID.set("Cannot connect to server.")
     
     if len(tdata)>0:
         listWindow = Tk()
         listWindow.title("FAS Plugin - Project Selection")
         frm = ttk.Frame(listWindow)
         frm.grid(row=0, column=0, columnspan=4)
         ttk.Label(frm, text="Select project").grid(column=0, row=0)
         theCombo=ttk.Combobox(frm, values=tdata, width = 100)
         theCombo.grid(column=1, row=1)
         ttk.Button(frm, text="OK", command=partial(processProjectSelection,listWindow,theCombo,cProjectID)).grid(column=3, row=2)
         ttk.Button(frm, text="Cancel", command=listWindow.destroy).grid(column=2, row=2)

         listWindow.mainloop()   

         
def run_fas4sysml(cProjectUUID):
     mainWindow = Tk()
     mainWindow.title("FAS Plugin")
     frm = ttk.Frame(mainWindow)
     frm.grid(row=0, column=0, columnspan=3)

     ttk.Label(frm, text="FAS Plugin for SysML v2").grid(column=0, row=0)
     cProjectID = StringVar()
     cProjectID.set(cProjectUUID)
     cServerName = StringVar()
     cServerName .set('http://localhost:9000')
     ttk.Label(frm, text="").grid(column=0, row=1)
     ttk.Label(frm, text="Server").grid(column=0, row=2)
     ttk.Entry(frm, textvariable = cServerName, width = 50).grid(column=1, row=2)
     ttk.Label(frm, text="Project UUID").grid(column=0, row=3)
     ttk.Entry(frm, textvariable = cProjectID, width = 50).grid(column=1, row=3)
     ttk.Button(frm, text="Select", command=partial(selectproject,cProjectID,cServerName)).grid(column=2, row=3)
     ttk.Label(frm, text="").grid(column=0, row=4)
     ttk.Button(frm, text="Run FAS transformation", command=partial(fas_transform,cProjectID,cServerName)).grid(column=1, row=5)
     ttk.Button(frm, text="Quit", command=mainWindow.destroy).grid(column=2, row=5)
     mainWindow.mainloop()


def main():
     init_printing(use_unicode=False)

     cProjectID = ''
     if len (sys.argv)>1:
         cProjectID=sys.argv[1]
     run_fas4sysml(cProjectID)


if __name__ == "__main__":
     main()
