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
import os
import json
import base64


def isWithSpecialCharacters(cName):
    return any(not (cCurrent.isalnum() or cCurrent=='_') for cCurrent in cName)

def wrapNameInCorrectQuotes(cName):
    cNameNew = cName
    if isWithSpecialCharacters(cName):
        cNameNew = "'" + cNameNew + "'" 
    return cNameNew

def RenderFunctionalGroupsInSysML(clGroupName,clActivities, mMatrixG):
     cSysMLString=''
     cLF = '\r\n'
     N=len(mMatrixG)  
     if N>0:
         M=len(mMatrixG[0])
     else:
         M=0
         
     for n in range(N):
         cSysMLString= cSysMLString + '      package ' + wrapNameInCorrectQuotes(clGroupName[n]) + '{' + cLF
         for m in range (M):
             if mMatrixG[n][m] > 0:
                 cSysMLString = cSysMLString + '         import UseCaseActivities::overallUseCase::' + wrapNameInCorrectQuotes(clActivities[m]) + ';' + cLF
         
         cSysMLString= cSysMLString + '      }' + cLF

     
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
# This function is there due to porting from another programming language without an "append()" function
# It shall be fully replaced by "append()" during further code cleaning
     clOld.append(newEntry)      
     return clOld


def ParseFullActivityName(sFullName):
     #If the Full name start with a number in round brackets, then this number is cut away and returned separately
     #If no number is available, then -1 will be returned as the Activity number
     iActivityNumber = -1
     sName = sFullName.strip()
     if sName[0] == '(':
         iClosingBracketPos = sName.find(')')
         if (iClosingBracketPos > -1) and (len(sName) > (iClosingBracketPos + 1)):
             if iClosingBracketPos > 1:
                 iActivityNumber = int(sName [1:(iClosingBracketPos)])
             sName = sName [(iClosingBracketPos+1):].strip()

     return sName, iActivityNumber 

def ParseopenOfficeExportFile(cFileName):
     FID1_ID = open(cFileName,'r')
     clGroupNames=[]
     clGroupPositionVectors=[]
     clActivityDictionary=[]
     bActivityNumbersAreExhaustive=True
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
             sFullName, iLineIndex = Readname(FID1,iLineIndex)
             sName, iActivityNumber = ParseFullActivityName(sFullName)
             if iActivityNumber == -1:
                 bActivityNumbersAreExhaustive=False
             vPositionsXY, iLineIndex = ReadPositions(FID1,4,iLineIndex)
             clActivityDictionary.append({ 'name': sName, 'number' :  iActivityNumber, 'positions' : vPositionsXY })
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

     # If all Activities have been numbered by a preceding number in round brackets in the name, then sort activity names and positions by activity number,
     # otherwise sort alphabetically by activity name, in order to have reproducible matrix content with equivalent input, independent from order of elements 
     # in the graphical representation of the input.
     if bActivityNumbersAreExhaustive:
         clActivityDictionary = sorted(clActivityDictionary, key=lambda act: act.get('number'))
     else:
         clActivityDictionary = sorted(clActivityDictionary, key=lambda act: act.get('name'))

     clActivityNames=[cAct.get('name') for cAct in clActivityDictionary]
     clActivityPositionVectors=[cAct.get('positions') for cAct in clActivityDictionary]

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
       
     return sorted(clFunctionalGroups) 
 
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
     return clActivitiesAndObjectFlows, clFunctionalGroups, clActivityNames


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
                     clGroupNew[nFillIndex] = clGroup[nFillIndex] 
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


