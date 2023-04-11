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


# This python code has been directly translated from GNU Octave ".m" files
# The input comes via a file written from OpenOffice, with graphical information about the use case activities and their flows.


import sys


def RenderFunctionalGroupsInSysML(clGroupName,clActivities, mMatrixG):
     cSysMLString=''
     cLF = '\r\n'
     N=len(mMatrixG)  
     if N>0:
         M=len(mMatrixG[0])
     else:
         M=0
         
     for n in range(N):
         cSysMLString= cSysMLString + '         package ' + clGroupName[n] + '{' + cLF
         for m in range (M):
             if mMatrixG[n][m] > 0:
                 cSysMLString = cSysMLString + '            import ' + clActivities[m] + ';' + cLF
         
         cSysMLString= cSysMLString + '         }' + cLF

     
     return cSysMLString

def  ReadPositions(FID,numpos,iLineIndex):
      
     vPositionsXY=[0 for col in range(numpos)]
     n= 1
     iLineIndexNew = iLineIndex 
     while n<=numpos:
         sLine = FID[iLineIndexNew]
         iLineIndexNew = iLineIndexNew + 1
         if len(sLine.strip()) == 0:
             n=n-1
         else:  
             vPositionsXY[n-1] = float(sLine.strip())
             if n>2:
                 vPositionsXY[n-1] = vPositionsXY[n-1] + vPositionsXY[n-3]
         n=n+1;
     
     return vPositionsXY, iLineIndexNew
      
def Readname(FID,iLineIndex):
     sName = ''
     iLineIndexNew = iLineIndex
     while len(sName)==0 and iLineIndexNew < len(FID):
         sName=''
         sLine = FID[iLineIndexNew]
         iLineIndexNew = iLineIndexNew + 1
         sName = sLine.strip()
 
     return sName, iLineIndexNew        
def  My_GrowCellArray(clOld, newEntry):
     clNew = ['' for col in range((len(clOld)+1))]
     for nCopy in range(len(clOld)):
         clNew[nCopy]=clOld[nCopy]
     clNew[len(clNew)-1]=newEntry;
     return clNew      


def ParseopenOfficeExportFile(cFileName):
     FID1_ID = open(cFileName,'r')
     clGroupNames=[]
     clGroupPositionVectors=[]
     clActivityNames=[]
     clActivityPositionVectors=[]
     clConnectorNames=[]
     clConnectorPositionVectors=[]
     FID1 = FID1_ID.readlines()
     iLineIndex = 0
     while iLineIndex < len(FID1):
         sLine = FID1[iLineIndex]
         sLine=sLine.strip()
         iLineIndex = iLineIndex + 1
         if sLine == 'Group':
             sName, iLineIndex = Readname(FID1,iLineIndex)
             vPositionsXY, iLineIndex = ReadPositions(FID1,4,iLineIndex)
             clGroupNames =  My_GrowCellArray(clGroupNames, sName)
             clGroupPositionVectors =  My_GrowCellArray(clGroupPositionVectors, vPositionsXY)            
         elif sLine=='Element':
             sName, iLineIndex = Readname(FID1,iLineIndex)
             vPositionsXY, iLineIndex = ReadPositions(FID1,4,iLineIndex)
             clActivityNames =  My_GrowCellArray(clActivityNames, sName)
             clActivityPositionVectors =  My_GrowCellArray(clActivityPositionVectors, vPositionsXY)
         elif sLine=='Connector':
             vStartPositionXY, iLineIndex = ReadPositions(FID1,2,iLineIndex)
             vEndPositionXY, iLineIndex = ReadPositions(FID1,2, iLineIndex)
             sName, iLineIndex = Readname(FID1, iLineIndex)
             vPositionsXY, iLineIndex = ReadPositions(FID1,4, iLineIndex)
             clConnectorNames =  My_GrowCellArray(clConnectorNames, sName)
             clConnectorPositionVectors =  My_GrowCellArray(clConnectorPositionVectors, [vStartPositionXY[0], vStartPositionXY[1], vEndPositionXY[0], vEndPositionXY[1]]);
         else: 
             sLine = FID1[iLineIndex]
             iLineIndex = iLineIndex + 1
         
      
     FID1_ID.close()
     return clGroupNames, clGroupPositionVectors, clActivityNames, clActivityPositionVectors,clConnectorNames,clConnectorPositionVectors


