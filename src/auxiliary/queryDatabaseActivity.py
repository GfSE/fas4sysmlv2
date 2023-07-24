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
        if iCount ==6:
            iResult = int(currentLine.strip())
    os.remove(cInfoFile)
    os.rmdir(cWorkingFolder)
    return iResult

iInitialEntities=query_sql_entities() #These will be subtracted from all query results, because they are not from the current monitoring session.
print('Database read / write operations executed:')
while True:
    update_entities_committed(query_sql_entities()-iInitialEntities)
    sleep(1)

