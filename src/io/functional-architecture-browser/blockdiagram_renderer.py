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
#   This is the main py file of the block diagram renderer for the FAS plugin for SysML v2.
#
#   When calling as a script, pass the project ID as an optional first parameter
#   and the host url for connecting to the repository as an optional second one.
#
#   The script is made for drawing the functional architecture that was generated by the FAS plugin
#   It depends on blockdiag for rendering the corresponding diagram

import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from time import sleep
from functools import partial
import sys
import json
import tempfile
import base64
import webbrowser
import zlib



import requests 

import platform
import os

from fas4sysmlv2API_helpers import * 




def read_functional_architecture(strProjectID,strServerName):

     clFunctionalBlocksAndFlows= []           

     bSuccess = True
     cErrorMessage = ''
     cProjectID=strProjectID.get()
     cServerName=format_servername(strServerName.get())
     
     print('Reading the functional architecture from project ' + cProjectID + ' on server ' + cServerName + ' ...')
    
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

     clFunctionalBlocks=[]
     clFunctionalBlockIds=[]
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
                 if response.get("@type") == "PartUsage":
                     clFunctionalBlocks.append(response.get("name"))
                     clFunctionalBlockIds.append(response.get("elementId"))
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
         
                 

         #Process Functional Architecture        
         
         
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
                 
                 clPair=[]
                 for iFlowPartner in range (len(clTargetIds)):
                     cTargetId = clTargetIds[iFlowPartner]
                     if  clItemsFlowEndIds.count(cTargetId) > 0:
                         cOwnedRelationship=clItemFlowEndOwnedRelationships[ clItemsFlowEndIds.index(cTargetId)][0].get('@id')
                         if clReferenceSubSettingIds.count(cOwnedRelationship) > 0:
                             cReferencedFeature = clReferenceSubSettingReferencedFeatures[clReferenceSubSettingIds.index(cOwnedRelationship)].get('@id')
                             if clFunctionalBlockIds.count(cReferencedFeature) > 0:
                                 cBlock = clFunctionalBlocks[clFunctionalBlockIds.index(cReferencedFeature)]
                                 clPair.append(cBlock)
                                 
                                 
                 if clItemFeatureIds.count(cFeatureMembershipTarget)>0:
                     cItemFeatureTypeId=clItemFeatureTypes[clItemFeatureIds.index(cFeatureMembershipTarget)]
                     #print (cItemFeatureTypeId)
                     if clItemDefIds.count(cItemFeatureTypeId[0].get('@id'))>0:
                         cItemDefinitionName = clItemDefs[clItemDefIds.index(cItemFeatureTypeId[0].get('@id'))]
                     else:
                         cItemDefinitionName = ''

                 if len(clPair) == 2:
                    clFunctionalBlocksAndFlows.append({"source": clPair[0], "flow": cItemDefinitionName, "target":   clPair[1]})
         
         return bSuccess, cErrorMessage, clFunctionalBlocksAndFlows


	
    


def extend_flow_string (sFlow, sNew):
     sFlow_extended = sFlow
     if len(sFlow) > 0: 
         sFlow_extended = sFlow_extended + ', '
     sFlow_extended = sFlow_extended + sNew
     return sFlow_extended


def evaluateFlow(sLine):   
     return sLine.get('source'),sLine.get('flow'),sLine.get('target')

def render_images(cProjectID,cServerName,cFolder,mainWindow):
    mainWindow.config(cursor="wait")
    sleep(0.1)
    mainWindow.update()
    sleep(0.1)
    thehost = cServerName.get()
    project_id=cProjectID.get()                    
    data = read_full_repository(thehost , project_id)
    imagenum = 0
    for myelement in data:
        if myelement.get('@type')=='LiteralString' and myelement.get('value')!='base64' and myelement.get('value')!='image/jpeg':
            imagenum = imagenum + 1
            imageString = myelement.get('value')
            cImageName = cFolder.get() + 'Image' + str(imagenum) +'.html'
            FID=open(cImageName,'w')
            FID.write('<html><body><img src="data:image/jpg;base64, ' +imageString +'" alt="" /></body></html>')
            FID.close()                 
            webbrowser.open_new(cImageName)
    mainWindow.config(cursor="")

