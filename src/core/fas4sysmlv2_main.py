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
#   This is the main py file of the FAS plugin for SysML v2.
#
#   When calling as a script, pass the project ID as an optional first parameter
#   and the host url for connecting to the repository as an optional second one.
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
import json
import tempfile

from sympy import *

import requests 

import platform
import os

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

#### THE FOLLOWING IS ONLY NEEDED IF WE WANT TO CONTINUE WRITING A NEW MODEL INSTEAD OF INCREMENTS FOR THE EXISTING MODEL
#### IF THIS STAYS NEEDED IN FUTURE, THEN A JOINT MODULE WITH fas_frontend SHOULD BE CREATED

def UpdateMatrixWithFlow(clDomainObjects,clActivityNamesSorted,mMatrixO, sLineToParse):
     sSourceObject,sFlow,sTargetObject = parseFlowLine(sLineToParse)
     clActivities = clActivityNamesSorted
     clDomainObjects = UpdateUniqueContentCellArray (clDomainObjects, sFlow)
     M = len(clActivities);
     mNewMatrixO = mMatrixO
     if len(mNewMatrixO)==0:
         mNewMatrixO = [['' for col in range(M)] for row in range(M)]
     for nInitIndex1 in range(M):
         for nInitIndex2  in range(M):
             if GetIndexOfStringInCellArray(clActivities,sSourceObject) == nInitIndex1 and GetIndexOfStringInCellArray(clActivities,sTargetObject) == nInitIndex2 :
                 if mNewMatrixO[nInitIndex1][nInitIndex2] == '':
                     mNewMatrixO[nInitIndex1][nInitIndex2] =  sFlow
                 else:
                     mNewMatrixO[nInitIndex1][nInitIndex2] =  mNewMatrixO[nInitIndex1][nInitIndex2] + ' + ' + sFlow  
    
     mMatrixO = mNewMatrixO;
     return clDomainObjects,mMatrixO 

     
def RenderFunctionalGroupsInSysML(clGroupName,clActivities, mMatrixG):
     cSysMLString=''
     cLF = '\n'
     N=len(mMatrixG)  
     if N>0:
         M=len(mMatrixG[0])
     else:
         M=0
         
     for n in range(N):
         cSysMLString= cSysMLString + '         package ' + clGroupName[n] + '{' + cLF
         for m in range (M):
             if mMatrixG[n][m] > 0:
                 cSysMLString = cSysMLString + '            import OverallUseCase::' + clActivities[m] + ';' + cLF
         
         cSysMLString= cSysMLString + '         }' + cLF

     
     return cSysMLString
     
def RenderActivityDefinitionsInSysML(O,clActivities):
     cSysMLString=''
     cLF = '\n'


     for nText in range(len(clActivities)):      
         clBufferOfNamesForUniqueness = [] # Remember all parameter names to be able to ensure uniqueness

         cSysMLString = cSysMLString + '         action ' + clActivities[nText] + ' {' + cLF
         for nIn in range(len(clActivities)):
             if O[nIn][nText] != '':
                 sTemp = O[nIn][nText]
                 sFlowString = sTemp.strip()
                 iNumOccurences = sFlowString.count('+')
                 for nParam in range(iNumOccurences  +1):
                     sCurrentFlowName = SubFlow(sFlowString,nParam)
                     sInput = sCurrentFlowName.lower()
                     iNumberForUniqueness=1
                     while clBufferOfNamesForUniqueness.count(sInput)>0:
                         if clBufferOfNamesForUniqueness.count(sInput + str(iNumberForUniqueness)) == 0:
                             sInput = sInput  + str(iNumberForUniqueness)
                         iNumberForUniqueness=iNumberForUniqueness+1
                     cSysMLString=cSysMLString + '            in ' + sInput + ';' + cLF
                     clBufferOfNamesForUniqueness.append(sInput)
              
          
     
         for nOut in range(len(clActivities)):
             if O[nText][nOut] != '':
                 sTemp = O[nText][nOut]
                 sFlowString = sTemp.strip()
                 iNumOccurences = sFlowString.count('+')
                 for nParam in range(iNumOccurences + 1):
                     sCurrentFlowName = SubFlow(sFlowString,nParam)
                     sOutput = sCurrentFlowName.lower() 
                     iNumberForUniqueness=1
                     while clBufferOfNamesForUniqueness.count(sOutput)>0:
                         if clBufferOfNamesForUniqueness.count(sOutput + str(iNumberForUniqueness)) == 0:
                             sOutput = sOutput  + str(iNumberForUniqueness)
                         iNumberForUniqueness=iNumberForUniqueness+1
                     cSysMLString = cSysMLString + '            out ' + sOutput + ';' + cLF
                     clBufferOfNamesForUniqueness.append(sOutput) 

         cSysMLString = cSysMLString + '         }' + cLF
    
     return cSysMLString


