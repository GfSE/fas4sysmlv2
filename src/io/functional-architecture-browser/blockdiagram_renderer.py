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


def isWithSpecialCharacters(cName):
    return any(not cCurrent.isalnum() for cCurrent in cName)

def wrapNameInCorrectQuotes(cName):
    cNameNew = cName
    if isWithSpecialCharacters(cName):
        cNameNew = "'" + cNameNew + "'" 
    return cNameNew

def wrapNameInCorrectQuotesForGraphViz(cName):
    cNameNew = cName
    if isWithSpecialCharacters(cName):
        cNameNew = '"' + cNameNew + '"' 
    return cNameNew


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
    mainWindow.config(cursor="watch")
    sleep(0.1)
    mainWindow.update()
    sleep(0.1)
    thehost = cServerName.get()
    project_id=cProjectID.get()                    
    data = read_full_repository(thehost , project_id)
    imagenum = 0
    clReferenceUsages = []
    clReferenceUsageOwners = []
    clMetadataUsages = []
    clMetadataUsageOwners = []
    clActionUsages = []
    clActionUsageNames = []
    clActionUsageOwners = []
    for myelement in data:
        #Collect some relationships in from the model
        if myelement.get('@type')=='ActionUsage':
             clActionUsages.append(myelement.get('@id'))
             clActionUsageOwners.append(myelement.get('owner').get('@id'))
             clActionUsageNames.append(myelement.get('name'))
        if myelement.get('@type')=='MetadataUsage':
             clMetadataUsages.append(myelement.get('@id'))
             clMetadataUsageOwners.append(myelement.get('annotatedElement')[0].get('@id'))
        if myelement.get('@type')=='ReferenceUsage':
             clReferenceUsages.append(myelement.get('@id'))
             clReferenceUsageOwners.append(myelement.get('owner').get('@id'))
             
    for myelement in data:
        if myelement.get('@type')=='LiteralString' and myelement.get('value')!='base64' and myelement.get('value')!='image/jpeg' and myelement.get('value')!='image/png':
            #Find the ActionUsage that is the owner of the ItemUsage that owns the Image that owns the StringLiteral (by jumping via 2 reference usages and one direct ownership)
            currentOwnerId = myelement.get('owner').get('@id')
            cAction = ''
            sCoordinates = []
            if clReferenceUsages.count(currentOwnerId)>0:
                cReferenceUsageOwnerId=clReferenceUsageOwners[clReferenceUsages.index(currentOwnerId)]
                if clReferenceUsages.count(cReferenceUsageOwnerId)>0:                    
                    cReferenceUsageOwnerId=clReferenceUsageOwners[clReferenceUsages.index(cReferenceUsageOwnerId)]
                    if clMetadataUsages.count(cReferenceUsageOwnerId)>0:
                        cItemUsageOwnerId=clMetadataUsageOwners[clMetadataUsages.index(cReferenceUsageOwnerId)]
                        if clActionUsages.count(cItemUsageOwnerId)>0:
                            cAction=clActionUsageNames[clActionUsages.index(cItemUsageOwnerId)]

                            # Find the coordinates of the image snippet (they are attributes of the item usage) 
                            for myelement2 in data:
                                if myelement2.get('@id')==clActionUsages[clActionUsages.index(cItemUsageOwnerId)]:
                                    vOwned2=myelement2.get('ownedElement')
                                    for eOwned2 in vOwned2:
                                        idOwned2 = eOwned2.get('@id')
                                        for myelement3 in data:
                                            if myelement3.get('@id')==idOwned2 and myelement3.get('@type')=='AttributeUsage':
                                                cCoordinateName = myelement3.get('name')
                                                vOwned3=myelement3.get('ownedElement')
                                                for eOwned3 in vOwned3:
                                                    idOwned3 = eOwned3.get('@id')
                                                    cCoordinateValue = ''
                                                    for myelement4 in data:
                                                        if myelement4.get('@id')==idOwned3: #and myelement3.get('@type')=='Mutiplicity':
                                                            if cCoordinateValue == '' and str(myelement4.get('value')).isdigit():
                                                                 cCoordinateValue = int(str(myelement4.get('value')))
                                                                 sCoordinates.append({"name": cCoordinateName, "value": cCoordinateValue})
 
            sCoordinates = sorted(sCoordinates, key=lambda coord: coord.get('name'))

            imagenum = imagenum + 1
            imageString = myelement.get('value')
            cImageName = cFolder.get() + 'Image' + str(imagenum) +'.html'
            FID=open(cImageName,'w')
            cCoordinates = ''
            ix1 = 0
            iy1 = 0
            ix2 = 0
            iy2 = 0
            for currentCoordinate in sCoordinates:
                cCoordinates = cCoordinates + currentCoordinate.get('name') + ' = ' +  str(currentCoordinate.get('value')) +'; ' 
                if currentCoordinate.get('name')=='samsX1':
                    ix1=currentCoordinate.get('value')
                if currentCoordinate.get('name')=='samsY1':
                    iy1=currentCoordinate.get('value')
                if currentCoordinate.get('name')=='samsX2':
                    ix2=currentCoordinate.get('value')
                if currentCoordinate.get('name')=='samsY2':
                    iy2=currentCoordinate.get('value')
            if ix1>ix2:
                ixtemp=ix1
                ix1=ix2
                ix2=ixtemp
            if iy1>iy2:
                iytemp=iy1
                iy1=iy2
                iy2=iytemp
                    
                   
            if cCoordinates == '':
                cCoordinates = 'none'
            FID.write('<html><body><img width="800" style=\'text-align: left; max-width: 100%; max-height: 100%;\' src="data:image/jpg;base64, ' +imageString +'" alt="" /></div> <div style=\'display: table-cell; position:absolute; border: 2px solid red; left: ' +str(ix1/0.965-5.0)+ 'px; top: ' +str(iy1/0.965+8.0)+ 'px; width: '+str((ix2-ix1)/0.965-0.0)+'px; height: '+str((iy2-iy1)/0.965-0.0)+'px \'></div><p><font size="+2">'+cAction+'</font></p></body></html>')
            # abandoned border: <div style=\'display: table-cell; position:absolute; border: 2px solid red; left: ' +str(0)+ 'px; top: ' +str(0)+ 'px; width: '+str(500)+'px; height: '+str(500)+'px \'>
            # abandoned coordinate information: <p>(Coordinates: '+cCoordinates+')</p>
            FID.close()                 
            webbrowser.open_new(cImageName)
    mainWindow.config(cursor="")