def  CreateFunctionalGroups(clActivityNames, clActivityPositionVectors, clGroupNames,  clGroupPositionVectors):
     clFunctionalGroups = []
     for nGroup in range(len(clGroupPositionVectors)):
         vGrp = clGroupPositionVectors[nGroup]
         cGroupingString = clGroupNames[nGroup]
         for nActivity  in  range (len(clActivityPositionVectors)):
             vAct = clActivityPositionVectors[nActivity]
             if vAct[0] > vGrp[0] and vAct[1]> vGrp[1] and vAct[2] < vGrp[2] and vAct[3]<vGrp[3]:
                 cGroupingString = cGroupingString + ':' + clActivityNames[nActivity]
           
         
         clFunctionalGroups = My_GrowCellArray(clFunctionalGroups, cGroupingString)
       
     return clFunctionalGroups 
 
def isConnected (vConnectorXY, vActivityPositions, rTolerancePixels):
     bret = False;
     if (vConnectorXY[0] > (vActivityPositions[0] - rTolerancePixels)) and (vConnectorXY[0] < (vActivityPositions[2] + rTolerancePixels)):
         #Top line of activity rectangle
         if vConnectorXY[1] > (vActivityPositions[1] - rTolerancePixels) and vConnectorXY[1] < (vActivityPositions[1] + rTolerancePixels):
             bret = True
         #Bottom line of activity rectangle
         if vConnectorXY[1] > (vActivityPositions[3] - rTolerancePixels) and vConnectorXY[1] < (vActivityPositions[3] + rTolerancePixels):
             bret = True;
     if vConnectorXY[1] > (vActivityPositions[1] - rTolerancePixels) and vConnectorXY[1] < (vActivityPositions[3] + rTolerancePixels):
         # Left line of activity rectangle
         if vConnectorXY[0] > (vActivityPositions[0] - rTolerancePixels) and vConnectorXY[0] < (vActivityPositions[0] + rTolerancePixels):
             bret = True;
         # Right line of activity rectangle
         if vConnectorXY[0] > (vActivityPositions[2] - rTolerancePixels) and vConnectorXY[0] < (vActivityPositions[2] + rTolerancePixels):
             bret = True;
        
     
     return bret

def CreateActivitiesAndObjectFlows(clActivityNames, clActivityPositionVectors,clConnectorNames,clConnectorPositionVectors,rTolerancePixels):
     clActivitiesAndObjectFlows = []
     for nActivity in range(len(clActivityPositionVectors)):
         vActPositions = clActivityPositionVectors[nActivity]
         for nConnector in range(len(clConnectorPositionVectors)):
             vConnPositions = clConnectorPositionVectors[nConnector]
             if isConnected ([vConnPositions[0],vConnPositions[1]], vActPositions, rTolerancePixels):
                 for nActivity2 in range(len(clActivityPositionVectors)):
                     if isConnected ([vConnPositions[2],vConnPositions[3]], clActivityPositionVectors[nActivity2], rTolerancePixels):
                         clActivitiesAndObjectFlows = My_GrowCellArray(clActivitiesAndObjectFlows,clActivityNames[nActivity] + ':' + clConnectorNames[nConnector] + ':' + clActivityNames[nActivity2]  )

     return clActivitiesAndObjectFlows
       


def ParseActivityModel (cFileName):
     clGroupNames, clGroupPositionVectors, clActivityNames, clActivityPositionVectors,clConnectorNames,clConnectorPositionVectors = ParseopenOfficeExportFile(cFileName)
     rTolerancePixels = 50
     clActivitiesAndObjectFlows = CreateActivitiesAndObjectFlows(clActivityNames, clActivityPositionVectors,clConnectorNames,clConnectorPositionVectors, rTolerancePixels)
     clFunctionalGroups = CreateFunctionalGroups(clActivityNames, clActivityPositionVectors, clGroupNames,  clGroupPositionVectors)
     return clActivitiesAndObjectFlows, clFunctionalGroups


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


def RenderActivityDefinitionsInSysML(O,clActivities):
     cSysMLString=''
     cLF = '\r\n'

     for nText in range(len(clActivities)):      
         cSysMLString = cSysMLString + '      action def ' + clActivities[nText] + ' {' + cLF
         for nIn in range(len(clActivities)):
             if O[nIn][nText] != '':
                 sTemp = O[nIn][nText]
                 sFlowString = sTemp.strip()
                 iNumOccurences = sFlowString.count('+')
                 for nParam in range(iNumOccurences  +1):
                     sCurrentFlowName = SubFlow(sFlowString,nParam)
                     sInput = sCurrentFlowName
                     cSysMLString=cSysMLString + '         in ' + sInput + ';' + cLF
              
          
     
         for nOut in range(len(clActivities)):
             if O[nText][nOut] != '':
                 sTemp = O[nText][nOut]
                 sFlowString = sTemp.strip()
                 iNumOccurences = sFlowString.count('+')
                 for nParam in range(iNumOccurences + 1):
                     sCurrentFlowName = SubFlow(sFlowString,nParam)
                     sOutput = sCurrentFlowName 
                     cSysMLString = cSysMLString + '         out ' + sOutput + ';' + cLF
         cSysMLString = cSysMLString + '      }' + cLF
    
     return cSysMLString
     
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


