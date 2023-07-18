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

import platform
import os

def run_freesketchplugin(cFreesketchFolderName, cModelElementName):
    cPluginName = "Free Sketch Plugin by IPEK - Institute of Product Engineering at Karlsruhe Institute of Technology (KIT)"

    cSources = '.\\MainClass.java .\\com\\nomagic\\actions\\ActionsCategory.java .\\com\\nomagic\\actions\\NMAction.java .\\com\\nomagic\\magicdraw\\actions\\ActionsConfiguratorsManager.java .\\com\\nomagic\\magicdraw\\core\\Application.java .\\com\\nomagic\\magicdraw\\core\\myInstance.java .\\com\\nomagic\\magicdraw\\core\\myProject.java .\\com\\nomagic\\magicdraw\\ui\\dialogs\\MDDialogParentProvider.java .\\de\\gfse\\RealMainClass.java .\\global\\DataSerializer.java .\\global\\DataSerializer4Trace.java .\\global\\DataTree.java .\\rectangledesign\\BottomPanel.java .\\rectangledesign\\CenterPanel.java .\\rectangledesign\\Controller.java .\\rectangledesign\\LeftPanel.java .\\rectangledesign\\Shapes.java .\\rectangledesign\\TopPanel.java'

    cSourceFolders = '.\\com\\nomagic\\magicdraw\\core\\;.\\de\\gfse\\'

    bSilenced=False
    if platform.system()!='Windows':
         cSilencer='2>/dev/null'
         cSources = cSources.replace('\\','/')
         cSourceFolders = cSourceFolders.replace('\\','/').replace(';',':')
    else:
         cSilencer='>nul 2>&1'

    cFreesketchFolderName=cFreesketchFolderName.replace('\\\\','{}').replace('\\','').replace('{}','\\')
    if platform.system()!='Windows':
        clCommands=['`update-alternatives --list javac|grep "/jdk"|head -n 1`' +' -cp "gson.jar:imageplugin.jar" ' + cSources , 
                    '`update-alternatives --list java|grep "/jdk"|head -n 1`' + ' -cp ' + cSourceFolders + ':.:"gson.jar":"imageplugin.jar" MainClass "' + cFreesketchFolderName + '" "' + cModelElementName + '" \'' + cPluginName+ '\'']
    else:
        clCommands=['javac -cp "gson.jar;imageplugin.jar" ' + cSources ,
                    'java -cp ' + cSourceFolders + ';.;"gson.jar";"imageplugin.jar"  MainClass "' + cFreesketchFolderName + '" "' + cModelElementName + '" "' + cPluginName+ '"']

    for cCommand in clCommands:
         if bSilenced:
             cCommand = cCommand + ' ' + cSilencer
         if platform.system()!='Windows':
             os.system('/bin/bash -c "'+ cCommand +'"')
         else:
             os.system(cCommand)