def ProcessUrlInput(subWindow,theText,cProjectID,cServerName,mainWindow,strBaseURLParam,clFunctionalBlocksAndFlows,bIsDemoRun,cImageFolder):
    sText = theText.get()
    strBaseURLParam.set(sText)
    print('     URL for rendering: ' + strBaseURLParam.get())
    subWindow.destroy()
    print('     Rendering ...')
    render_diagram(cProjectID,cServerName,mainWindow,strBaseURLParam,clFunctionalBlocksAndFlows,bIsDemoRun,cImageFolder)
    print('        Rendering done.')
    strBaseURLParam.set('')

def askForBaseUrl(cProjectID,cServerName,mainWindow,strBaseURLParam,clFunctionalBlocksAndFlows,bIsDemoRun,cImageFolder):
     subWindow = Tk()
     subWindow.title("URL Input")
     frm = ttk.Frame(subWindow)
     strURL = StringVar()
     strURL.set("")
     frm.grid(row=0, column=0, columnspan=3)
     ttk.Label(frm, text="Please specify an URL to use for block diagram rendering.").grid(column=0, row=0)
     ttk.Label(frm, text="You can get rid of this dialog by hard-coding the URL in the variable strRenderingUrl").grid(column=1, row=1)
     ttk.Label(frm, text="in the first line of render_diagram in blockdiagram_renderer.py.").grid(column=1, row=2)
     ttk.Label(frm, text="                                                                           URL: ").grid(column=0, row=3)
     theText = ttk.Entry(frm, textvariable = strURL, width = 80)
     theText.insert(END, 'graphviz')
     theText.grid(column=1, row=3)
     ttk.Label(frm, text="You must ensure yourself that any URL you enter or hard-code raises no security concerns.").grid(column=1, row=4)
     ttk.Label(frm, text="You can try http://interactive.blockdiag.com/ if you can be sure it is safe to open.").grid(column=1, row=5)
     ttk.Label(frm, text="Enter 'graphviz' to use grpahviz locally instead of a remote resource.").grid(column=1, row=6)
     ttk.Button(frm, text="OK", command=partial(ProcessUrlInput,subWindow,theText,cProjectID,cServerName,mainWindow,strBaseURLParam,clFunctionalBlocksAndFlows,bIsDemoRun,cImageFolder)).grid(column=3, row=7)
     subWindow.mainloop()

 