def RenderFlowsAndItemDefsInSysML(O,clActivities):
     cSysMLString=''
     cItemString='' 
     cLF = '\n'
     clActionNames = clActivities

     
     cSysMLString = cSysMLString + '      action def OverallUseCase {' + cLF
    
     cSysMLString = cSysMLString + RenderActivityDefinitionsInSysML(O,clActivities)
    
     clBufferOfAllUsedItemDefs = [] #Remember what was already defined to avoid duplications
     for n1 in range(len(clActivities)): 
         for n2 in range(len(clActivities)):
             if O[n1][n2] != '':
                 sFlowString=(O[n1][n2]).strip()
                 for nParam in range(sFlowString.count('+')+1):
                     sCurrentFlowName = SubFlow(sFlowString,nParam)
                     sResult = sCurrentFlowName.lower() 
                     sInput = sCurrentFlowName.lower() 

                     cSysMLString = cSysMLString + '         flow of ' + sCurrentFlowName + ' from ' + clActionNames[n1] + '.' + sResult + ' to '  + clActionNames[n2] + '.' + sInput + ';' + cLF

                     if clBufferOfAllUsedItemDefs.count(sCurrentFlowName) < 1:
                         clBufferOfAllUsedItemDefs.append(sCurrentFlowName)
                         cItemString = cItemString + '   item def ' + sCurrentFlowName + ';' + '\n'
              

     cSysMLString = cSysMLString + '      }' + cLF
    
     return cSysMLString, cItemString, clActionNames


def ProcessFasCards(clActivitiesAndObjectFlows, clFunctionalGroups, clActivityNamesSorted): 
     ### Process Activities and Object Flows
     cSysMLString=''
     cLF = '\n'
     clLinesToParse =  clActivitiesAndObjectFlows
     clDomainObjects = []
     clActivities = clActivityNamesSorted
     mMatrixO = []
  
     for nIndex in range(len(clLinesToParse)):
        sLineToParse = clLinesToParse[nIndex]
        clDomainObjects,mMatrixO = UpdateMatrixWithFlow(clDomainObjects,clActivities,mMatrixO, sLineToParse)
    
     ### Process Functional Groupings
     clLinesToParse =  clFunctionalGroups  
     N=len(clLinesToParse)
     M=len(mMatrixO)
     mMatrixG = [[0 for col in range(M)] for row in range(N)]

     clGroupName = ['' for col in range(N)]
     for n in range (N):
        sLineToParse = clLinesToParse[n];
        sGroupName, clGroup = parseGroupLine(sLineToParse)
        clGroupName[n]=sGroupName;
        for m in range(M):
          if GetIndexOfStringInCellArray(clGroup,clActivities[m]) > -1:
             mMatrixG[n][m] = 1;
          
        
     
     sFlows, sItemDefs, clActionNames = RenderFlowsAndItemDefsInSysML(mMatrixO, clActivities)
     cSysMLString=cSysMLString + sItemDefs + cLF  + '   package UseCaseActivities{' + cLF
     cSysMLString = cSysMLString + sFlows
     cSysMLString = cSysMLString + '      package FunctionalGroups{' + cLF
     cSysMLString = cSysMLString + RenderFunctionalGroupsInSysML(clGroupName ,clActionNames, mMatrixG)
     cSysMLString=cSysMLString + '      }' + cLF
     cSysMLString=cSysMLString + '   }' + cLF
     return cSysMLString 


#### END TEMP



