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
#   This is the main py file of the FAS plugin for SysML v2
#   When calling as a script, pass the project ID as an optional first parameter


from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from functools import partial
import sys


import requests 


def fas_transform(cProjectID,cServerName):
     print(cProjectID.get())
     print(cServerName.get())
     messagebox.showwarning("FAS Plugin","fas_transform is not yet implemented")

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
         response = requests.get(cServerName.get() + "/projects")
         data = response.json()
         for response in data:
             tdata.append(response.get("name") + " (" + response.get("@id") + ")" )
     except  requests.exceptions.ConnectionError:
         cProjectID.set("Cannot connect to server.")
     
     if len(tdata)>0:
         listWindow = Tk()
         listWindow.title("FAS Plugin - Project Selection")
         frm = ttk.Frame(listWindow)
         frm.grid(row=0, column=0, columnspan=4)
         ttk.Label(frm, text="Select project").grid(column=0, row=0)
         theCombo=ttk.Combobox(frm, values=tdata, width = 100)
         theCombo.grid(column=1, row=1)
         ttk.Button(frm, text="OK", command=partial(processProjectSelection,listWindow,theCombo,cProjectID)).grid(column=3, row=2)
         ttk.Button(frm, text="Cancel", command=listWindow.destroy).grid(column=2, row=2)

         listWindow.mainloop()   
         
def run_fas4sysml(cProjectUUID):
     mainWindow = Tk()
     mainWindow.title("FAS Plugin")
     frm = ttk.Frame(mainWindow)
     frm.grid(row=0, column=0, columnspan=3)

     ttk.Label(frm, text="FAS Plugin for SysML v2").grid(column=0, row=0)
     cProjectID = StringVar()
     cProjectID.set(cProjectUUID)
     cServerName = StringVar()
     cServerName .set('http://localhost:9000')
     ttk.Label(frm, text="").grid(column=0, row=1)
     ttk.Label(frm, text="Server").grid(column=0, row=2)
     ttk.Entry(frm, textvariable = cServerName, width = 50).grid(column=1, row=2)
     ttk.Label(frm, text="Project UUID").grid(column=0, row=3)
     ttk.Entry(frm, textvariable = cProjectID, width = 50).grid(column=1, row=3)
     ttk.Button(frm, text="Select", command=partial(selectproject,cProjectID,cServerName)).grid(column=2, row=3)
     ttk.Label(frm, text="").grid(column=0, row=4)
     ttk.Button(frm, text="Run FAS transformation", command=partial(fas_transform,cProjectID,cServerName)).grid(column=1, row=5)
     ttk.Button(frm, text="Quit", command=mainWindow.destroy).grid(column=2, row=5)
     mainWindow.mainloop()

def main():
     cProjectID = ''
     if len (sys.argv)>1:
         cProjectID=sys.argv[1]
     run_fas4sysml(cProjectID)

if __name__ == "__main__":
     main()
