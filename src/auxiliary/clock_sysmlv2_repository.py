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

#   This code performs stress tests and clocks repository response times
#   It runs on bare python to enable running it in the back-end

import sys
import os
import platform
import requests 
import json
import uuid
from datetime import datetime
sys.path.insert(1,os.getcwd().replace('auxiliary','core'))
from fas4sysmlv2API_helpers import *
from time import *
 

print('NumElementsInput;NumElementsReadByQuery;Len;Commit time / s;Read time / s;Project ID')
cServerName="http://localhost:9000"


for iNumParts in [10, 1000, 5000]:
         if cServerName != '':
                timestamp = datetime.now()
                project_name = f"Test Project  - {timestamp}"
                response = requests.post(cServerName + "/projects", headers={"Content-Type": "application/json"}, data=json.dumps({"name":project_name}))
                if response.status_code!=200:
                    print('FAILED to create project')
                targetProjectID=response.json().get('@id')
                payloadArray = []

                commitStart = time()
                for iPartNo in range(iNumParts):
                    cPackageName = 'MyPackage' + str(iPartNo+1)
                    cPartName = 'MyPart' + str(iPartNo+1)
                    part_element_id = str(uuid.uuid4())
                    package_element_id = str(uuid.uuid4())
                    owningmembership_element_id = str(uuid.uuid4())
                    payloadArray.append(dictionary_payload_package(package_element_id, cPackageName , cPartName))
                    payloadArray.append(dictionary_payload_partusage(part_element_id, cPartName, cPartName))
                    payloadArray.append(dictionary_payload_owningmembership(owningmembership_element_id, {'@id': part_element_id}, part_element_id, {'@id': part_element_id}, part_element_id, {'@id': part_element_id}, '', {'@id': package_element_id}))
                    if len(payloadArray) > 1999:
                        #Commit in chunks if payload gets too large
                        commit_body =  '{"change": ' + json.dumps(payloadArray) +'}'
                        payloadArray = []
                        commit_url = f"{cServerName}/projects/{targetProjectID}/commits" 
                        response = requests.post(commit_url, 
                                      headers={"Content-Type": "application/json"}, 
                                      data=commit_body)

 
                commit_body =  '{"change": ' + json.dumps(payloadArray) +'}'
                commit_url = f"{cServerName}/projects/{targetProjectID}/commits" 

                response = requests.post(commit_url, 
                                      headers={"Content-Type": "application/json"}, 
                                      data=commit_body)

                commitEnd = time()
                if response.status_code!=200:
                    print('FAILED to commit to project')
                    print (response.json())

         if cServerName == '':
            print('Could not determine server name')
         else:
            bSuccess = True
            if len(targetProjectID) > 0:
                 cErrorMessage = ''
                 cProjectID=targetProjectID
                 
                
                 try:
                     response = requests.get(cServerName + "/projects/" + cProjectID)
                 except  requests.exceptions.ConnectionError:
                     bSuccess = False
                     cErrorMessage = 'Error: Could not connect to server'
                     print(cErrorMessage)

                     
                 if bSuccess and str(response)!='<Response [200]>':
                     bSuccess = False
                     cErrorMessage = 'Error: Could not find project on stated host'
                     print('Error: Could not find project on stated host')

                 



                 if bSuccess:
                     readStart = time()
                     iCounterQuery = 0

                     data = run_query_for_elementtyp('OwningMembership', cServerName, cProjectID)
                     #print(data)
                     for response in data:
                         if response.get("@type") == 'OwningMembership':
                             iCounterQuery = iCounterQuery + 1
                     
                     
                     readEnd=time()
                     print(str(iNumParts)+';'+str(iCounterQuery)+';' +str(len(str(data)))  +';' +str(commitEnd-commitStart) + ';' + str(readEnd-readStart) + ';' + cProjectID     )
                     if iNumParts != iCounterQuery :
                         print('FAILED')                







