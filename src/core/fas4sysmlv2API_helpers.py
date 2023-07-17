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
#   This is an include file of the FAS plugin for SysML v2 for helping with the handling of the SysML v2 REST API.
#

import requests
import json
import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from functools import partial


def format_servername(cName):
     if len(cName)>0:
         if cName[len(cName)-1] == '/':
            cName = cName[0:(len(cName)-1)]
         
         if cName.find('http') == -1:
            cName = 'http://' + cName
     
     return cName
  

def read_full_repository(cServerName, cProjectID):
# This function has been created to demonstrate the handling
# of multiple HTML response pages.
#
# Normally, this function should not be used, but queries 
# for subsets of the repository should be used instead.
     bSuccess = True
     data = []
     try:
         response = requests.get(cServerName + "/projects/" + cProjectID)
     except  requests.exceptions.ConnectionError:
         bSuccess = false
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


     if bSuccess:
         response = requests.get(cServerName + "/projects/" + cProjectID + "/commits/"+sHeadCommit+"/elements")
         data = response.json()

         # Handle next pages of mutlti-page HTML responses (when the payload is very large)
         while response.headers.get('Link','--NOTFOUND--').find('?page[after]')>-1:
            cNextPageLink = response.headers.get('Link').replace('<','').replace('; rel="next"','').replace('; rel="prev"','').replace('page[size]=100>','page[size]=10000>').replace('>','')
            response = requests.get(cNextPageLink)
            if response.status_code == 200:
                data = data + response.json()

     return data

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
         listWindow.title("Project Selection")
         frm = ttk.Frame(listWindow)
         frm.grid(row=0, column=0, columnspan=4)
         ttk.Label(frm, text="Select project").grid(column=0, row=0)
         theCombo=ttk.Combobox(frm, values=tdata, width = 100)
         theCombo.grid(column=1, row=1)
         ttk.Button(frm, text="OK", command=partial(processProjectSelection,listWindow,theCombo,cProjectID)).grid(column=3, row=2)
         ttk.Button(frm, text="Cancel", command=listWindow.destroy).grid(column=2, row=2)

         listWindow.mainloop() 

def dictionary_payload_partusage(element_id, name = None, quali_name = None, owner = None, owning = None):
    dictionary_payload_partusage = {
        "payload": {
            '@type': 'PartUsage',
            '@id': element_id,
            'elementId': element_id,
            'name': name,
            'owner': owner,
            'owningMembership': owning,
            'owningNamespace': owner,
            'owningRelationship': owning,
            'qualifiedName': quali_name
        },
        "identity": {"@id": element_id}
    }
    return dictionary_payload_partusage

def dictionary_payload_owningmembership(element_id, member_element, memberId, owned_member_element, owned_member_element_id, target, name, owner):
    dictionary_payload_owningmembership = {
        "payload": {'@type': 'OwningMembership',
                    '@id': element_id,
                    'elementId': element_id,
                    'memberElement': member_element,
                    'memberElementId': memberId,
                    'memberName': name,
                    'membershipOwningNamespace': owner,
                    'ownedMemberElement': owned_member_element ,
                    'ownedMemberElementId': owned_member_element_id,
                    'ownedMemberName': name,
                    'ownedRelatedElement': [owned_member_element],
                    'owningRelatedElement': owner,
                    'relatedElement': [owner, owned_member_element],
                    'source': [owner],
                    'target': [target]
                   },
        "identity": {"@id": element_id}
    }
    return dictionary_payload_owningmembership

def dictionary_payload_package(element_id, name = None, quali_name = None, member = None, membership = None ):
    dictionary_payload_package = {
        "payload": {'@type': 'Package',
                    '@id': element_id,
                    'elementId': element_id,
                    'member': member,
                    'membership': membership,
                    'name': name,
                    'ownedElement': member,
                    'ownedMember': member,
                    'ownedMembership': membership,
                    'ownedRelationship': membership,
                    'qualifiedName': quali_name
                   },
        "identity": {"@id": element_id}
    }
    return dictionary_payload_package