def SymbolicUpdateMatrixWithFlow(clDomainObjects,clActivities,mMatrixO, sLineToParse):
     sSourceObject,sFlow,sTargetObject = parseFlowLine(sLineToParse)
     clDomainObjects = UpdateUniqueContentCellArray (clDomainObjects, sFlow)
     M = len(clActivities);
     mNewMatrixO = mMatrixO
     
     if mNewMatrixO.shape[0] == 0:
         mNewMatrixO = Matrix([[0 for col in range(M)] for row in range(M)])
     for nInitIndex1 in range(M):
         for nInitIndex2  in range(M):
             if GetIndexOfStringInCellArray(clActivities,sSourceObject) == nInitIndex1 and GetIndexOfStringInCellArray(clActivities,sTargetObject) == nInitIndex2 :
                 mTemp = [[0 for col in range(M)] for row in range(M)]
                 sFlowSymbolic = symbols(sFlow)
                 mTemp[nInitIndex1][nInitIndex2] = sFlowSymbolic
                 mNewMatrixO = mNewMatrixO + Matrix(mTemp)

    
     return clDomainObjects,clActivities,mNewMatrixO 
 
 
def RenderFunctionalArchitecture(F,clFunctionalBlockNames):
     cItemDefString = ''
     cSysMLstring = '   part functionalSystem{' + '\n'

     cDependencySpecification = ''
     clSourcePortNames = [['' for col in range(F.shape[0])] for row in range(F.shape[0])]
     clTargetPortNames = [['' for col in range(F.shape[0])] for row in range(F.shape[0])]
     for nBlock in range(F.shape[0]):
         cCurrentBlock = clFunctionalBlockNames[nBlock]
         cSysMLstring = cSysMLstring + '      part ' + cCurrentBlock + '{' + '\n'
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
                         cSysMLstring = cSysMLstring + '         port ' + cPortName + ';' + '\n'
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
                         cSysMLstring = cSysMLstring + '         port ' + cPortName + ';' + '\n'
                         clPortCell[nPort]=cPortName
               
                         clTargetPortNames[nPortIn][nBlock]=clPortCell
                         
                         
         cSysMLstring = cSysMLstring + '      }' + '\n'
   
    
    ## Connect the blocks with flows
     cItemString = ''
     clBufferOfAllUsedItemDefs = [] #Remember what was already defined to avoid duplications

     for nBlock1 in range(F.shape[0]):
         for nBlock2 in range(F.shape[0]):
             cFlow=F[nBlock1,nBlock2]
             if nBlock1 != nBlock2 and cFlow != 0: 
                 sFlowName = str(cFlow)
                 clSourcePorts = clSourcePortNames[nBlock1][nBlock2]
                 clTargetPorts = clTargetPortNames[nBlock1][nBlock2]
                 for nPort in range(len(clSourcePorts)):
                     sCurrentFlowName = SubFlow(sFlowName,nPort)
                     cSysMLstring = cSysMLstring + '      flow of ' + sCurrentFlowName + ' from ' + clFunctionalBlockNames[nBlock1] + '.' + clSourcePorts[nPort] + ' to ' + clFunctionalBlockNames[nBlock2] + '.' + clTargetPorts[nPort] + ';' + '\n'

                     if clBufferOfAllUsedItemDefs.count(sCurrentFlowName) < 1:
                         clBufferOfAllUsedItemDefs.append(sCurrentFlowName)
                         cItemDefString = cItemDefString + '   item def ' + sCurrentFlowName + ';' + '\n'
           
    
    ## Trace Functional Blocks to Functional Groups
     for nBlock in range(F.shape[0]):
         sCurrentName = clFunctionalBlockNames[nBlock]
         cDependencySpecification = cDependencySpecification + '   dependency from functionalSystem::' + sCurrentName + ' to UseCaseActivities::FunctionalGroups::' + sCurrentName + ';' + '\n'
    
      
     cSysMLstring = cSysMLstring + '   }' + '\n' + cItemString 
   
     return  cSysMLstring, cDependencySpecification, cItemDefString



