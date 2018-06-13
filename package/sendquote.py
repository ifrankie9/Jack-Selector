# -*- coding: utf-8 -*-
#ICON CREDIT TO Flaticon Basic License.
#Copyright © <2017>  <DUFF-NORTON INC>  ALL RIGHTS RESERVED.
#This file is part of Duff Jack Selector.
#Duff Jack Selector is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 

import win32com.client as win32
from win32com.client import Dispatch, constants
import os
import sys
import psutil
import subprocess
from os.path import basename
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
import qrc_resources

class SendQuote(QDialog):

    def __init__(self, parent=None):
        super(SendQuote, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setAttribute(Qt.WA_GroupLeader)
        self.setStyleSheet("""QToolBar {
         background-color: white;
        }""")

        # Create model
        self.countrymodel = QSqlTableModel()
        self.countrymodel.setTable("country_name_list")
        self.countrymodel.select()

        self.statemodel = QSqlTableModel()
        self.statemodel.setTable("state_name_list")
        self.statemodel.select()

        self.firstNameLabel = QLabel("First Name: <font color='red'>*")
        self.firstNameLineEdit = QLineEdit()
        self.lastNameLabel = QLabel("Last Name: <font color='red'>*")
        self.lastNameLineEdit = QLineEdit()
        namerx = QRegExp("[a-z-A-Z ]+")
        namevali = QRegExpValidator(namerx)
        self.firstNameLineEdit.setValidator(namevali)
        self.lastNameLineEdit.setValidator(namevali)
        self.companyLabel = QLabel("Company: <font color='red'>*")
        self.companyLineEdit = QLineEdit()
        self.address1Label = QLabel("Address: <font color='red'>*")
        self.address1LineEdit = QLineEdit()
        self.address2Label = QLabel("Address2: ")
        self.address2LineEdit = QLineEdit()
        self.cityLabel = QLabel("City: <font color='red'>*")
        self.cityLineEdit = QLineEdit()
        self.countryLabel = QLabel("Country: <font color='red'>*")
        self.countryComboBox = QComboBox()
        self.countryComboBox.setModel(self.countrymodel)
        self.countryComboBox.setModelColumn(\
            self.countrymodel.fieldIndex("name"))
        self.connect(self.countryComboBox,SIGNAL("activated(int)"),
                     self.comboBoxUpdate)
        self.stateLabel = QLabel("State/Province: <font color='red'>*")   
        self.stateLineEdit = QLineEdit()
        self.stateLineEdit.setPlaceholderText("Please Enter...")
        self.stateLineEdit.hide()
        self.stateComboBox = QComboBox()
        self.stateComboBox.setModel(self.statemodel)
        self.stateComboBox.setModelColumn(self.statemodel.fieldIndex("name"))
        self.zipcodeLabel = QLabel("Zip/Postal code: <font color='red'>*")
        self.zipcodeLineEdit = QLineEdit()
        self.emailLabel = QLabel("Email: <font color='red'>*")
        self.emailLineEdit = QLineEdit()
        emailrx = QRegExp("^[A-Za-z0-9_\+-]+(\.[A-Za-z0-9_\+-]+)*@[A-Za-z0-9-]"
                          "+(\.[A-Za-z0-9-]+)*\.([A-Za-z]{2,4})$")
        emailvali = QRegExpValidator(emailrx)
        self.emailLineEdit.setValidator(emailvali)
        self.phoneLabel = QLabel("Phone: <font color='red'>*")
        self.phoneLineEdit = QLineEdit()
        self.faxLabel = QLabel("Fax: ")
        self.faxLineEdit = QLineEdit()
        self.commentLabel = QLabel("Special Instructions:"
                                   "<font color='red'>*")
        self.commentTextBox = QPlainTextEdit()

        self.warmLabel = QLabel("<b><font color='red'>"
                                "  *Please fill all highlighted fields</b>")
        self.warmLabel.hide()
        self.uploadLabel1 = QLabel("<i><font color='red'>"
                                "*Successfully uploaded!</i>")
        self.uploadLabel1.hide()
        self.uploadLabel2 = QLabel("<i><font color='red'>"
                                "*Successfully uploaded!</i>")
        self.uploadLabel2.hide()
        self.uploadButton1 = QPushButton("Upload File - Attachment 1 ")
        self.uploadButton2 = QPushButton("Upload File - Attachment 2 ")
        self.connect(self.uploadButton1,SIGNAL("clicked()"),
                     self.openUpload1)
        self.connect(self.uploadButton2,SIGNAL("clicked()"),
                     self.openUpload2)

        self.upcheck1 = False
        self.upcheck2 = False

        #layout
        inputLayout = QGridLayout()
        inputLayout.addWidget(self.firstNameLabel, 0, 0)
        inputLayout.addWidget(self.firstNameLineEdit, 0, 1)
        inputLayout.addWidget(self.lastNameLabel, 1, 0)
        inputLayout.addWidget(self.lastNameLineEdit, 1, 1)
        inputLayout.addWidget(self.companyLabel, 2, 0)
        inputLayout.addWidget(self.companyLineEdit, 2, 1)
        inputLayout.addWidget(self.address1Label, 3, 0)
        inputLayout.addWidget(self.address1LineEdit, 3, 1)
        inputLayout.addWidget(self.address2Label, 4, 0)
        inputLayout.addWidget(self.address2LineEdit, 4, 1)
        inputLayout.addWidget(self.cityLabel, 5, 0)
        inputLayout.addWidget(self.cityLineEdit, 5, 1)
        inputLayout.addWidget(self.countryLabel, 6, 0)
        inputLayout.addWidget(self.countryComboBox, 6, 1)
        inputLayout.addWidget(self.stateLabel, 7, 0)
        inputLayout.addWidget(self.stateComboBox, 7, 1)
        inputLayout.addWidget(self.stateLineEdit, 8, 1)
        inputLayout.addWidget(self.zipcodeLabel, 9, 0)
        inputLayout.addWidget(self.zipcodeLineEdit, 9, 1)
        inputLayout.addWidget(self.emailLabel, 10, 0)
        inputLayout.addWidget(self.emailLineEdit, 10, 1)
        inputLayout.addWidget(self.phoneLabel, 11, 0)
        inputLayout.addWidget(self.phoneLineEdit, 11,  1)
        inputLayout.addWidget(self.faxLabel, 12, 0)
        inputLayout.addWidget(self.faxLineEdit, 12, 1)
        inputLayout.addWidget(self.commentLabel, 13, 0)
        inputLayout.addWidget(self.commentTextBox, 13, 1)
        inputLayout.addWidget(self.warmLabel, 14, 1)
        inputLayout.addWidget(self.uploadLabel1, 15, 0)
        inputLayout.addWidget(self.uploadButton1, 15, 1)
        inputLayout.addWidget(self.uploadLabel2, 16, 0)
        inputLayout.addWidget(self.uploadButton2, 16, 1)

        self.lineEditFields = [self.firstNameLineEdit,
                               self.lastNameLineEdit,
                               self.companyLineEdit,
                               self.address1LineEdit,
                               self.cityLineEdit,
                               self.zipcodeLineEdit,
                               self.phoneLineEdit,
                               self.emailLineEdit]

        for item in self.lineEditFields:
            item.setStyleSheet('QLineEdit { background-color: #fff79a }')
            item.textChanged.connect(self.lineEditColor)
        
        emailAction = QAction(QIcon(":/email.png"),
                              "&Send Email", self)
        emailAction.setShortcut("Email")
        self.pageLabel = QLabel("<b>Send Quote     </b>")

        toolBar = QToolBar()
        toolBar.addWidget(self.pageLabel)
        toolBar.addAction(emailAction)
        self.textBrowser = QTextBrowser()
        layout = QVBoxLayout()
        layout.addWidget(toolBar)
        layout.addLayout(inputLayout)
        self.setLayout(layout)

        self.connect(emailAction, SIGNAL("triggered()"),
                     self.checktoSendEmail)

        self.textBrowser.setSearchPaths(["./quote"])
        self.resize(320, 580)
        self.setWindowTitle("Request A Quote")

        self.checkSend = False

        for item in psutil.pids():
            p = psutil.Process(item)
            if p.name() == "OUTLOOK.EXE":
                flag = 1
                break
            else:
                flag = 0

        if (flag == 1):
            self.checktoSendEmail()
        else:
            #self.open_outlook()
            os.startfile("outlook")
            self.checktoSendEmail()

    def lineEditColor(self):
        #define block write changes
        sender = self.sender()
        if sender.text().isEmpty():
            sender.setStyleSheet('QLineEdit { background-color: #fff79a }')
        else:
            sender.setStyleSheet('QLineEdit { background-color: #c4df9b }')


    def comboBoxUpdate(self):
        #show state depends on country name
        country = str(self.countryComboBox.currentText())
        if country == "United States":
            self.stateComboBox.show()
            self.stateLineEdit.hide()
            self.stateLineEdit.clear()
        elif country not in ("United States", "- Select -"):
            self.stateLineEdit.show()
            self.stateComboBox.hide()
            self.stateComboBox.setCurrentIndex(0)

    def return_strings(self):
        #   Return list of values. 
        return map(str, [self.edit_first.text(), self.edit_second.text()])


    def checktoSendEmail(self):
        if len(self.firstNameLineEdit.text()) > 0 and\
           len(self.lastNameLineEdit.text()) > 0 and\
           len(self.companyLineEdit.text()) > 0 and\
           len(self.address1LineEdit.text()) > 0 and\
           len(self.cityLineEdit.text()) > 0 and\
           len(self.zipcodeLineEdit.text()) > 0 and\
           len(self.phoneLineEdit.text()) > 0 and\
           len(self.emailLineEdit.text()) > 0 and\
           len(self.commentTextBox.toPlainText()) > 0 and\
           self.countryComboBox.currentText() <> "- Select -":
            self.warmLabel.hide()
            self.sendEmail()
        else:
            self.warmLabel.show()

    def openUpload1(self):
        self.filename1 = QFileDialog.getOpenFileName(self, 'Open File')
        if self.filename1:
            self.uploadLabel1.show()
            self.upcheck1 = True

    def openUpload2(self):
        self.filename2 = QFileDialog.getOpenFileName(self, 'Open File')
        if self.filename2:
            self.uploadLabel2.show()
            self.upcheck2 = True
    
    def sendEmail(self):
        #EMAIL Contains
        firstName = unicode(self.firstNameLineEdit.text())
        lastName = self.lastNameLineEdit.text()
        company = self.companyLineEdit.text()
        address1 = self.address1LineEdit.text()
        address2 = self.address2LineEdit.text()
        city = self.cityLineEdit.text()
        zipcode = self.zipcodeLineEdit.text()
        email = self.emailLineEdit.text()
        statetext = self.stateLineEdit.text()
        statecombo = self.stateComboBox.currentText()
        country = self.countryComboBox.currentText()
        phone = self.phoneLineEdit.text()
        fax = self.faxLineEdit.text()
        comment = self.commentTextBox.toPlainText()

        if country == "United States":
            mail_contain = """<h1>Request Quote</h1>
              <h3>Send from - Duff Norton Jack Selector App<h3>
              <table>
              <tr><td align=left>First Name: </td>
              <td colspan=2><b>%s</b></td></tr>
              <tr><td align=left>Last Name: </td>
              <td colspan=2><b>%s</b></td></tr>
              <tr><td align=left>Company: </td>
              <td><b>%s</b></td></tr>
              <tr><td align=left>Address1: </td>
              <td><b>%s</b></td></tr>
              <tr><td align=left>Address2: </td>
              <td><b>%s</b></td></tr>
              <tr><td align=left>City: </td>
              <td><b>%s</b></td></tr>
              <tr><td align=left>Country: </td>
              <td><b>%s</b></td></tr>
              <tr><td align=left>State/Province:</td>
              <td><b>%s</b></td></tr>
              <tr><td align=left>Zip/Postal Code:</td>
              <td><b>%s</b></td></tr>
              <tr><td align=left>Email: </td>
              <td><b>%s</b></td></tr>
              <tr><td align=left>Phone: </td>
              <td><b>%s</b></td></tr>
              <tr><td align=left>Fax: </td>
              <td><b>%s</b></td></tr>
              <tr><td align=left>Special Instructions:</td>
              <td><b>%s</b></td></tr>
              </table>"""\
              % (firstName, lastName, company, address1, address2, city,
                 country, statecombo, zipcode, email, phone, fax, comment)
        else:
            mail_contain = """<h1>Request Quote</h1>
              <table>
              <tr><td align=left>First Name: </td>
              <td colspan=2><b>%s</b></td></tr>
              <tr><td align=left>Last Name: </td>
              <td colspan=2><b>%s</b></td></tr>
              <tr><td align=left>Company: </td>
              <td><b>%s</b></td></tr>
              <tr><td align=left>Address1: </td>
              <td><b>%s</b></td></tr>
              <tr><td align=left>Address2: </td>
              <td><b>%s</b></td></tr>
              <tr><td align=left>City: </td>
              <td><b>%s</b></td></tr>
              <tr><td align=left>Country: </td>
              <td><b>%s</b></td></tr>
              <tr><td align=left>State/Province:</td>
              <td><b>%s</b></td></tr>
              <tr><td align=left>Zip/Postal Code:</td>
              <td><b>%s</b></td></tr>
              <tr><td align=left>Email: </td>
              <td><b>%s</b></td></tr>
              <tr><td align=left>Phone: </td>
              <td><b>%s</b></td></tr>
              <tr><td align=left>Fax: </td>
              <td><b>%s</b></td></tr>
              <tr><td align=left>Special Instructions:</td>
              <td><b>%s</b></td></tr>
              </table>"""\
              % (firstName, lastName, company, address1, address2, city,
                 country, statetext, zipcode, email, phone, fax, comment)

        outlook = win32.Dispatch('outlook.application')
        mail = outlook.CreateItem(0)
        mail.To = 'duffnorton@cmworks.com'
        #mail.CC = "moreaddresses here"
        #mail.BCC = "address"
        mail.Subject = 'Request A Quote - From App User'
        mail.HTMLBody = mail_contain
        
        if self.upcheck1 == True:
            attachment1 = str(self.filename1)
            mail.Attachments.Add(attachment1)
        if self.upcheck2 == True:
            attachment2 = str(self.filename2)
            mail.Attachments.Add(attachment2)
        mail.Send()
        self.close()


def open_outlook():
    try:
        subprocess.call([\
            'C:\Program Files\Microsoft Office\Office15\Outlook.exe'])
        os.system("C:\Program Files\Microsoft Office\Office15\Outlook.exe");
    except:
        print("Outlook didn't open successfully")
 
       

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    form = SendQuote()
    form.show()
    app.exec_()