def RenderActivityDefinitionsInSysML(O,clActivities, clActivityNamesSorted, sImages):
     # The use case activities in clActivities are connected with each other via matrix O
     # The exhaustive set of use case activities to render (including the ones without connections)
     # is provided in clActivityNamesSorted. The sort order in clActivityNamesSorted will
     # be the order in which the Actions will be declared in SysML v2.

     clSysMLStringsToBeSorted = []
     clActionDefs = clActivityNamesSorted
     cLF = '\r\n'


     for nText in range(len(clActivities)):      
         clBufferOfNamesForUniqueness = [] # Remember all parameter names to be able to ensure uniqueness

         cSysMLString = '         action ' + wrapNameInCorrectQuotes(clActivities[nText]) + ' {' + cLF
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
                     cSysMLString=cSysMLString + '            in ' + wrapNameInCorrectQuotes(sInput) + ';' + cLF
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
                     cSysMLString = cSysMLString + '            out ' + wrapNameInCorrectQuotes(sOutput) + ';' + cLF
                     clBufferOfNamesForUniqueness.append(sOutput) 
         
         cImageSysMLString1 = ''
         cImageSysMLString2 = ''
         for currentImage in sImages:
             if currentImage.get('activity') == clActivities[nText]:
                 cImageSysMLString1 = currentImage.get('sysml1')
                 cImageSysMLString2 = currentImage.get('sysml2')

         cSysMLString = cSysMLString + cImageSysMLString2 + '         }' + cLF

         iSortNumber = -1
         if clActivityNamesSorted.count(clActivities[nText]) > 0:
             iSortNumber = clActivityNamesSorted.index(clActivities[nText]) 

         clSysMLStringsToBeSorted.append({'name' : clActivities[nText], 'sysml' : cImageSysMLString1 + cSysMLString, 'number' : iSortNumber })

     #Process use case activities without object flows
     for nFullListIndex in range(len(clActivityNamesSorted)):
         if clActivities.count(clActivityNamesSorted[nFullListIndex]) < 1:
             cSysMLStringTemp = '         action ' + wrapNameInCorrectQuotes(clActivityNamesSorted[nFullListIndex]) + ' {' + cLF + '         }' + cLF 
             clSysMLStringsToBeSorted.append({'name' : clActivityNamesSorted[nFullListIndex], 'sysml' : cSysMLStringTemp, 'number' : nFullListIndex })

     clSysMLStringsSorted = sorted(clSysMLStringsToBeSorted, key=lambda act: act.get('number'))

     cSysMLStringFinal = '';

     for nString in range(len(clSysMLStringsSorted )):
         cSysMLStringFinal = cSysMLStringFinal + clSysMLStringsSorted[nString].get('sysml')


     return clActionDefs, cSysMLStringFinal
     
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


def RenderFlowsAndItemDefsInSysML(O,clActivities,clActivityNamesSorted, sImages):
     cSysMLString=''
     cItemString='' 
     cLF = '\r\n'

     
     cSysMLString = cSysMLString + '      action overallUseCase {' + cLF
    
     clActionNames, cSysMLStringToAdd = RenderActivityDefinitionsInSysML(O,clActivities,clActivityNamesSorted, sImages)

     cSysMLString = cSysMLString + cSysMLStringToAdd
    
     clBufferOfAllUsedItemDefs = [] #Remember what was already defined to avoid duplications
     for n1 in range(len(clActivities)): 
         for n2 in range(len(clActivities)):
             if O[n1][n2] != '':
                 sFlowString=(O[n1][n2]).strip()
                 for nParam in range(sFlowString.count('+')+1):
                     sCurrentFlowName = SubFlow(sFlowString,nParam)
                     sResult = sCurrentFlowName.lower() 
                     sInput = sCurrentFlowName.lower() 

                     cSysMLString = cSysMLString + '         flow of ' + wrapNameInCorrectQuotes(sCurrentFlowName) + ' from ' + wrapNameInCorrectQuotes(clActionNames[n1]) + '.' + wrapNameInCorrectQuotes(sResult) + ' to '  + wrapNameInCorrectQuotes(clActionNames[n2]) + '.' + wrapNameInCorrectQuotes(sInput) + ';' + cLF

                     if clBufferOfAllUsedItemDefs.count(sCurrentFlowName) < 1:
                         clBufferOfAllUsedItemDefs.append(sCurrentFlowName)
                         cItemString = cItemString + '   item def ' + wrapNameInCorrectQuotes(sCurrentFlowName) + ';' + '\r\n'
              

     cSysMLString = cSysMLString + '      }' + cLF
    
     return cSysMLString, cItemString, clActionNames


