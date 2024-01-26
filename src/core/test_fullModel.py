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
#   This is a test script for the FAS plugin for SysML v2.
#
#   It reads and dumps the full model that comes out of an end-to-end plugin execution       
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
from fas4sysmlv2API_helpers import *

from sympy import *
from time import *

import requests 

import platform
import os

def isWithSpecialCharacters(cName):
    return any(not (cCurrent.isalnum() or cCurrent=='_') for cCurrent in cName)

def wrapNameInCorrectQuotes(cName):
    cNameNew = cName
    if isWithSpecialCharacters(cName):
        cNameNew = "'" + cNameNew + "'" 
    return cNameNew

 



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

     

     
     
  

  
def read_activities_and_functional_groups(strProjectID,strServerName):

     clActivitiesAndObjectFlows = []           
     clFunctionalGroups = []

     bSuccess = True
     cErrorMessage = ''
     cProjectID=strProjectID.get()
     cServerName=format_servername(strServerName.get())
     
     print('Reading Use Case Activities and Functional Groups from project ' + cProjectID + ' on host ' + cServerName + ' ...')
    
     try:
         response = requests.get(cServerName + "/projects/" + cProjectID)
     except  requests.exceptions.ConnectionError:
         bSuccess = False
         cErrorMessage = 'Error: Could not connect to server'
         print(cErrorMessage)

         
     if bSuccess and response.status_code!=200:
         bSuccess = False
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
             if len(data)>200:
                 print('  -> Found ' +str(len(data))+ ' elements of type '  +  cElementType)
              
             currentSet = []
             for currentRecord in data:
                 sIdToGet=currentRecord.get('@id')
                 qresult, response = multi_page_http_get(cServerName + "/projects/" + cProjectID + "/commits/"+sHeadCommit+"/elements/" + sIdToGet)
                 currentSet.append(response)

             for response in currentSet:

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
                     bIgnoreAction = False
                     for cCurrentAction in currentSet: #We know that "data" is a list of ActionUsages, because lists are retrieved type-by-type
                         cOwnerID = cCurrentAction.get('owner').get('@id')
                         if response.get("@id") == cOwnerID:
                             bIgnoreAction = True #If the action owns other actions it is not a leaf and must be ignored.
                     if bIgnoreAction == False:
                         clActions.append(response.get("name") + "-" + response.get('@id'))
                         clActionIds.append(response.get("elementId"))
                 if response.get("@type") == "ItemDefinition":
                     clItemDefs.append(response.get("name") + "-" + response.get('@id'))
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
                     clPackageNames.append(response.get("name") + "-" + response.get('@id'))
         
                 

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
     clFunctionalGroupsSorted = sorted(clFunctionalGroups)
     return bSuccess, cErrorMessage, clActivitiesAndObjectFlows, clFunctionalGroupsSorted, clActivityNamesSorted


def read_functionalArchitecture(strProjectID,strServerName):
     #This is copy and paste from the corresponding activity reading function. To be done: Find more suitable variable names, now that we read functional locks and not activity names

     clActivitiesAndObjectFlows= []           
     clFunctionalGroups = []

     bSuccess = True
     cErrorMessage = ''
     cProjectID=strProjectID.get()
     cServerName=format_servername(strServerName.get())
     
     print('Functional Blocks and their interfaces from project ' + cProjectID + ' on host ' + cServerName + ' ...')
    
     try:
         response = requests.get(cServerName + "/projects/" + cProjectID)
     except  requests.exceptions.ConnectionError:
         bSuccess = False
         cErrorMessage = 'Error: Could not connect to server'
         print(cErrorMessage)

         
     if bSuccess and response.status_code!=200:
         bSuccess = False
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

     clElementTypes = ['ReferenceSubsetting','EndFeatureMembership','FeatureMembership','ItemFlowEnd','PartUsage','ItemDefinition','FlowConnectionUsage','ItemFeature','Package']
     
     if bSuccess:
     
         for cElementType in clElementTypes:
             data = run_query_for_elementtyp(cElementType, cServerName, cProjectID)
             if len(data)>200:
                 print('  -> Found ' +str(len(data))+ ' elements of type '  +  cElementType)
              
             currentSet = []
             for currentRecord in data:
                 sIdToGet=currentRecord.get('@id')
                 qresult, response = multi_page_http_get(cServerName + "/projects/" + cProjectID + "/commits/"+sHeadCommit+"/elements/" + sIdToGet)
                 currentSet.append(response)

             for response in currentSet:

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
                 if response.get("@type") == "PartUsage":
                     bIgnoreAction = False
                     for cCurrentAction in currentSet: #We know that "data" is a list of ActionUsages, because lists are retrieved type-by-type
                         cOwnerID = cCurrentAction.get('owner').get('@id')
                         if response.get("@id") == cOwnerID:
                             bIgnoreAction = True #If the action owns other actions it is not a leaf and must be ignored.
                     if bIgnoreAction == False:
                         clActions.append(response.get("name") + "-" + response.get('@id'))
                         clActionIds.append(response.get("elementId"))
                 if response.get("@type") == "ItemDefinition":
                     clItemDefs.append(response.get("name") + "-" + response.get('@id'))
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
                     clPackageNames.append(response.get("name") + "-" + response.get('@id'))
         
                 

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
     clFunctionalGroupsSorted = sorted(clFunctionalGroups)
     return bSuccess, cErrorMessage, clActivitiesAndObjectFlows, clFunctionalGroupsSorted, clActivityNamesSorted




