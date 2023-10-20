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

#   This code monitors SQL actitvity inside the Postgres container


import sys
from time import sleep
import os
import tempfile
from math import ceil


def update_entities_committed(iNum):
    iNumForScaling = ceil(iNum/200.0)
    cEntities = 'entities'
    if iNum == 1:
        cEntities = 'entity'

    #sys.stdout.write ('\b'*10000 + '  |' + '#'*iNumForScaling + ' (' +str(iNum) + ' ' + cEntities + ')' )
    sys.stdout.write ('\b'*10000 + '  |' + '#'*iNumForScaling  )
    sys.stdout.flush()
 
def end_progress_indicator():
    sys.stdout.write('\r\n')
    sys.stdout.flush()

def query_sql_entities():
    iResult = 0
    cWorkingFolder=tempfile.mkdtemp()
    cInfoFile = os.path.join(cWorkingFolder,'db_entities.txt')


    cCommand = 'docker exec -i -t sysml2-postgres psql -P pager=off -U postgres -d sysml2 --command "SELECT tup_inserted FROM pg_stat_database WHERE datname=' +chr(39) + 'sysml2' + chr(39) + ';"'

    os.system(cCommand + ' > ' + cInfoFile)
    FID = open(cInfoFile,'r')
    lines=FID.readlines()
    FID.close()
    iCount = 0
    for currentLine in lines:
        iCount = iCount + 1
        if iCount ==3 and currentLine.find('tup')==-1 and  currentLine.find('---')==-1  and currentLine.find('row')==-1 :
            iResult = int(currentLine.strip())
        if iCount ==6 and iResult == 0:
            iResult = int(currentLine.strip())
    os.remove(cInfoFile)
    os.rmdir(cWorkingFolder)
    return iResult

iInitialEntities=query_sql_entities() #These will be subtracted from all query results, because they are not from the current monitoring session.
print('Database read / write operations executed:')
while True:
    update_entities_committed(query_sql_entities()-iInitialEntities)
    sleep(1)

