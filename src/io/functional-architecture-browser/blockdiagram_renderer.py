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

#TODO
#The following functions need to be placed in a common module, if they keep being shared with fas4sysmlv2_main.py
  

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
         listWindow.title("Block Diagram Renderer - Project Selection")
         frm = ttk.Frame(listWindow)
         frm.grid(row=0, column=0, columnspan=4)
         ttk.Label(frm, text="Select project").grid(column=0, row=0)
         theCombo=ttk.Combobox(frm, values=tdata, width = 100)
         theCombo.grid(column=1, row=1)
         ttk.Button(frm, text="OK", command=partial(processProjectSelection,listWindow,theCombo,cProjectID)).grid(column=3, row=2)
         ttk.Button(frm, text="Cancel", command=listWindow.destroy).grid(column=2, row=2)

         listWindow.mainloop()   

### END TODO



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
                    clFunctionalBlocksAndFlows.append(clPair[0] + ' -> ' +   clPair[1] + ' [label = ' + cItemDefinitionName + ' ]')
         
         return bSuccess, cErrorMessage, clFunctionalBlocksAndFlows




def render_diagram(cProjectID,cServerName):
     bSuccess, cErrorMsg, clFunctionalBlocksAndFlows = read_functional_architecture(cProjectID,cServerName)
     if bSuccess == False:
         messagebox.showerror("Diagram Renderer","Reading from the repository failed with the following error message: " + cErrorMsg)
     else:
         cDiag = ''
         cNewLine = '\n'
         cDiag = cDiag + 'blockdiag {' + cNewLine
         cSpace = '  '
         cDiag = cDiag + cSpace + 'default_fontsize = 5' + cNewLine
         for cLine in clFunctionalBlocksAndFlows: 
             cDiag = cDiag + cSpace + cLine  + cNewLine

         cDiag = cDiag + '}'  + cNewLine

         print('------------------------------------------')
         print('')
         print(cDiag)
         print('')
         print('------------------------------------------')


         encoded = base64.b64encode(zlib.compress(bytes(cDiag, "utf-8"))).decode("ascii")
         cURL = 'http://interactive.blockdiag.com/image?compression=deflate&encoding=base64&src=' + encoded.replace('/','_').replace('+','-')

         print('Opening ' + cURL)
         
         webbrowser.open_new(cURL)


def run_renderer(cProjectUUID, cHost):
     mainWindow = Tk()
     mainWindow.title("Block Diagram Renderer")
     frm = ttk.Frame(mainWindow)
     frm.grid(row=0, column=0, columnspan=3)

     ttk.Label(frm, text="WARNING: Before running, please check that http://blockdiag.com/ still exists").grid(column=0, row=0)
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
     ttk.Button(frm, text="Render block diagram", command=partial(render_diagram,cProjectID,cServerName)).grid(column=1, row=5)
     ttk.Button(frm, text="Quit", command=mainWindow.destroy).grid(column=2, row=5)
     mainWindow.mainloop()


def main():

     cProjectID = ''
     cHost = 'http://localhost:9000'
     if len (sys.argv)>1:
         cProjectID=sys.argv[1]
     if len (sys.argv)>2:
         cHost=sys.argv[2]
     run_renderer(cProjectID,cHost)


if __name__ == "__main__":
     main()
