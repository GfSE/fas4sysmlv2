/* #   Copyright 2022 Gesellschaft fuer Systems Engineering e.V. (GfSE)
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
*/

package de.gfse;

import java.awt.BorderLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.File;
import java.util.Map;
import java.util.TreeMap;

import javax.swing.DefaultListModel;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JList;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.ListSelectionModel;


import global.DataSerializer;
import global.DataTree;


import rectangledesign.BottomPanel;
import rectangledesign.CenterPanel;
import rectangledesign.Controller;
import rectangledesign.LeftPanel;
import rectangledesign.Shapes;
import rectangledesign.TopPanel;


public class RealMainClass {
	
  private DataTree tree;
  private DataSerializer dataSerializer;

  private static String modelElementName = "";
  private static String workingFolderName = "";
  
  public String getModelElementName(){return modelElementName;}
  public String getWorkingFolderName(){return workingFolderName;}
	
  public void RealMainClass(){
  }
	
  public  void realmain(String newWorkingFolderName, String newModelElementName, String pluginName){
            this.modelElementName = newModelElementName;
            this.workingFolderName = newWorkingFolderName;

	    JFrame frm = new JFrame(pluginName);
	    frm.setSize(910, 680);
	    frm.setLocationRelativeTo(null);
	    frm.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
            frm.setResizable(false);
	    
	    Controller contr = new Controller(frm);

	    frm.add(new LeftPanel(contr),BorderLayout.LINE_START);
	    frm.add(new TopPanel(contr),BorderLayout.NORTH);
	    frm.add(new CenterPanel(contr), BorderLayout.CENTER);
	    frm.add(new BottomPanel(contr), BorderLayout.SOUTH);
	    
	    frm.setVisible(true);
  }

}