def render_diagram(cProjectID,cServerName,mainWindow,strBaseURLParam, clFunctionalBlocksAndFlows=[], bIsDemoRun = False, cImageFolder=''):
     if len(clFunctionalBlocksAndFlows) != 0:
         bDemoRun = True
     else:
         bDemoRun = bIsDemoRun
         
     strRenderingURL = '' # Could be http://interactive.blockdiag.com/, if that site exists and is safe to use by the time of running this code
     mainWindow.config(cursor="watch")
     sleep(0.1)
     mainWindow.update()
     sleep(0.1)
     if strBaseURLParam.get() != '':
         strRenderingURL = strBaseURLParam.get()
     if strRenderingURL == '':
         askForBaseUrl(cProjectID,cServerName,mainWindow,strBaseURLParam,clFunctionalBlocksAndFlows,bDemoRun,cImageFolder)
     else:
         if len(clFunctionalBlocksAndFlows) == 0:
             bSuccess, cErrorMsg, clFunctionalBlocksAndFlows = read_functional_architecture(cProjectID,cServerName)
         else:
             bSuccess = True
             
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

                         
             if strRenderingURL == 'graphviz':
                 bGraphViz = True
             else:
                 bGraphViz = False
                 
             cDiag = ''
             cNewLine = '\n'
             if bGraphViz:
                cDiag = cDiag + 'digraph {node [shape=box margin=0.1];' 
             else:
                cDiag = cDiag + 'blockdiag {' + cNewLine
             cSpace = '  '
             if bGraphViz == False:
                 if len(clNormalizedBlocksAndFlows) < len(clFunctionalBlocksAndFlows):
                     # Some flows are labled with multiple items. The font size needs to be reduced
                     cDiag = cDiag + cSpace + 'default_fontsize = 3' + cNewLine
                 else:
                     cDiag = cDiag + cSpace + 'default_fontsize = 5' + cNewLine
             for cLine in clNormalizedBlocksAndFlows: 
                 cDiagLine = ''             
                 if len(cLine.get('target_to_source_flows'))>0:
                     #Flows in both directions exist
                     if bGraphViz:
                         cLabelPrefix = '<<table cellpadding="3" border="0" cellborder="0"><tr><td>'
                         cLabelPostfix = '&nbsp;&nbsp;&nbsp;</td></tr></table>>'
                         cDiagLine = wrapNameInCorrectQuotesForGraphViz(cLine.get('source'))   + ' -> ' + wrapNameInCorrectQuotesForGraphViz(cLine.get('target'))   + ' [label = '+cLabelPrefix + cLine.get('source_to_target_flows') + cLabelPostfix + ' ];'                
                         cDiagLine = cDiagLine + wrapNameInCorrectQuotesForGraphViz(cLine.get('target'))   + ' -> ' + wrapNameInCorrectQuotesForGraphViz(cLine.get('source'))   + ' [label = ' +cLabelPrefix + cLine.get('target_to_source_flows') + cLabelPostfix +' ];'                
                     else:
                         cItemDefinitionName = cLine.get('target_to_source_flows') + '   <-->   ' + cLine.get('source_to_target_flows')
                         cDiagLine = wrapNameInCorrectQuotes(cLine.get('source'))  + ' <-> ' + wrapNameInCorrectQuotes(cLine.get('target'))   + ' [label = "' + cItemDefinitionName + '" ]'                
                 else:
                     cItemDefinitionName = cLine.get('source_to_target_flows')
                     if bGraphViz:      
                         cDiagLine = wrapNameInCorrectQuotesForGraphViz(cLine.get('source')) + ' -> '  + wrapNameInCorrectQuotesForGraphViz(cLine.get('target'))   + ' [label = "' + cItemDefinitionName + '" ];'                
                     else:                         
                         cDiagLine = wrapNameInCorrectQuotes(cLine.get('source')) + ' -> '  + wrapNameInCorrectQuotes(cLine.get('target'))   + ' [label = "' + cItemDefinitionName + '" ]'                
                    

                 if bGraphViz:
                     cDiag = cDiag + cDiagLine
                 else:
                     cDiag = cDiag + cSpace + cDiagLine  + cNewLine

             cDiag = cDiag + '}'  
             if bGraphViz == False:
                 cDiag = cDiag + cNewLine
 


             encoded = base64.b64encode(zlib.compress(bytes(cDiag, "utf-8"))).decode("ascii")
             cURL = strRenderingURL + 'image?compression=deflate&encoding=base64&src=' + encoded.replace('/','_').replace('+','-')

             if bGraphViz:
                 sCmd = "echo '" + cDiag + "' | dot -Tsvg  > " + cImageFolder + "output.svg"
                 print ('     Executing ' + sCmd)
                 os.system(sCmd)
                 webbrowser.open_new(cImageFolder + 'output.svg')
             else:
                 
                 print('     Opening ' + cURL)
                 mainWindow.config(cursor="")
             
                 webbrowser.open_new(cURL)
             if bDemoRun:
                 mainWindow.destroy()                 

     if bDemoRun == False:
         mainWindow.config(cursor="arrow")

def run_renderer(cProjectUUID, cHost, cFolder):
     mainWindow = Tk()
     mainWindow.title("Diagram Renderer")
     frm = ttk.Frame(mainWindow)
     frm.grid(row=0, column=0, columnspan=3)

     ttk.Label(frm, text="Model information will be read from the repository and displayed graphically.").grid(column=0, row=0)
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
     bShowBlockdiag = True
     bShowImage=True
     bSuccess = True
     if cProjectUUID!='' and cHost!='':
         bShowImage=False
         bShowBlockdiag = False
         vPartUsages=run_query_for_elementtyp('PartUsage', cHost, cProjectUUID)
         if len(vPartUsages) > 0:
             bShowBlockdiag = True
         vLiterals=run_query_for_elementtyp('LiteralString', cHost, cProjectUUID)
         if len(vLiterals) > 0:
             bShowImage=True             

     if bShowBlockdiag and bShowImage:
         ttk.Button(frm, text="Select", command=partial(selectproject,cProjectID,cServerName)).grid(column=2, row=3)
         ttk.Label(frm, text="").grid(column=0, row=4)
     if bShowBlockdiag:
         strBaseURLParam = StringVar()
         strBaseURLParam.set('')
         ttk.Button(frm, text="Render block diagram", command=partial(render_diagram,cProjectID,cServerName,mainWindow,strBaseURLParam,[],False,cFolder)).grid(column=1, row=5)
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