def run_fas(clActivitiesAndObjectFlows, clFunctionalGroups, clActivityNamesSorted):

     cSysMLString=''
     cFormulaOutput = ''
    
     ### Process Activities and Object Flows
     clLinesToParse =  clActivitiesAndObjectFlows
     clDomainObjects = []
     clActivities = clActivityNamesSorted
     mSymbolicMatrixO = Matrix([])
  
     for nIndex in range(len(clLinesToParse)):
         sLineToParse = clLinesToParse[nIndex]
         clDomainObjects,clActivities,mSymbolicMatrixO = SymbolicUpdateMatrixWithFlow(clDomainObjects,clActivities,mSymbolicMatrixO, sLineToParse)
     
     
     cFormulaOutput = cFormulaOutput  + 'O = (symbolic ' + str(mSymbolicMatrixO.shape[0]) + 'x' + str(mSymbolicMatrixO.shape[1]) + ' matrix)'
     cFormulaOutput = cFormulaOutput  + '\n' 
     cFormulaOutput = cFormulaOutput  + '\n' +pretty(mSymbolicMatrixO, num_columns=195)
     cFormulaOutput = cFormulaOutput  + '\n' 
     
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
          
   
     cFormulaOutput = cFormulaOutput  + '\n' + 'G = (symbolic ' + str(mSymbolicMatrixG.shape[0]) + 'x' + str(mSymbolicMatrixG.shape[1]) + ' matrix)'
     cFormulaOutput = cFormulaOutput  + '\n' 
     cFormulaOutput = cFormulaOutput  + '\n' +pretty(mSymbolicMatrixG, num_columns=195)
     cFormulaOutput = cFormulaOutput  + '\n'     
    
     
     ### Compute the functional architecture via FAS-as-a-formula
     ### F = G*O*G.T;
     mSymbolicMatrixF=mSymbolicMatrixG*mSymbolicMatrixO*mSymbolicMatrixG.T;
     
     cFormulaOutput = cFormulaOutput  + '\n' + '---------------------------------'
     cFormulaOutput = cFormulaOutput  + '\n' 'Applying FAS-as-a-formula:'
     cFormulaOutput = cFormulaOutput  + '\n' ''
     # Explanation of "FAS-as-a-formula": https://github.com/GfSE/fas4sysmlv2/blob/main/doc/tech-docs/fas/FAS-as-a-formula-2022.odt"
     GOG,T,F = symbols('GOG, T, F')
     #This is a work-around to print the formula F=G*O*G**T in nice formatting:
     cFormulaOutput = cFormulaOutput  + '\n' + pretty(Eq(F, GOG**T))
     cFormulaOutput = cFormulaOutput  + '\n' 
     cFormulaOutput = cFormulaOutput  + '\n'  + '---------------------------------'
     cFormulaOutput = cFormulaOutput  + '\n' 
     
     cFormulaOutput = cFormulaOutput  + '\n' + 'F = (symbolic ' + str(mSymbolicMatrixF.shape[0]) + 'x' + str(mSymbolicMatrixF.shape[1]) + ' matrix)'
     cFormulaOutput = cFormulaOutput  + '\n' 
     cFormulaOutput = cFormulaOutput  + '\n' +pretty(mSymbolicMatrixF, num_columns=195)
     cFormulaOutput = cFormulaOutput  + '\n'     
     
     ### FAS method says that names of functional blocks are equal to names of functional groups
     clFunctionalBlockNames = clGroupName
     
     ### Print the functional architecture
     cSysMLString, cDependencySpecification, cItemDefString = RenderFunctionalArchitecture(mSymbolicMatrixF,clFunctionalBlockNames)
    
     return cSysMLString, cFormulaOutput, cDependencySpecification, cItemDefString    
  

def format_servername(cName):
     if len(cName)>0:
         if cName[len(cName)-1] == '/':
            cName = cName[0:(len(cName)-1)]
         
         if cName.find('http') == -1:
            cName = 'http://' + cName
     
     return cName
  
def run_query_for_elementtyp(cElementType, cServerName, cProjectID):
    qresponse_json=json.dumps('')
    qinput = {
      '@type':'Query',
      'select': ['name','@id','@type','owner'],
      'where': {
        '@type': 'CompositeConstraint',
        'operator': 'and',
        'constraint': [
            {
                '@type': 'PrimitiveConstraint',
                'inverse': False,
                'operator': '=',
                'property': '@type',
                'value': cElementType
            }
        ]
      }
    }

    payload = json.dumps(qinput)
    qurl = f"{cServerName}/projects/{cProjectID}/query-results" 
    qresponse = requests.post(qurl, json=qinput)
    if qresponse.status_code == 200:
        qresponse_json = qresponse.json()

    return qresponse_json
  