def ProcessFasCards(clActivitiesAndObjectFlows, clFunctionalGroups, clActivityNamesSorted, sImages): 
     ### Process Activities and Object Flows
     cSysMLString=''
     cLF = '\r\n'
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
          
        
     
     sFlows, sItemDefs, clActionNames = RenderFlowsAndItemDefsInSysML(mMatrixO, clActivities, clActivityNamesSorted, sImages)
     cSysMLString=cSysMLString + sItemDefs + cLF  + '   package UseCaseActivities{' + cLF
     cSysMLString = cSysMLString + sFlows
     cSysMLString=cSysMLString   + '   }' + cLF
     cSysMLString = cSysMLString + '   package FunctionalGroups{' + cLF
     cSysMLString = cSysMLString + RenderFunctionalGroupsInSysML(clGroupName ,clActionNames, mMatrixG)
     cSysMLString=cSysMLString   + '   }' + cLF
     return cSysMLString 


def GetSamsMethodImages(cPath,clActivityNamesInSortOrder):
     sImages = [];
     for cActivity in clActivityNamesInSortOrder:
         if os.path.isdir(cPath+cActivity):
              filename = cPath+cActivity+os.sep+'DataSerializer.json'
              if os.path.exists(filename):
                  FID = open(filename)
                  data = json.load(FID)
                  FID.close()
                  theTree = data.get("tree")
                  imagename = ''
                  for imagenameKey in theTree.keys():
                      imagename = str(imagenameKey)
                      break
                  newstruct = theTree.get(imagename)
                  bFoundCoordinates = False;
                  for coordinatesKey in newstruct.keys():
                      coordinatesKeyString = str(coordinatesKey)
                      bFoundCoordinates = True
                      break
                  if bFoundCoordinates:
                      coordinatesStruct = newstruct.get(coordinatesKeyString)
                      x1=coordinatesStruct.get('x1')
                      x2=coordinatesStruct.get('x2')
                      y1=coordinatesStruct.get('y1')
                      y2=coordinatesStruct.get('y2')
                  else:
                      x1 = 0
                      x2 = 0
                      y1 = 0
                      y2 = 0

                  cSysMLstring1 = ''
                  cSysMLstring2 = ''
                  with open( cPath+cActivity+os.sep+imagename,'rb' ) as file:
                      binContent = file.read()
                      encodedContent = base64.b64encode(binContent).decode()
                      cNewLine= '\r\n'
                      cMimeType = '"image/jpeg"'
                      if imagename.find('.png')>-1:
                          cMimeType = '"image/png"'
                      cSysMLstring1 = '         import ImageMetadata::*;'+cNewLine+'         metadata '+wrapNameInCorrectQuotes('img'+cActivity)+' : Icon about '+ wrapNameInCorrectQuotes(cActivity) +' {'+cNewLine+'               :>> fullImage = Image(){'+cNewLine+'                  content="'+encodedContent+'";'+cNewLine+'                  encoding="base64";'+cNewLine+'                  type='+cMimeType+';'+cNewLine+'               }'+cNewLine+'         }'+cNewLine
                  cSysMLstring2 = '            attribute samsX1 = ' + str(x1)+';'+cNewLine
                  cSysMLstring2 = cSysMLstring2 + '            attribute samsX2 = ' + str(x2)+';'+cNewLine
                  cSysMLstring2 = cSysMLstring2 + '            attribute samsY1 = ' + str(y1)+';'+cNewLine
                  cSysMLstring2 = cSysMLstring2 + '            attribute samsY2 = ' + str(y2)+';'+cNewLine
                  sImages.append({"activity": cActivity, "sysml1": cSysMLstring1, "sysml2": cSysMLstring2})
      
     return sImages
     

def  fas_frontend(cFileName,cPath):
     clActivitiesAndObjectFlows, clFunctionalGroups, clActivityNamesInSortOrder = ParseActivityModel(cFileName)
     sImages = []
     if cPath.strip()!='':
         sImages=GetSamsMethodImages(cPath.strip(),clActivityNamesInSortOrder)
     cSysMLString = ProcessFasCards(clActivitiesAndObjectFlows, clFunctionalGroups, clActivityNamesInSortOrder,sImages) 
     print(cSysMLString);

  
     return clActivitiesAndObjectFlows, clFunctionalGroups, cSysMLString, clActivityNamesInSortOrder 
        

def main(): 
    cFileName = sys.argv[1]
    cPath = sys.argv[2].strip()

    clActivitiesAndObjectFlows, clFunctionalGroups, cSysMLString, clActivityNamesInSortOrder  = fas_frontend(cFileName,cPath)

if __name__ == "__main__":
    main()