def read_relationships(strProjectID,strServerName):

     bSuccess = True
     cErrorMessage = ''
     cProjectID=strProjectID.get()
     cServerName=format_servername(strServerName.get())
     
     print('Relationships from project ' + cProjectID + ' on host ' + cServerName + ' ...')
    
     try:
         response = requests.get(cServerName + "/projects/" + cProjectID)
     except  requests.exceptions.ConnectionError:
         bSuccess = False
         cErrorMessage = 'Error: Could not connect to server'
         print(cErrorMessage)

         
     if bSuccess and response.status_code!=200:
         bSuccess = False
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


     clElementTypes = ['Dependency','OwningMembership','Package']
     
     if bSuccess:
     
         currentSet = []
         for cElementType in clElementTypes:
             data = run_query_for_elementtyp(cElementType, cServerName, cProjectID)
             if len(data)>200:
                 print('  -> Found ' +str(len(data))+ ' elements of type '  +  cElementType)
              
             for currentRecord in data:
                 sIdToGet=currentRecord.get('@id')
                 qresult, response = multi_page_http_get(cServerName + "/projects/" + cProjectID + "/commits/"+sHeadCommit+"/elements/" + sIdToGet)
                 currentSet.append(response)

         print('')
         print('Packages: ')
          
         for response in currentSet:
                 if response.get("@type") == "Package":
                     print(response.get("name") + ' --> ' + response.get('@id'))
 
         print('')
         print('OwningMemberships: ')

         for response in currentSet:
                 if response.get("@type") == "OwningMembership": 
                     OwnerId = response.get('membershipOwningNamespace')
                     OwnedId = response.get('ownedMemberElementId')
                     print('Owner -> ' + OwnerId.get('@id') + ' --- Owned -> ' + OwnedId);

         print('')
         print('Dependencies: ')

         for response in currentSet:

                 if response.get("@type") == "Dependency": 
                     print('Dependency '+response.get('@id')+  ' from ' + response.get('source')[0].get('@id')  + ' to '  + response.get('target')[0].get('@id') )





def fas_transform(cProjectID,cServerName,cNewProjectID,mainWindow):

     bSuccess, cErrorMsg, clFctArch, clFunctionalGroups, clActivityNamesSorted = read_functionalArchitecture(cProjectID,cServerName)
     print(clFctArch)

     print('')

     bSuccess, cErrorMsg, clActivitiesAndObjectFlows, clFunctionalGroups, clActivityNamesSorted = read_activities_and_functional_groups(cProjectID,cServerName)
     print('Use Case Activities and Object Flows:')

     print(clActivitiesAndObjectFlows)
     print('')
     print('Functional Groups:')
     print(clFunctionalGroups)
     print('')
     
     read_relationships(cProjectID,cServerName)
     

         
def run_fas4sysml(cProjectUUID, cHost):
     mainWindow = Tk()
     mainWindow.title("FAS Plugin")
     frm = ttk.Frame(mainWindow)
     frm.grid(row=0, column=0, columnspan=3)

     ttk.Label(frm, text="FAS Plugin for SysML v2").grid(column=0, row=0)
     cProjectID = StringVar()
     cNewProjectID = StringVar()
     cProjectID.set(cProjectUUID)
     cNewProjectID.set(cProjectUUID)
     cServerName = StringVar()
     cServerName.set(cHost)
     ttk.Label(frm, text="").grid(column=0, row=1)
     ttk.Label(frm, text="Server").grid(column=0, row=2)
     ttk.Entry(frm, textvariable = cServerName, width = 50).grid(column=1, row=2)
     ttk.Label(frm, text="Project UUID").grid(column=0, row=3)
     ttk.Entry(frm, textvariable = cProjectID, width = 50).grid(column=1, row=3)
     ttk.Button(frm, text="Select", command=partial(selectproject,cProjectID,cServerName)).grid(column=2, row=3)
     ttk.Label(frm, text="").grid(column=0, row=4)
     ttk.Button(frm, text="Run FAS model read", command=partial(fas_transform,cProjectID,cServerName,cNewProjectID,mainWindow)).grid(column=1, row=5)
     ttk.Button(frm, text="Quit", command=mainWindow.destroy).grid(column=2, row=5)
     mainWindow.mainloop()
     return cNewProjectID.get(), cServerName.get()


def main():
     init_printing(use_unicode=False)

     cProjectID = ''
     cHost = 'http://localhost:9000'
     if len (sys.argv)>1:
         cProjectID=sys.argv[1]
     if len (sys.argv)>2:
         cHost=sys.argv[2]
     cNewProjectID, cNewServerName = run_fas4sysml(cProjectID,cHost)


if __name__ == "__main__":
     main()