def read_activities_and_functional_groups(strProjectID,strServerName):

     clActivitiesAndObjectFlows = []           
     clFunctionalGroups = []

     bSuccess = True
     cErrorMessage = ''
     cProjectID=strProjectID.get()
     cServerName=format_servername(strServerName.get())
     
     print('Reading Use Case Activities and Functional Groups from project ' + cProjectID + ' on server ' + cServerName + ' ...')
    
     try:
         response = requests.get(cServerName + "/projects/" + cProjectID)
     except  requests.exceptions.ConnectionError:
         bSuccess = false
         cErrorMessage = 'Error: Could not connect to server'
         print(cErrorMessage)

         
     if bSuccess and response.status_code!=200:
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
     clEndFeatureMembershipIds=[]
     clEndFeatureMembershipTargets=[]
     clFeatureMembershipIds=[]
     clFeatureMembershipOwnedRelatedElements = []
     clFeatureMembershipTargets=[]
     clFlowIds=[]
     clFlowTargets=[]
     clFlowItems=[]
     clFlowOwnedRelationships = []
     clItemsFlowEndIds=[]
     clItemFlowEndOwnedRelationships = []
     clItemFeatureIds=[]
     clItemFeatureTypes=[]
     clItemDefs=[]
     clItemDefIds=[]
     clPackageIds=[]
     clPackageNames=[]
     clPackageImportedMemberships=[]
     clReferenceSubSettingIds=[]
     clReferenceSubSettingReferencedFeatures=[]

     clElementTypes = ['ReferenceSubsetting','EndFeatureMembership','FeatureMembership','ItemFlowEnd','ActionUsage','ItemDefinition','FlowConnectionUsage','ItemFeature','Package']
     
     if bSuccess:
     
         for cElementType in clElementTypes:
             data = run_query_for_elementtyp(cElementType, cServerName, cProjectID)
             for currentRecord in data:
                 sIdToGet=currentRecord.get('@id')
                 qresult = requests.get(cServerName + "/projects/" + cProjectID + "/commits/"+sHeadCommit+"/elements/" + sIdToGet)
                 response = qresult.json()


                 if response.get("@type") == "ReferenceSubsetting": #As ownedRelationship of target of FeatureEndMembership
                     clReferenceSubSettingReferencedFeatures.append(response.get("referencedFeature"))
                     clReferenceSubSettingIds.append(response.get("elementId"))
                 if response.get("@type") == "EndFeatureMembership":
                     clEndFeatureMembershipTargets.append(response.get("target"))
                     clEndFeatureMembershipIds.append(response.get("elementId"))
                 if response.get("@type") == "FeatureMembership":
                     clFeatureMembershipTargets.append(response.get("target"))
                     clFeatureMembershipIds.append(response.get("elementId"))
                     clFeatureMembershipOwnedRelatedElements.append(response.get("ownedRelatedElement"))
                 if response.get("@type") == "ItemFlowEnd":  #As target of EndFeatureMembership
                     clItemFlowEndOwnedRelationships.append(response.get("ownedRelationship"))
                     clItemsFlowEndIds.append(response.get("elementId"))
                 if response.get("@type") == "ActionUsage":
                     clActions.append(response.get("name"))
                     clActionIds.append(response.get("elementId"))
                 if response.get("@type") == "ItemDefinition":
                     clItemDefs.append(response.get("name"))
                     clItemDefIds.append(response.get("elementId"))
                 if response.get("@type") == "FlowConnectionUsage":
                     clFlowIds.append(response.get("elementId"))
                     clFlowTargets.append(response.get("relatedElement"))
                     clFlowItems.append(response.get("itemFeature"))
                     clFlowOwnedRelationships.append(response.get("ownedRelationship"))
                 if response.get("@type") == "ItemFeature":
                     clItemFeatureIds.append(response.get("elementId"))
                     clItemFeatureTypes.append(response.get("type"))
                 if response.get("@type") == "Package":
                     clPackageIds.append(response.get("elementId"))
                     clPackageImportedMemberships.append(response.get("importedMembership"))
                     clPackageNames.append(response.get("name"))
         
                 

         #Process Use Case Activities and Object Flows         
         
         
         for iFlow in range(len(clFlowIds)):
             
             vFlowOwnedRelationship = clFlowOwnedRelationships[iFlow]
             if len(vFlowOwnedRelationship)==3:
                 cFlowOwnedRelationship1=vFlowOwnedRelationship[0].get('@id')
                 cFlowOwnedRelationship2=vFlowOwnedRelationship[1].get('@id')
                 cFlowOwnedRelationship3=vFlowOwnedRelationship[2].get('@id')
                 clTargetIds = []
                 cFeatureMembershipTarget='undefined'
                 if clEndFeatureMembershipIds.count(cFlowOwnedRelationship1) > 0: 
                     clTargetIds.append(clEndFeatureMembershipTargets[clEndFeatureMembershipIds.index(cFlowOwnedRelationship1)][0].get('@id'))
                 if clEndFeatureMembershipIds.count(cFlowOwnedRelationship2) > 0:
                     clTargetIds.append(clEndFeatureMembershipTargets[clEndFeatureMembershipIds.index(cFlowOwnedRelationship2)][0].get('@id'))
                 if clEndFeatureMembershipIds.count(cFlowOwnedRelationship3) > 0:
                     clTargetIds.append(clEndFeatureMembershipTargets[clEndFeatureMembershipIds.index(cFlowOwnedRelationship3)][0].get('@id'))
                     
                 if clFeatureMembershipIds.count(cFlowOwnedRelationship1) > 0: 
                     cFeatureMembershipTarget=clFeatureMembershipTargets[clFeatureMembershipIds.index(cFlowOwnedRelationship1)][0].get('@id')
                 if clFeatureMembershipIds.count(cFlowOwnedRelationship2) > 0:
                     cFeatureMembershipTarget=clFeatureMembershipTargets[clFeatureMembershipIds.index(cFlowOwnedRelationship2)][0].get('@id')
                 if clFeatureMembershipIds.count(cFlowOwnedRelationship3) > 0:
                     cFeatureMembershipTarget=clFeatureMembershipTargets[clFeatureMembershipIds.index(cFlowOwnedRelationship3)][0].get('@id')
                 
                 clActionPair=[]
                 for iFlowPartner in range (len(clTargetIds)):
                     cTargetId = clTargetIds[iFlowPartner]
                     if  clItemsFlowEndIds.count(cTargetId) > 0:
                         cOwnedRelationship=clItemFlowEndOwnedRelationships[ clItemsFlowEndIds.index(cTargetId)][0].get('@id')
                         if clReferenceSubSettingIds.count(cOwnedRelationship) > 0:
                             cReferencedFeature = clReferenceSubSettingReferencedFeatures[clReferenceSubSettingIds.index(cOwnedRelationship)].get('@id')
                             if clActionIds.count(cReferencedFeature) > 0:
                                 cAction = clActions[clActionIds.index(cReferencedFeature)]
                                 clActionPair.append(cAction)
                                 
                                 
                 if clItemFeatureIds.count(cFeatureMembershipTarget)>0:
                     cItemFeatureTypeId=clItemFeatureTypes[clItemFeatureIds.index(cFeatureMembershipTarget)]
                     #print (cItemFeatureTypeId)
                     if clItemDefIds.count(cItemFeatureTypeId[0].get('@id'))>0:
                         cItemDefinitionName = clItemDefs[clItemDefIds.index(cItemFeatureTypeId[0].get('@id'))]
                     else:
                         cItemDefinitionName = ''

                 if len(clActionPair) == 2:
                    clActivitiesAndObjectFlows.append(clActionPair[0] + ':' + cItemDefinitionName + ':' + clActionPair[1])
         
         #Process  Functional Groups
         for iPackage in range(len(clPackageIds)):
             cPackageName = clPackageNames[iPackage]
             cCurrentFunctionalGroup = cPackageName
             vFeatureMemberships=clPackageImportedMemberships[iPackage]
             for iUseCaseActivityInGroupCounter in range(len(vFeatureMemberships)):
                cFeatureMembershipForUseCaseActivity = vFeatureMemberships[iUseCaseActivityInGroupCounter].get('@id')
                if  clFeatureMembershipIds.count(cFeatureMembershipForUseCaseActivity) > 0:
                    cFeatureMembershipOwnedRelatedElement = clFeatureMembershipOwnedRelatedElements[clFeatureMembershipIds.index(cFeatureMembershipForUseCaseActivity)][0].get('@id')
                    if clActionIds.count(cFeatureMembershipOwnedRelatedElement) > 0:
                         cAction = clActions[clActionIds.index(cFeatureMembershipOwnedRelatedElement)]
                         cCurrentFunctionalGroup = cCurrentFunctionalGroup + ':' + cAction
             
             if cCurrentFunctionalGroup.count(':') > 0:
                 clFunctionalGroups.append(cCurrentFunctionalGroup)       

         
     clActivityNamesSorted = sorted(clActions)    
     return bSuccess, cErrorMessage, clActivitiesAndObjectFlows, clFunctionalGroups, clActivityNamesSorted