def render_diagram(cProjectID,cServerName,mainWindow):
     mainWindow.config(cursor="wait")
     sleep(0.1)
     mainWindow.update()
     sleep(0.1)
     bSuccess, cErrorMsg, clFunctionalBlocksAndFlows = read_functional_architecture(cProjectID,cServerName)
     if bSuccess == False:
         messagebox.showerror("Diagram Renderer","Reading from the repository failed with the following error message: " + cErrorMsg)
     else:
         # blockdiag currently only supports one connection per pair of blocks
         # connections will be unified by direction and sorted by connection partner
         # Then multiple flows will be visualized by concatenating a corresponding string to label the connection



         clNormalizedBlocksAndFlows =[]

         for cLineToInsert in clFunctionalBlocksAndFlows:
             cNewSource, cNewFlow, cNewTarget  = evaluateFlow( cLineToInsert )
             bUpdated = False
             for iLineToProcess in range(len(clNormalizedBlocksAndFlows )):
                 dictCurrent = clNormalizedBlocksAndFlows[iLineToProcess]
                 cSource = dictCurrent.get('source')
                 cTarget = dictCurrent.get('target')
                 cFlowsS2T = dictCurrent.get('source_to_target_flows')
                 cFlowsT2S = dictCurrent.get('target_to_source_flows')
                 if cSource == cNewSource and cTarget == cNewTarget:
                     cFlowsS2T = extend_flow_string(cFlowsS2T, cNewFlow)
                     clNormalizedBlocksAndFlows[iLineToProcess] = { 'source': cSource, 'target' :  cTarget, 'source_to_target_flows' : cFlowsS2T, 'target_to_source_flows': cFlowsT2S }
                     bUpdated = True
                 elif cTarget == cNewSource and cSource == cNewTarget:
                     cFlowsT2S = extend_flow_string(cFlowsT2S, cNewFlow)
                     clNormalizedBlocksAndFlows[iLineToProcess] = { 'source': cSource, 'target' :  cTarget, 'source_to_target_flows' : cFlowsS2T, 'target_to_source_flows': cFlowsT2S }
                     bUpdated = True

             if bUpdated == False:
                     clNormalizedBlocksAndFlows.append({ 'source': cNewSource, 'target' :  cNewTarget, 'source_to_target_flows' : cNewFlow, 'target_to_source_flows': '' })

                     

         cDiag = ''
         cNewLine = '\n'
         cDiag = cDiag + 'blockdiag {' + cNewLine
         cSpace = '  '
         if len(clNormalizedBlocksAndFlows) < len(clFunctionalBlocksAndFlows):
             # Some flows are labled with multiple items. The font size needs to be reduced
             cDiag = cDiag + cSpace + 'default_fontsize = 3' + cNewLine
         else:
             cDiag = cDiag + cSpace + 'default_fontsize = 5' + cNewLine
         for cLine in clNormalizedBlocksAndFlows: 
             cDiagLine = ''             
             if len(cLine.get('target_to_source_flows'))>0:
                 #Flows in both directions exist
                 cItemDefinitionName = cLine.get('target_to_source_flows') + '   <-->   ' + cLine.get('source_to_target_flows')
                 cDiagLine = cLine.get('source')  + ' <-> ' + cLine.get('target')   + ' [label = "' + cItemDefinitionName + '" ]'                
             else:
                 cItemDefinitionName = cLine.get('source_to_target_flows')                 
                 cDiagLine = cLine.get('source') + ' -> '  + cLine.get('target')   + ' [label = "' + cItemDefinitionName + '" ]'                
                

             cDiag = cDiag + cSpace + cDiagLine  + cNewLine

         cDiag = cDiag + '}'  + cNewLine

         print('------------------------------------------')
         print('')
         print(cDiag)
         print('')
         print('------------------------------------------')


         encoded = base64.b64encode(zlib.compress(bytes(cDiag, "utf-8"))).decode("ascii")
         cURL = 'http://interactive.blockdiag.com/image?compression=deflate&encoding=base64&src=' + encoded.replace('/','_').replace('+','-')

         print('Opening ' + cURL)
         mainWindow.config(cursor="")
         
         webbrowser.open_new(cURL)


def run_renderer(cProjectUUID, cHost, cFolder):
     mainWindow = Tk()
     mainWindow.title("Block Diagram Renderer")
     frm = ttk.Frame(mainWindow)
     frm.grid(row=0, column=0, columnspan=3)

     ttk.Label(frm, text="WARNING: Before running, please check that http://blockdiag.com/ still exists").grid(column=0, row=0)
     cProjectID = StringVar()
     cProjectID.set(cProjectUUID)
     strFolder= StringVar()
     strFolder.set(cFolder)
     cServerName = StringVar()
     cServerName.set(cHost)
     ttk.Label(frm, text="").grid(column=0, row=1)
     ttk.Label(frm, text="Server").grid(column=0, row=2)
     ttk.Entry(frm, textvariable = cServerName, width = 50).grid(column=1, row=2)
     ttk.Label(frm, text="Project UUID").grid(column=0, row=3)
     ttk.Entry(frm, textvariable = cProjectID, width = 50).grid(column=1, row=3)
     ttk.Button(frm, text="Select", command=partial(selectproject,cProjectID,cServerName)).grid(column=2, row=3)
     ttk.Label(frm, text="").grid(column=0, row=4)
     bShowBlockdiag = True
     bShowImage=True
     bSuccess = True
     if cProjectUUID!='':
         try:
             response = requests.get(cHost + "/projects/" + cProjectUUID)
         except  requests.exceptions.ConnectionError:
             bSuccess = False

         
         if bSuccess and response.status_code==200:
             data = response.json()
             cProjectName = data.get('name')
             if cProjectName.find('UseCaseActivities')>-1:
                 bShowBlockdiag = False
                 bShowImage=True             
             else:
                 bShowBlockdiag = True
                 bShowImage=False             

     if bShowBlockdiag:
         ttk.Button(frm, text="Render block diagram", command=partial(render_diagram,cProjectID,cServerName,mainWindow)).grid(column=1, row=5)
     if bShowImage:
         if bShowBlockdiag:
            iColumn = 2
         else:
            iColumn = 1 
         ttk.Button(frm, text="Show images", command=partial(render_images,cProjectID,cServerName,strFolder,mainWindow)).grid(column=iColumn, row=5)
     ttk.Button(frm, text="Quit", command=mainWindow.destroy).grid(column=3, row=5)
     mainWindow.mainloop()


def main(): 
    cProject= sys.argv[1].strip()
    cHost = sys.argv[2].strip()
    cFolder = sys.argv[3].strip()


    run_renderer(cProject, cHost, cFolder)

if __name__ == "__main__":
    main()