def UpdateMatrixWithFlow(clDomainObjects,clActivities,mMatrixO, sLineToParse):
     sSourceObject,sFlow,sTargetObject = parseFlowLine(sLineToParse)
     clActivities = UpdateUniqueContentCellArray (clActivities, sSourceObject)
     clActivities = UpdateUniqueContentCellArray (clActivities, sTargetObject)
     clDomainObjects = UpdateUniqueContentCellArray (clDomainObjects, sFlow)
     M = len(clActivities);
     mNewMatrixO = [['' for col in range(M)] for row in range(M)]
     for nInitIndex1 in range(M):
         for nInitIndex2  in range(M):
             if nInitIndex1 < len(mMatrixO) and nInitIndex2 < len(mMatrixO):
                 mNewMatrixO[nInitIndex1][nInitIndex2] = mMatrixO[nInitIndex1][nInitIndex2]
             if GetIndexOfStringInCellArray(clActivities,sSourceObject) == nInitIndex1 and GetIndexOfStringInCellArray(clActivities,sTargetObject) == nInitIndex2 :
                 if mNewMatrixO[nInitIndex1][nInitIndex2] == '':
                     mNewMatrixO[nInitIndex1][nInitIndex2] =  sFlow
                 else:
                     mNewMatrixO[nInitIndex1][nInitIndex2] =  mNewMatrixO[nInitIndex1][nInitIndex2] + ' + ' + sFlow  
    
     mMatrixO = mNewMatrixO;
     return clDomainObjects,clActivities,mMatrixO 


def RenderFlowsInSysML(O,clActivities):
     cSysMLString=''
     cLF = '\r\n'
     
     cSysMLString = cSysMLString + '      action def OverallUseCase {' + cLF
    
     for nText in range(len(clActivities)):   
         cSysMLString = cSysMLString + '         action a' + str(nText) + ':' + clActivities[nText] + ';' + cLF
    
     for n1 in range(len(clActivities)): 
         for n2 in range(len(clActivities)):
             if O[n1][n2] != '':
                 sFlowString=(O[n1][n2]).strip()
                 for nParam in range(sFlowString.count('+')+1):
                     sInput = SubFlow(sFlowString,nParam)
                     sResult = sInput
                     cSysMLString = cSysMLString + '         flow from a' + str(n1) + '.' + sResult + ' to a'  + str(n2) + '.' + sInput + ';' + cLF
               

     cSysMLString = cSysMLString + '      }' + cLF
    
     return cSysMLString


def ProcessFasCards(clActivitiesAndObjectFlows, clFunctionalGroups): 
     ### Process Activities and Object Flows
     cSysMLString=''
     cLF = '\r\n'
     clLinesToParse =  clActivitiesAndObjectFlows
     clDomainObjects = []
     clActivities = []
     mMatrixO = []
  
     for nIndex in range(len(clLinesToParse)):
        sLineToParse = clLinesToParse[nIndex]
        clDomainObjects,clActivities,mMatrixO = UpdateMatrixWithFlow(clDomainObjects,clActivities,mMatrixO, sLineToParse)
    
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
          
        
     
      
     cSysMLString=cSysMLString + '   package UseCaseActivities{' + cLF
     cSysMLString = cSysMLString + RenderActivityDefinitionsInSysML(mMatrixO, clActivities)
     cSysMLString = cSysMLString + RenderFlowsInSysML(mMatrixO, clActivities)
     cSysMLString = cSysMLString + '      package FunctionalGroups{' + cLF
     cSysMLString = cSysMLString + RenderFunctionalGroupsInSysML(clGroupName ,clActivities, mMatrixG)
     cSysMLString=cSysMLString + '      }' + cLF
     cSysMLString=cSysMLString + '   }' + cLF
     return cSysMLString 




def  fas_frontend(cFileName,cPath):
     clActivitiesAndObjectFlows, clFunctionalGroups = ParseActivityModel(cFileName)
     cSysMLString = ProcessFasCards(clActivitiesAndObjectFlows, clFunctionalGroups) 
     print(cSysMLString);

  
     return clActivitiesAndObjectFlows, clFunctionalGroups, cSysMLString
        

def main(): 
    cFileName = sys.argv[1]
    ## Path is legacy
    cPath = ''

    clActivitiesAndObjectFlows, clFunctionalGroups, cSysMLString = fas_frontend(cFileName,cPath)

if __name__ == "__main__":
    main()