def DumpJupyterNotebook(cWorkingFolderAndOutputFile, cWorkingFolderAndInputFile, cSysMLString):
     cNotebookFile = cWorkingFolderAndOutputFile
     FID1=open(cWorkingFolderAndInputFile,'r');
     FID2=open(cNotebookFile,'w');
     for tline in FID1:
         num = tline.find('"<Paste SysMLv2 code here>"')
         if num > -1:
             cCommaBlankAndQuotationMark=',' + '\r\n' + '    "'
             cCodedSysML='    "' + cSysMLString.replace('\n','\\n"' + cCommaBlankAndQuotationMark)    
             #Remove final comma, blank and quotation mark 
             cCodedSysML = cCodedSysML[:(len(cCodedSysML)-len(cCommaBlankAndQuotationMark))]
             FID2.write(cCodedSysML )
         else:
             FID2.write(tline)
     FID1.close()
     FID2.close()
     return cNotebookFile 


def write_functional_architecture(cProjectID,cServerName,cSysMLString,cOptionalInputModel,cOptionalDependencySpecification, cItemDefString):
     targetProjectID = ''

     bSuccess = False
     cErrorMsg = ''
     cSysMLString = 'package FunctionalModel {\n' + cOptionalInputModel + cSysMLString + cOptionalDependencySpecification + '}\n'
     print('')
     print('Here is the generated functional architecture: ')
     print(cSysMLString)
     print('Writing it to the server ... ')

     bNewProject = true # if set to false then the commit will be made to the project from which the use case activities were read
     if bNewProject:
         cWorkingFolder=tempfile.mkdtemp()
         #print(cWorkingFolder)
         cNotebookFile = os.path.join(cWorkingFolder,'temp_fas_input_writer.ipynb')
         FID =open(cNotebookFile ,'w');
         FID.write('{\n "cells": [\n  {\n   "cell_type": "markdown",\n   "id": "237f75ac",\n   "metadata": {},\n   "source": [\n    "FAS for SysMLv2: FAS Input to Repository Writer\\n",\n    "=="\n   ]\n  },\n  {\n   "cell_type": "code",\n   "execution_count": null,\n   "id": "f4fe084d",\n   "metadata": {},\n   "outputs": [],\n   "source": [\n    "<Paste SysMLv2 code here>"\n   ]\n  },\n  {\n   "cell_type": "code",\n   "execution_count": null,\n   "id": "7e04e6fc",\n   "metadata": {},\n   "outputs": [],\n   "source": [\n    "%publish FunctionalModel"\n   ]\n  }\n ],\n "metadata": {\n  "kernelspec": {\n   "display_name": "SysML",\n   "language": "sysml",\n   "name": "sysml"\n  },\n  "language_info": {\n   "codemirror_mode": "sysml",\n   "file_extension": ".sysml",\n   "mimetype": "text/x-sysml",\n   "name": "SysML",\n   "pygments_lexer": "java",\n   "version": "1.0.0"\n  }\n },\n "nbformat": 4,\n "nbformat_minor": 5\n}\n')
         FID.close()

         cOutputFile = os.path.join(cWorkingFolder, 'temp_output.ipynb')
         cResultFile = os.path.join(cWorkingFolder, 'temp_result.ipynb')

         DumpJupyterNotebook(cOutputFile, cNotebookFile, cSysMLString)
         if platform.system()!='Windows':
             cSilencer='2>/dev/null'
             os.system('/bin/bash -i -c "jupyter nbconvert --to notebook --execute ' + cOutputFile + ' --stdout >' + cResultFile + ' ' + cSilencer+'"')
         else:
             cSilencer='>nul 2>&1';
             os.system('jupyter nbconvert --to notebook --execute ' + cOutputFile + ' --output=' + cResultFile + ' ' + cSilencer)

         status = ''
         FID1=open(cResultFile ,'r');
         bStdout = False
         bData = False
         bResultExpected = False
         for tline in FID1:
             if bResultExpected:
                 status = 'STATUS: ' + tline.replace('\\n','').replace('\\r','').strip()
                 break
             if tline.find('"name": "stdout",')>-1:
                 bStdout = True
             if tline.find('"data": {')>-1 and bStdout:
                 bData = True
             if tline.find('"text/plain": [')>-1 and bData:
                 bResultExpected = True
         FID1.close()
         
         os.remove(cResultFile)
         os.remove(cOutputFile)
         os.remove(cNotebookFile)
         os.rmdir(cWorkingFolder)
  
         if status.find('Saved to Project') < 0:
                cErrorMsg =  'Error in commit to target project: ' + status
                print(cErrorMsg)
                bSuccess= false
         else:
                posOpeningParenthesis = status.find('(')
                posClosingParenthesis = status.find(')')
                targetProjectID = status[(posOpeningParenthesis+1):posClosingParenthesis]
                bSuccess= True
     else:
         cErrorMsg = "write_functional_architecture: code is not yet implemented for writing to existing projects"
         messagebox.showwarning("FAS Plugin","fas_transform is missing functionality for tracing functional blocks to functional groups and for re-using the original item defs in the database, instead of composing new ones")
         print(cErrorMsg)
     
     return bSuccess, cErrorMsg, targetProjectID


def render_transform_result(cFormulaOutput, cSysMLString, bSuccess, cTargetProject, cItemDefString):
     cSysMLString = cSysMLString + cItemDefString
     renderingWindow= Tk()
     renderingWindow.title("FAS Plugin")
     #renderingWindow.state('zoomed')
     ttk.Label(renderingWindow, text="FAS-as-a-formula application and result").grid(column=0, row=0)
     scr = scrolledtext.ScrolledText(renderingWindow, width = 200, height = 40, font = ("Courier", 9))
     scr.grid(column = 0, pady = 10, padx = 10)
     scr.focus()
     cStatusString = ''
     if bSuccess:
         cSuccessString = 'Wrote the model to project ID ' + cTargetProject
         print(cSuccessString)
         cStatusString = '\n================================================\nWriting the model to the repository\n================================================\n\n'
         cStatusString = cStatusString + cSuccessString
     scr.insert(tk.INSERT, '================================================\nApplying FAS-as-a-formula to the model\n================================================\n\n' + cFormulaOutput + '\n\n\n================================================\nResulting functional architecture\n================================================\n\n' + cSysMLString + cStatusString)
                           
     scr.configure(state ='disabled')
     renderingWindow.mainloop()

def fas_transform(cProjectID,cServerName):
     bSuccess, cErrorMsg, clActivitiesAndObjectFlows, clFunctionalGroups, clActivityNamesSorted = read_activities_and_functional_groups(cProjectID,cServerName)
     if bSuccess == False:
         messagebox.showerror("FAS Plugin","Reading from the repository failed with the following error message: " + cErrorMsg)
     else:
         print('Transforming to functional architecture via FAS-as-a-formula ...')
         cSysMLString, cFormulaOutput,cOptionalDependencySpecification, cItemDefString = run_fas(clActivitiesAndObjectFlows, clFunctionalGroups, clActivityNamesSorted)
         cOptionalInputModel=ProcessFasCards(clActivitiesAndObjectFlows, clFunctionalGroups, clActivityNamesSorted )
         bSuccess, cErrorMsg, cTargetProject = write_functional_architecture(cProjectID,cServerName,cSysMLString,cOptionalInputModel,cOptionalDependencySpecification, cItemDefString)
         render_transform_result(cFormulaOutput, cSysMLString, bSuccess, cTargetProject, cItemDefString)
         if bSuccess == False:
             messagebox.showerror("FAS Plugin","Writing to the repository failed with the following error message: " + cErrorMsg)
         else:    
             print("Writing to the repository succeeded.") ##In that case the GUI representation of the success message will be generated elsewhere
     


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

         
def run_fas4sysml(cProjectUUID, cHost):
     mainWindow = Tk()
     mainWindow.title("FAS Plugin")
     frm = ttk.Frame(mainWindow)
     frm.grid(row=0, column=0, columnspan=3)

     ttk.Label(frm, text="FAS Plugin for SysML v2").grid(column=0, row=0)
     cProjectID = StringVar()
     cProjectID.set(cProjectUUID)
     cServerName = StringVar()
     cServerName.set(cHost)
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
     cHost = 'http://localhost:9000'
     if len (sys.argv)>1:
         cProjectID=sys.argv[1]
     if len (sys.argv)>2:
         cHost=sys.argv[2]
     run_fas4sysml(cProjectID,cHost)


if __name__ == "__main__":
     main()
