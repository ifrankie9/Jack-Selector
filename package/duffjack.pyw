# -*- coding: utf-8 -*-
#ICON CREDIT TO Flaticon Basic License.
#Copyright © <2017>  <DUFF-NORTON INC>  ALL RIGHTS RESERVED.
#For any information about this program, please contact
#duffnorton@cmworks.com or mail to 9415 Pioneer Ave, Charlotte, NC 28273
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

import os
import platform
import sys
import math
import codecs
import gzip
import webbrowser
import sip
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
import helpform
import sendquote
import qrc_resources

__version__ = "1.0.0"
CODEC = "UTF-8"

X11 = "qt_x11_wait_for_window_manager" in dir()

ID = 0
SELECTION = RESULTID = 1
JACKTYPE = CAPACITY = 2
TRANSLATING = SRATIO = 3
AB = SDIAMETER = 4
KEYED = SROOTDIA = 5
ENDOPTION = SLEAD = 6
CAPACITYNUM = HPTEXT = 7
TRAVELRATE = STORQUEPERLBS = 8
DIAMETER = STORQUENOLOAD = 9
ROOTDIA = STORQUEFULLLOAD = 10
LEAD = STURNSOFWORM = 11
RATIO = 12
HPNUM = 13
TORQUEPERLBS = 14
TORQUENOLOAD = 15
TORQUEFULLLOAD = 16
TORQUEPERJACK = 17
TORQUETOTAL = 18
HPPERJACK = 19
HPTOTAL = 20
MAXINPERHOUR = 21
DUTYCYCLE = 22
TURNSOFWORM = 23
FIXEDFREE = 24
FIXEDGUIDE = 25
PINENDS = 26
SELFLOCKING = 27

ACQUIRED = 1

DATE_FORMAT = "MMMM dd, yyyy"

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
 


class MySqlModel(QSqlRelationalTableModel):
    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        return QSqlTableModel.data(self,index,role)


class AssetDelegate(QSqlRelationalDelegate):

    def __init__(self, parent=None):
        super(AssetDelegate, self).__init__(parent)
        
    def paint(self, painter, option, index):
        myoption = QStyleOptionViewItem(option)
        if index.column() == SELECTION:
            myoption.displayAlignment |= Qt.AlignLeft|Qt.AlignVCenter
        QSqlRelationalDelegate.paint(self, painter, myoption, index)


    def createEditor(self, parent, option, index):
        if index.column() == SELECTION:
            editor = QLineEdit(parent)
            regex = QRegExp(r"(?:0[1-9]|1[0124-9]|2[0-7])"
                            r"(?:0[1-9]|[1-5][0-9]|6[012])")
            validator = QRegExpValidator(regex, parent)
            editor.setValidator(validator)
            editor.setInputMask("9999")
            editor.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
            return editor
        else:
            return QSqlRelationalDelegate.createEditor(self, parent,
                                                       option, index)

    def setEditorData(self, editor, index):
        if index.column() == SELECTION:
            text = index.model().data(index, Qt.DisplayRole).toString()
            editor.setText(text)
        else:
            QSqlRelationalDelegate.setEditorData(self, editor, index)


    def setModelData(self, editor, model, index):
        if index.column() == SELECTION:
            model.setData(index, QVariant(editor.text()))
        else:
            QSqlRelationalDelegate.setModelData(self, editor, model,
                                                index)


class LogDelegate(QSqlRelationalDelegate):

    def __init__(self, parent=None):
        super(LogDelegate, self).__init__(parent)


    def paint(self, painter, option, index):
        myoption = QStyleOptionViewItem(option)
        if index.column() == RATIO:
            myoption.displayAlignment |= Qt.AlignLeft|Qt.AlignVCenter
        QSqlRelationalDelegate.paint(self, painter, myoption, index)


    def createEditor(self, parent, option, index):
        if index.column() == RATIO:
            editor = QDateEdit(parent)
            editor.setMaximumDate(QDate.currentDate())
            editor.setDisplayFormat("yyyy-MM-dd")
            if PYQT_VERSION_STR >= "4.1.0":
                editor.setCalendarPopup(True)
            editor.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
            return editor
        else:
            return QSqlRelationalDelegate.createEditor(self, parent,
                                                       option, index)

    def setEditorData(self, editor, index):
        if index.column() == RATIO:
            date = index.model().data(index, Qt.DisplayRole).toDate()
            editor.setDate(date)
        else:
            QSqlRelationalDelegate.setEditorData(self, editor, index)


    def setModelData(self, editor, model, index):
        if index.column() == RATIO:
            model.setData(index, QVariant(editor.date()))
        else:
            QSqlRelationalDelegate.setModelData(self, editor, model,
                                                index)

class FetchTable(QApplication):
    def __init__(self, mainWindow):
        super(FetchTable, self).__init__()
        while mainWindow.assetModel.canFetchMore():
            mainWindow.assetModel.fetchMore()
        
class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.image = QImage() 
        self.dirty = False
        self.entry = False
        self.filename = None
        self.selector = []
        self.printer = QPrinter()
        self.printer.setPageSize(QPrinter.Letter)
        self.printer.setResolution(QPrinter.HighResolution)
        self.printer.setOutputFormat(QPrinter.PdfFormat)
        
#*                                                                         *
#*                               * TAB 1*                                  *
#*                                                                         *

        #ARRANGEMENT GROUP
        arrangeLabel = QLabel("Number of Jacks")
        self.arrangeComboBox = QComboBox()
        self.arrangeComboBox.addItem("- Select -")
        self.arrangeComboBox.addItem("1")
        self.arrangeComboBox.addItem("2")
        self.arrangeComboBox.addItem("3")
        self.arrangeComboBox.addItem("4")
        self.arrangeComboBox.addItem("6")
        self.arrangeComboBox.addItem("8")
        arrangeGroup = QGroupBox("JACK ARRANGEMENT")
        arrangeLayout = QGridLayout(arrangeGroup)                                  
        arrangeLayout.addWidget(arrangeLabel, 0, 0)
        arrangeLayout.addWidget(self.arrangeComboBox, 0, 1)

        #LOAD GROUP
        dynloadLabel = QLabel("&Dynamic Load:")
        self.dynloadLineEdit = QLineEdit()
        dynloadLabel.setBuddy(self.dynloadLineEdit)
        self.dynloadLineEdit.setPlaceholderText("Number of Lbs. Per Jack")
        staloadLabel = QLabel("&Static Load:")
        self.staloadLineEdit = QLineEdit()
        staloadLabel.setBuddy(self.staloadLineEdit)
        self.staloadLineEdit.setPlaceholderText("Number of Lbs. Per Jack")
        loadGroup = QGroupBox("JACK LOAD")
        loadLayout = QGridLayout(loadGroup)                                  
        loadLayout.addWidget(dynloadLabel, 0, 0)
        loadLayout.addWidget(self.dynloadLineEdit, 0, 1)
        loadLayout.addWidget(staloadLabel, 1, 0)
        loadLayout.addWidget(self.staloadLineEdit, 1, 1)

        #TYPE GROUP
        typeLabel = QLabel("Screw Type:")
        self.acmeRadioButton = QRadioButton("Machine Screw Jack")
        self.ballRadioButton = QRadioButton("Ball Screw Jack")
        screwtypeLayout = QHBoxLayout()
        screwtypeLayout.addWidget(self.acmeRadioButton)
        screwtypeLayout.addWidget(self.ballRadioButton)
        
        self.selflocking = QCheckBox("Check if self-locking is required?")
        self.antibacklash = QCheckBox("Check if Anti-Backlash is required?")
        hideLayout = QVBoxLayout()
        hideLayout.addWidget(self.selflocking)
        self.selflocking.hide()
        hideLayout.addWidget(self.antibacklash)
        self.antibacklash.hide()
        self.acmeRadioButton.clicked.connect(self.showhide)
        self.ballRadioButton.clicked.connect(self.hideshow)
        
        self.configurationLabel = QLabel("Configuration:")
        self.jacktypeLable = QLabel()
        self.jacktypeLable.hide()
        self.configurationComboBox = QComboBox()
        self.configurationComboBox.addItem("- Select -")
        self.configurationComboBox.addItem("Upright")
        self.configurationComboBox.addItem("Inverted")
        self.configurationComboBox.addItem("Upright Rotating")
        self.configurationComboBox.addItem("Inverted Rotating")
        self.configurationComboBox.addItem("Double Clevis")
        self.configurationLabel.setBuddy(self.configurationComboBox)
        self.connect(self.configurationComboBox,
                     SIGNAL("currentIndexChanged(int)"), self.setJackType)
        self.connect(self.configurationComboBox,
                     SIGNAL("activated(int)"), self.setJackType2)

        self.translatingLabel = QLabel("Translating:")
        self.endtypeLabel = QLabel()
        self.endtypeLabel.hide()
        self.translatingComboBox  = QComboBox()
        self.translatingComboBox.addItem("- Select -")
        self.translatingComboBox.addItem("Threaded End")
        self.translatingComboBox.addItem("Top Plate")
        self.translatingComboBox.addItem("Clevis End")
        self.translatingLabel.setBuddy(self.translatingComboBox)
        self.connect(self.translatingComboBox,
                     SIGNAL("currentIndexChanged(int)"),
                     self.setEndTypeImage)

        self.keyoptionLabel =  QLabel("Keyed Options")
        self.keyoptionComboBox = QComboBox()
        self.keyoptionComboBox.addItem("- Select -")
        self.keyoptionComboBox.addItem("Not Keyed")
        self.keyoptionComboBox.addItem("Keyed")
        self.keyoptionLabel.setBuddy(self.keyoptionComboBox)

        self.bearingoptionLabel =  QLabel("Radial Bearing Options")
        self.bearingoptionComboBox = QComboBox()
        self.bearingoptionComboBox.addItem("- Select -")
        self.bearingoptionComboBox.addItem("Free End")
        self.bearingoptionComboBox.addItem("Bearing Support")
        self.bearingoptionLabel.setBuddy(self.bearingoptionComboBox)
        self.bearingoptionLabel.hide()
        self.bearingoptionComboBox.hide()
        
        confitransLayout = QGridLayout()
        confitransLayout.addWidget(self.configurationLabel, 0, 0)
        confitransLayout.addWidget(self.configurationComboBox, 0, 1)
        confitransLayout.addWidget(self.jacktypeLable, 1, 1)
        confitransLayout.addWidget(self.translatingLabel, 2, 0)
        confitransLayout.addWidget(self.translatingComboBox, 2, 1)       
        confitransLayout.addWidget(self.endtypeLabel, 3, 1)
        confitransLayout.addWidget(self.keyoptionLabel, 4, 0)       
        confitransLayout.addWidget(self.keyoptionComboBox, 4, 1)
        confitransLayout.addWidget(self.bearingoptionLabel, 5, 0)       
        confitransLayout.addWidget(self.bearingoptionComboBox, 5, 1)
        
        #DIRECTION GROUP
        self.directionLabel = QLabel()
        self.directionComboBox = QComboBox()
        self.directionComboBox.addItem("- Select -")
        self.directionComboBox.addItem("Tension")
        self.directionComboBox.addItem("Compression")
        self.directionComboBox.addItem("Compression & Tension")
        self.connect(self.directionComboBox, \
                     SIGNAL("currentIndexChanged(int)"),
                     self.setDirImage)
        self.endfixLabel = QLabel()
        self.endfixComboBox = QComboBox()
        self.endfixComboBox.addItem("- Select -")
        self.endfixComboBox.addItem("One end fixed & one end free")
        self.endfixComboBox.addItem("Pinned Ends")
        self.endfixComboBox.addItem("One end fixed & one end guided")
        self.endfixComboBox.hide()
        self.connect(self.directionComboBox,\
                     SIGNAL("currentIndexChanged(int)"),
                     self.showEndCombo)
        self.connect(self.endfixComboBox, SIGNAL("currentIndexChanged(int)"),
                     self.setEndfixImage)
        directionGroup = QGroupBox("LOAD OPTIONS")
        imageLayout = QHBoxLayout()
        imageLayout.addWidget(self.directionLabel)
        imageLayout.addWidget(self.endfixLabel)
        directionLayout = QVBoxLayout(directionGroup)                            
        directionLayout.addWidget(self.directionComboBox)
        directionLayout.addWidget(self.endfixComboBox)
        directionLayout.addLayout(imageLayout)
        #directionLayout.addStretch(1)

        #TRAVEL(SPEED) GROUP
        travelLabel = QLabel("&Total Travel:")
        self.travelLineEdit = QLineEdit()
        travelLabel.setBuddy(self.travelLineEdit)
        self.travelLineEdit.setPlaceholderText("Number in inches")
        self.travelComboBox = QComboBox()
        self.travelComboBox.addItem("inch/min")
        self.travelComboBox.addItem("inch/sec")
        travelLabel.setBuddy(self.travelComboBox)
        speedLabel = QLabel("Travel &Rate:")
        self.speedLineEdit = QLineEdit()
        speedLabel.setBuddy(self.speedLineEdit)
        dutyLabel = QLabel("Duty:")
        self.dutyLineEdit = QLineEdit()
        dutyLabel.setBuddy(self.dutyLineEdit)
        self.dutyComboBox = QComboBox()
        self.dutyComboBox.addItem("inches/hr")
        self.dutyComboBox.addItem("hrs/day")
        self.dutyComboBox.addItem("days/week")
        self.dutyComboBox.addItem("weeks/year")
        
        travelGroup = QGroupBox()
        travelGroup.setFlat(True)
        travelLayout = QGridLayout(travelGroup)                                
        travelLayout.addWidget(travelLabel, 0, 0)
        travelLayout.addWidget(self.travelLineEdit, 0, 1)
        travelLayout.addWidget(speedLabel, 1, 0)
        travelLayout.addWidget(self.speedLineEdit, 1, 1)
        travelLayout.addWidget(self.travelComboBox, 1, 2)
        travelLayout.addWidget(dutyLabel, 2, 0)
        travelLayout.addWidget(self.dutyLineEdit, 2, 1)
        travelLayout.addWidget(self.dutyComboBox, 2, 2)

        typeGroup = QGroupBox("JACK TYPE")
        typeLayout = QVBoxLayout(typeGroup)
        typeLayout.addLayout(screwtypeLayout)
        typeLayout.addLayout(hideLayout)
        typeLayout.addLayout(confitransLayout)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel|
                                          QDialogButtonBox.Ok)
        self.buttonBox.button(QDialogButtonBox.Cancel).setText("Reset")
        self.buttonBox.button(QDialogButtonBox.Cancel).setStatusTip(
            "Clear all inputs")
        self.buttonBox.button(QDialogButtonBox.Ok).setText("Submit")
        self.buttonBox.button(QDialogButtonBox.Ok).setToolTip("Calculating..")
        self.buttonBox.button(QDialogButtonBox.Ok).setStatusTip(
            "Selecting products for you.....Coming in 10s...")

        self.typeRadioGroup = QButtonGroup()
        self.typeRadioGroup.addButton(self.acmeRadioButton)
        self.typeRadioGroup.addButton(self.ballRadioButton)

        self.editFields = [self.arrangeComboBox,
                           self.dynloadLineEdit,
                           self.staloadLineEdit,
                           self.travelLineEdit,
                           self.speedLineEdit,
                           self.dutyLineEdit,
                           self.travelComboBox,
                           self.dutyComboBox,
                           self.directionComboBox,
                           self.directionLabel,
                           self.endfixComboBox,
                           self.endfixLabel,
                           self.configurationComboBox,
                           self.jacktypeLable,
                           self.translatingComboBox,
                           self.endtypeLabel,
                           self.keyoptionComboBox]

        self.buttonBox.accepted.connect(self.checktoSubmit)
        self.buttonBox.rejected.connect(self.clearAll)
        
        self.lineEditFields = [self.dynloadLineEdit,
                           self.staloadLineEdit,
                           self.travelLineEdit,
                           self.speedLineEdit,
                           self.dutyLineEdit]
        
        for item in self.lineEditFields:
            item.setStyleSheet('QLineEdit { background-color: #fff79a }')
            item.textChanged.connect(self.lineEditColor)

        self.warmLabel = QLabel("<b><font color='red'>"
                                "  *Please fill all fields</b>")
        self.warmLabel.hide()
            
        self.updateButton = QPushButton("Update")
        self.connect(self.updateButton,
                     SIGNAL("clicked()"), self.tableUpdate)

        #TAB SETUP & TAB 1 LAYOUT
        tabs = QTabWidget()
        self.tab1 = QWidget()
        tabs.addTab(self.tab1, "Select Jack")       
        tab1Layout = QFormLayout(self.tab1)
        tab1Layout.addRow(arrangeGroup)
        tab1Layout.addRow(loadGroup)
        tab1Layout.addRow(typeGroup)
        tab1Layout.addRow(directionGroup)
        tab1Layout.addRow(travelGroup)
        tab1Layout.addRow(self.warmLabel, self.buttonBox)
        #tab1Layout.addRow(self.warmLabel)
        tab1Layout.addRow(self.updateButton)
        
#*                                                                         *
#*                               * TAB 2 EDIT *                            *
#*                                                                         *

        #*    * DATABASE *     *
        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName("selectionresult.db")
        db.open()
        db.transaction()

        resultid = 1
        col = 0
    
        self.assetModel = MySqlModel(self)
        self.assetModel.setTable("results")
        self.assetModel.setSort(ID, Qt.AscendingOrder)
        #self.assetModel.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.assetModel.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self.assetModel.setHeaderData(ID, Qt.Horizontal,
                QVariant("ID"))
        self.assetModel.setHeaderData(SELECTION, Qt.Horizontal,
                QVariant("Model"))
        self.assetModel.setHeaderData(CAPACITYNUM, Qt.Horizontal,
                QVariant("Capacity\n[lbs]"))
        self.assetModel.setHeaderData(TRAVELRATE, Qt.Horizontal,
                "Travel\n Rate\n[RPM]")
        self.assetModel.setHeaderData(TORQUEPERJACK, Qt.Horizontal,
                QVariant("Torque\nRequired\nper Jack\n[in-lbs]"))
        self.assetModel.setHeaderData(TORQUETOTAL, Qt.Horizontal,
                QVariant("Total\n Torque\nRequired\n[in-lbs]"))
        self.assetModel.setHeaderData(HPPERJACK, Qt.Horizontal,
                "HP\n Required\nper Jack\n[HP]")
        self.assetModel.setHeaderData(HPTOTAL, Qt.Horizontal,
                "Total\n HP\nRequired\n[HP]")
        self.assetModel.select()

        self.assetView = QTableView()
        self.assetView.setModel(self.assetModel)
        self.assetView.setItemDelegate(AssetDelegate(self))
        self.assetView.setSelectionMode(QTableView.SingleSelection)
        self.assetView.setSelectionBehavior(QTableView.SelectRows)
        self.assetView.setSortingEnabled(True)
        self.assetView.sortByColumn(ID, Qt.AscendingOrder)
        self.assetView.setColumnWidth(1, 75)
        self.assetView.setColumnWidth(7, 63)
        self.assetView.setColumnWidth(8, 60)
        self.assetView.setColumnWidth(17, 65)
        self.assetView.setColumnWidth(18, 65)
        self.assetView.setColumnWidth(19, 65)
        self.assetView.setColumnWidth(20, 70)
        self.assetView.setColumnHidden(ID, True)
        #self.assetView.setColumnHidden(JACKTYPE, True)
        #self.assetView.setColumnHidden(TRANSLATING, True)
        #self.assetView.setColumnHidden(AB, True)
        #self.assetView.setColumnHidden(KEYED, True)
        #self.assetView.setColumnHidden(ENDOPTION, True)
        #self.assetView.setColumnHidden(CAPACITYNUM, True)
        #self.assetView.setColumnHidden(DIAMETER, True)
        #self.assetView.setColumnHidden(ROOTDIA, True)
        #self.assetView.setColumnHidden(LEAD, True)
        #self.assetView.setColumnHidden(RATIO, True)
        #self.assetView.setColumnHidden(HPNUM, True)
        #self.assetView.setColumnHidden(TORQUEPERLBS, True)
        #self.assetView.setColumnHidden(TORQUENOLOAD, True)
        #self.assetView.setColumnHidden(TORQUEFULLLOAD, True)
        #self.assetView.setColumnHidden(MAXINPERHOUR, True)
        if self.arrangeComboBox.currentText() == "1":
            self.assetView.setColumnHidden(TORQUETOTAL, True)
            self.assetView.setColumnHidden(HPTOTAL, True)
        #self.assetView.setColumnHidden(DUTYCYCLE, True)
        #self.assetView.setColumnHidden(TURNSOFWORM, True)
        #self.assetView.setColumnHidden(FIXEDFREE, True)
        #self.assetView.setColumnHidden(FIXEDGUIDE, True)
        #self.assetView.setColumnHidden(PINENDS, True)
        #self.assetView.setColumnHidden(SELFLOCKING, True)
        self.assetView.setVisible(False)
        assetLabel = QLabel("R&ESULTS")
        assetLabel.setFont(QFont("Times", 11, QFont.Bold))
        assetLabel.setBuddy(self.assetView)
        while self.assetModel.canFetchMore():
            self.assetModel.fetchMore()

        self.logModel = MySqlModel(self)
        self.logModel.setTable("selections")
        self.logModel.setSort(ID, Qt.AscendingOrder)
        self.logModel.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self.logModel.setHeaderData(CAPACITY, Qt.Horizontal,
                QVariant("Capacity"))
        self.logModel.setHeaderData(SRATIO, Qt.Horizontal,
                QVariant("Gear \n Ratio"))
        self.logModel.setHeaderData(SDIAMETER, Qt.Horizontal,
                QVariant("Screw \n Diameter"))
        self.logModel.setHeaderData(SROOTDIA, Qt.Horizontal,
                QVariant("Root \n Diameter"))
        self.logModel.setHeaderData(SLEAD, Qt.Horizontal,
                QVariant("Screw \n Lead"))
        self.logModel.setHeaderData(HPTEXT, Qt.Horizontal,
                QVariant("Max Input \n HP"))
        self.logModel.setHeaderData(STORQUEPERLBS, Qt.Horizontal,
                QVariant("Torque to\n Raise 1lbs."))
        self.logModel.setHeaderData(STORQUENOLOAD, Qt.Horizontal,
                QVariant("Worm Torque \n at No Load"))
        self.logModel.setHeaderData(STORQUEFULLLOAD, Qt.Horizontal,
                QVariant("Full Load \n Torque"))
        self.logModel.setHeaderData(STURNSOFWORM, Qt.Horizontal,
                QVariant("Input Turns \n per 1in."))
        self.logModel.select()

        self.logView = QTableView()
        self.logView.setModel(self.logModel)
        self.logView.setItemDelegate(LogDelegate(self))
        self.logView.setSelectionMode(QTableView.SingleSelection)
        self.logView.setSelectionBehavior(QTableView.SelectRows)
        self.logView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.logView.setColumnHidden(ID, True)
        self.logView.setColumnHidden(RESULTID, True)
        self.logView.setVisible(False)
        self.logView.resizeColumnsToContents()
        self.logView.setVisible(True)
        self.logView.horizontalHeader().setStretchLastSection(True)
        logLabel = QLabel("Model &Details")
        logLabel.setFont(QFont("Times", 10, QFont.Bold))
        logLabel.setBuddy(self.logView)

        resultLayout = QVBoxLayout()
        resultLayout.addWidget(assetLabel)
        resultLayout.addWidget(self.assetView, 1)
        resultLayout.addWidget(logLabel)
        resultLayout.addWidget(self.logView)
        #self.setLayout(resultLayout)

        self.connect(self.assetView.selectionModel(),
                     SIGNAL("currentRowChanged(QModelIndex,QModelIndex)"),
                     self.assetChanged)
        self.assetChanged(self.assetView.currentIndex())
                               
        #*    * INPUT *     *
        inputLabel = QLabel("INPUT")
        self.arrangementLabel = QLabel("Jack Arrangement:")
        self.arrangementLabel.setFont(QFont("Calibri", 10, QFont.Bold))
        self.arrangementReadLabel = QLabel()
        self.arrangementReadLabel.setAlignment(\
            Qt.AlignLeft|Qt.AlignVCenter)
        self.connect(self.arrangeComboBox, \
                     SIGNAL("currentIndexChanged(int)"),
                     self.arrangTextChanged)
        inputLabel.setFont(QFont("Times", 11, QFont.Bold))
        dynload1Label = QLabel("Dynamic Load:")
        dynload1Label.setFont(QFont("Calibri", 10, QFont.Bold))
        self.dynloadReadLabel = QLabel()
        self.dynloadReadLabel.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
        self.dynloadLineEdit.textChanged.connect(self.dynTextChanged)
        staload1Label = QLabel("Static Load:")
        staload1Label.setFont(QFont("Calibri", 10, QFont.Bold))
        self.staloadReadLabel = QLabel()
        self.staloadReadLabel.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
        self.staloadLineEdit.textChanged.connect(self.staTextChanged)
        direction1Label = QLabel("Load Direction:")
        direction1Label.setFont(QFont("Calibri", 10, QFont.Bold))
        self.direction2Label = QLabel()
        self.direction2Label.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
        self.connect(self.directionComboBox, \
                     SIGNAL("currentIndexChanged(int)"),
                     self.directionChanged)
        endfix1Label = QLabel("Column End Fixity:")
        endfix1Label.setFont(QFont("Calibri", 10, QFont.Bold))
        self.endfix2Label = QLabel()
        self.connect(self.endfixComboBox, SIGNAL("currentIndexChanged(int)"),
                     self.endfixChanged)
        travel1Label = QLabel("Total Travel:")
        travel1Label.setFont(QFont("Calibri", 10, QFont.Bold))
        self.travelReadLabel = QLabel()
        self.travelReadLabel.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
        self.travelLineEdit.textChanged.connect(self.travTextChanged)
        speed1Label = QLabel("Travel Rate:")
        speed1Label.setFont(QFont("Calibri", 10, QFont.Bold))
        self.speedReadLabel = QLabel()
        self.speedReadLabel.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
        self.connect(self.travelComboBox, SIGNAL("currentIndexChanged(int)"),
                     self.speedTextChanged)
        self.speedLineEdit.textChanged.connect(self.speedTextChanged)
        duty1Label = QLabel("Duty:")
        duty1Label.setFont(QFont("Calibri", 10, QFont.Bold))
        self.dutyReadLabel = QLabel()
        self.dutyReadLabel.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
        self.connect(self.dutyComboBox, SIGNAL("currentIndexChanged(int)"),
                     self.dutyTextChanged)
        self.dutyLineEdit.textChanged.connect(self.dutyTextChanged)
        type1Label = QLabel("Jack Type:")
        type1Label.setFont(QFont("Calibri", 10, QFont.Bold))
        self.acmeRadioButton.toggled.connect( \
            lambda:self.btnstate(self.acmeRadioButton))
        self.ballRadioButton.toggled.connect( \
            lambda:self.btnstate(self.ballRadioButton))
        self.typeReadLabel = QLabel()

        self.configuration1Label = QLabel("Configuration:")
        self.configuration1Label.setFont(QFont("Calibri", 10, QFont.Bold))
        self.configReadLabel = QLabel()
        self.configReadLabel.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
        self.connect(self.configurationComboBox,\
                     SIGNAL("currentIndexChanged(int)"),
                     self.configTextChanged)
        self.translating1Label = QLabel("Translating:")
        self.translating1Label.setFont(QFont("Calibri", 10, QFont.Bold))
        self.transReadLabel = QLabel()
        self.transReadLabel.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
        self.connect(self.translatingComboBox, \
                     SIGNAL("currentIndexChanged(int)"),
                     self.transTextChanged)
        self.keyedLabel = QLabel("Keyed Option:")
        self.keyedLabel.setFont(QFont("Calibri", 10, QFont.Bold))
        self.keyedReadLabel = QLabel()
        self.keyedReadLabel.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
        self.connect(self.keyoptionComboBox, \
                     SIGNAL("currentIndexChanged(int)"),
                     self.keyedTextChanged)

        self.radialLabel = QLabel("Radial Bearing Options")
        self.radialLabel.setFont(QFont("Calibri", 10, QFont.Bold))
        self.radialReadLabel = QLabel()
        self.radialReadLabel.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
        self.connect(self.bearingoptionComboBox, \
                     SIGNAL("currentIndexChanged(int)"),
                     self.radialTextChanged)
        self.radialLabel.hide()
        self.radialReadLabel.hide()

        self.editFieldsTab2 = [self.arrangementReadLabel,
                               self.dynloadReadLabel,
                               self.staloadReadLabel,
                               self.direction2Label,
                               self.endfix2Label,
                               self.travelReadLabel,
                               self.speedReadLabel,
                               self.dutyReadLabel,
                               self.typeReadLabel,
                               self.configReadLabel,
                               self.transReadLabel,
                               self.keyedReadLabel,
                               self.radialReadLabel]

        splitter = QSplitter(Qt.Horizontal)
        self.line = QFrame()
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        inputLayout = QGridLayout()
        inputLayout.addWidget(inputLabel, 0, 0)
        inputLayout.addWidget(self.arrangementLabel, 1, 0)
        inputLayout.addWidget(self.arrangementReadLabel, 1, 1)
        inputLayout.addWidget(dynload1Label, 2, 0)
        inputLayout.addWidget(self.dynloadReadLabel, 2, 1)
        inputLayout.addWidget(staload1Label, 3, 0)
        inputLayout.addWidget(self.staloadReadLabel, 3, 1)
        inputLayout.addWidget(direction1Label, 4, 0)
        inputLayout.addWidget(self.direction2Label, 4, 1)
        inputLayout.addWidget(endfix1Label, 5, 0)
        inputLayout.addWidget(self.endfix2Label, 5, 1)
        inputLayout.addWidget(travel1Label, 6, 0)
        inputLayout.addWidget(self.travelReadLabel, 6, 1)
        inputLayout.addWidget(speed1Label, 7, 0)
        inputLayout.addWidget(self.speedReadLabel, 7, 1)
        inputLayout.addWidget(duty1Label, 8, 0)
        inputLayout.addWidget(self.dutyReadLabel, 8, 1)
        inputLayout.addWidget(type1Label, 9, 0)
        inputLayout.addWidget(self.typeReadLabel, 9, 1)
        inputLayout.addWidget(self.configuration1Label, 10, 0)
        inputLayout.addWidget(self.configReadLabel, 10, 1)
        inputLayout.addWidget(self.translating1Label, 11, 0)
        inputLayout.addWidget(self.transReadLabel, 11, 1)
        inputLayout.addWidget(self.keyedLabel, 12, 0)
        inputLayout.addWidget(self.keyedReadLabel, 12, 1)
        inputLayout.addWidget(self.radialLabel, 13, 0)
        inputLayout.addWidget(self.radialReadLabel, 13, 1)
        inputLayout.addWidget(self.line, 14, 0, 1, -1)
        

        #TAB 2 LAYOUT
        #self.tab2 = QTabWidget()
        self.tab2 = QWidget()
        tabs.addTab(self.tab2, "Selection Results")
        tab2Layout = QVBoxLayout(self.tab2)
        tab2Layout.addLayout(inputLayout)
        tab2Layout.addLayout(resultLayout)
        
#*                                                                         *
#*                               * TAB 3  *                                *
#*                                                                         *

        self.bootLabel = QLabel("Boot:")
        self.bootComboBox = QComboBox()
        self.bootComboBox.addItem("Not Required")
        self.bootComboBox.addItem("For Vertical Operation")
        self.bootComboBox.addItem("For Horizontal Operation")

        paintLabel = QLabel("Paint (Housing Finish):                    ")
        self.paintComboBox = QComboBox()
        self.paintComboBox.addItem("Gray Enamel (Standard)")
        self.paintComboBox.addItem("None")
        self.paintComboBox.addItem("White Epoxy")
        self.paintComboBox.addItem("Gray Polyurethane")
        self.paintComboBox.addItem("Green Polyurethane")
        self.paintComboBox.addItem("White Polyurethane")
        self.paintComboBox.addItem("Red Oxide Primer")
        self.paintComboBox.addItem("Electroless Nickel Plated")

        stopnutLabel = QLabel("Stop Nut:")
        self.stopnutmatComboBox = QComboBox()
        self.stopnutmatComboBox.addItem("Not Required")
        self.stopnutmatComboBox.addItem("Steel")
        self.stopnutmatComboBox.addItem("Stainless Steel")
        self.stopnutComboBox = QComboBox()
        self.stopnutComboBox.addItem("- Select -")
        self.stopnutComboBox.addItem("Extend & Retract")
        self.stopnutComboBox.addItem("Extend")
        self.stopnutComboBox.addItem("Retract")
        self.connect(self.stopnutmatComboBox, SIGNAL("activated(int)"),
                     self.setstopnutType)
        self.stopnutComboBox.hide()

        greaseLabel = QLabel("Grease:")
        self.greaseComboBox = QComboBox()
        self.greaseComboBox.addItem("Standard Grease")
        self.greaseComboBox.addItem("Low Temperature, rated to -40\xb0 F")
        self.greaseComboBox.addItem("Food Grade Grease")
        self.greaseComboBox.addItem("Shipped Dry")

        spaceLabel = QLabel()

        inputAcessLayout = QGridLayout()
        inputAcessLayout.addWidget(self.bootLabel, 0, 0)
        inputAcessLayout.addWidget(self.bootComboBox, 0, 1)
        inputAcessLayout.addWidget(paintLabel, 1, 0)
        inputAcessLayout.addWidget(self.paintComboBox, 1, 1)
        inputAcessLayout.addWidget(stopnutLabel, 2, 0)
        inputAcessLayout.addWidget(self.stopnutmatComboBox, 2, 1)
        inputAcessLayout.addWidget(self.stopnutComboBox, 3, 1)
        inputAcessLayout.addWidget(greaseLabel, 4, 0)
        inputAcessLayout.addWidget(self.greaseComboBox, 4, 1)
        inputAcessLayout.addWidget(spaceLabel, 5, 0, 5, 5)
        
        #TAB 3 LAYOUT
        self.tab3 = QWidget()
        tabs.addTab(self.tab3, "Accessories")
        tab3Layout = QVBoxLayout(self.tab3)
        tab3Layout.addLayout(inputAcessLayout)

        self.setCentralWidget(tabs)

        #TIPS SETUP
        self.sizeLabel = QLabel()
        self.sizeLabel.setFrameStyle(QFrame.StyledPanel|QFrame.Sunken)
        status = self.statusBar()
        status.setSizeGripEnabled(False)
        status.addPermanentWidget(self.sizeLabel)
        status.showMessage("Ready", 5000)

#*                                                                         *
#*                              * TITLE EDIT *                             *
#*                                                                         *

        #*********************** ACTION ***********************
        fileNewAction = self.createAction("&New...", self.fileNew,
                QKeySequence.New, "fileNew", "Create a selection")
        fileOpenAction = self.createAction("&Open...", self.fileOpen,
                QKeySequence.Open, "fileOpen",
                "Open an existing selection file")
        fileSaveAction = self.createAction("&Save", self.fileSave,
                QKeySequence.Save, "fileSave", "Save the selection")
        fileSaveAsAction = self.createAction("Save &As...",
                self.fileSaveAs, "", "fileSaveas",
                tip="Save the selection using a new name")
        #filePreviewAction = self.createAction("&Preview",
        #        self.filePreview, "", "filePreview",
        #        tip="Preview Quote before printing")
        filePrintAction = self.createAction("&Print", self.filePrint,
                QKeySequence.Print, "filePrint", "Print Quote")
        
        duffnortonAction = self.createAction("&Duff Norton",
                self.duffPage, "", "duff", "Duff Norton Webpage")
        literatureAction = self.createAction("&Literature",
                self.viewLiterature, "", "literature",
                "Screw Jack Design Guide")
        modelAction = self.createAction("&2D / 3D models",
                self.viewOnlineModel, "", "model", "2D/3D Models")
        
        quoteAction = self.createAction("&Request a Quote",
                self.requestQuote, "", "question2", "Request a Quote")
        
        fileQuitAction = self.createAction("&Quit", self.close,
                "Ctrl+Q", "filequit", "Close the application")

        helpAboutAction = self.createAction("&About Jack Selector",
                self.helpAbout)
        helpHelpAction = self.createAction("&Help", self.helpHelp,
                QKeySequence.HelpContents)

        #*********************** MENU ***********************

        #FILE MENU
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenuActions = (fileNewAction, fileOpenAction,
                fileSaveAction, fileSaveAsAction, None,
                filePrintAction, fileQuitAction)
        self.connect(self.fileMenu, SIGNAL("aboutToShow()"),
                     self.updateFileMenu)
        #HELP MENU
        helpMenu = self.menuBar().addMenu("&Help")
        self.addActions(helpMenu, (literatureAction, modelAction,
                                   duffnortonAction, quoteAction, None,
                                   helpAboutAction, helpHelpAction))

        #TOOL BAR
        fileToolbar = self.addToolBar("File")
        fileToolbar.setObjectName("FileToolBar")
        self.addActions(fileToolbar, (fileNewAction, fileOpenAction,
                                      fileSaveAction, fileSaveAsAction,
                                      filePrintAction))
        #printToolbar = self.addToolBar("Print")
        #printToolbar.setObjectName("PrintToolbar")
        #self.addActions(printToolbar, (filePreviewAction, filePrintAction))
        
        #WEB BAR
        duffNortonToolbar = self.addToolBar("DuffNorton")
        duffNortonToolbar.setObjectName("duffNortonToolbar")
        self.addActions(duffNortonToolbar,
                        (literatureAction, modelAction, duffnortonAction,
                         None, quoteAction))

        #quoteToolbar = self.addToolBar("Request Quote")
        #quoteToolbar.setObjectName("RequestToolbar")
        #self.addActions(quoteToolbar, quoteAction)

        
        #SETTING
        settings = QSettings()
        self.recentFiles = settings.value("RecentFiles").toStringList()
        size = settings.value("MainWindow/Size",
                              QVariant(QSize(400,580))).toSize()
        self.resize(size)
        position = settings.value("MainWindow/Position",
                                  QVariant(QPoint(0, 0))).toPoint()
        self.move(position)
        self.restoreState(
                settings.value("MainWindow/State").toByteArray())
        
        self.setWindowTitle("Duff Norton - Jack Selector")
        self.updateFileMenu()
        QTimer.singleShot(0, self.loadInitialFile)

        self.selector = []
        self.selector.append(str(self.arrangementReadLabel.text()))
        self.selector.append(str(self.dynloadReadLabel.text()))
        self.selector.append(str(self.staloadReadLabel.text()))
        if self.acmeRadioButton.isChecked():
            self.selector.append("Machine Screw Jack")
        elif self.ballRadioButton.isChecked():
            self.selector.append("Ball Screw Jack")
        else:
            self.selector.append("")
        self.selector.append(str(self.configReadLabel.text()))
        self.selector.append(str(self.transReadLabel.text()))
        self.selector.append(str(self.keyedReadLabel.text()))
        self.selector.append(str(self.radialReadLabel.text()))
        self.selector.append(str(self.direction2Label.text()))
        self.selector.append(str(self.endfix2Label.text()))
        self.selector.append(str(self.travelReadLabel.text()))
        self.selector.append(str(self.speedReadLabel.text()))
        self.selector.append(str(self.travelComboBox.currentText()))
        self.selector.append(str(self.dutyReadLabel.text()))
        self.selector.append(str(self.dutyComboBox.currentText()))
        
#*                                                                         *
#*                        * DEFAULT FUNCTION *                             *
#*                                                                         *

    def hideWarmLabel(self):
        return self.warmLabel.hide()
    
    def checktoSubmit(self):
        #timer = QTimer()
        if self.arrangeComboBox.currentText() <> "- Select -" and\
           self.configurationComboBox.currentText() <> "- Select -" and\
           self.directionComboBox.currentText() <> "- Select -" and\
           len(self.dynloadLineEdit.text()) > 0 and\
           len(self.staloadLineEdit.text()) > 0 and\
           len(self.travelLineEdit.text()) > 0 and\
           len(self.speedLineEdit.text()) > 0 and\
           len(self.dutyLineEdit.text()) > 0 and \
           self.acmeRadioButton.isChecked() or \
           self.ballRadioButton.isChecked():
            self.warmLabel.hide()
            self.calculate()
        else:
            self.warmLabel.show()
            timer = QTimer(self)
            timer.timeout.connect(self.hideWarmLabel)
            timer.start(6000)

            #self.radiobutton == True and \


    def calculate(self):
        self.warmLabel.hide()
        while self.assetModel.canFetchMore():
            self.assetModel.fetchMore()
        self.assetView.setVisible(False)   
        self.assetView.setVisible(True)

        if self.arrangeComboBox.currentText() == "1":
            self.assetView.setColumnHidden(TORQUETOTAL, True)
            self.assetView.setColumnHidden(HPTOTAL, True)
        else:
            self.assetView.setColumnHidden(TORQUETOTAL, False)
            self.assetView.setColumnHidden(HPTOTAL, False)
        
        if self.travelComboBox.currentText() == "inch/min":
            travelinputinch = float(self.speedLineEdit.text())
        elif self.travelComboBox.currentText() == "inch/sec":
            travelinputinch = float(self.speedLineEdit.text()) * 60
            
        dyninput = self.dynloadLineEdit.text().toInt()[0]
        stainput = self.staloadLineEdit.text().toInt()[0]
        loadmax = max(dyninput, stainput)
        yeffecient = float(travelinputinch) / 12
        xeffecient = yeffecient * float(loadmax) / 33000
        inputduty = float(self.dutyLineEdit.text())

        arranEff = 1
        arranValue = self.arrangeComboBox.currentText()
        if arranValue == "2":
            arranEff = 0.95
        elif arranValue == "3":
            arranEff = 0.90
        elif arranValue == "4":
            arranEff = 0.85
        elif arranValue in ("6", "8"):
            arranEff = 0.80
        
        query = QSqlQuery()
        row = self.assetModel.rowCount()
        for i in range(row): 
            turnworm = self.assetModel.record(i)\
                       .value("turnsofworm").toByteArray()
            capacityNum = self.assetModel.record(i)\
                          .value("capacitynum").toByteArray()
            fullLoad = self.assetModel.record(i)\
                       .value("torquefullload").toByteArray()
            noLoad = self.assetModel.record(i)\
                     .value("torquenoload").toByteArray()
            horsePower = self.assetModel.record(i)\
                         .value("hpnum").toByteArray()
            
            #Lifting Speed RPM
            travelinputrpm = float(travelinputinch) * float(turnworm)

            #Torque Required load < 25%capacity
            #torqueCalc = float(dyninput) / float(capacityNum) \
            #             * float(fullLoad)

            #Torque Required load > 25%capacity
            torqueCalc = float(loadmax) / float(capacityNum)\
                         *(float(fullLoad) - float(noLoad)) + float(noLoad)
            totalTorqueCalc = float(arranValue) * float(torqueCalc) / \
                              float(arranEff)
            
            #HP Required lower value
            #hpCalc = (float(dyninput) / float(capacityNum) * 
            #          (float(travelinputrpm) - float(noLoad)) * 
            #          float(fullLoad) + float(noLoad)) / 63025

            hpCalc = float(travelinputrpm) * float(torqueCalc)/ 63025
            totalHpCalc = float(travelinputrpm) * float(totalTorqueCalc)/\
                          63025
            
            #Actuator Effecieny
            jackEffecient = float(xeffecient) / \
                            ((float(loadmax) / float(capacityNum)\
                             * float(fullLoad)) * float(travelinputrpm)\
                             / 63025)
            maxInPerHour = min(float(travelinputinch)*60,
                               float(travelinputinch)*60*
                               (float(jackEffecient)*float(horsePower)\
                                /float(hpCalc)))
            dutyCycle = float(maxInPerHour) / \
                        (float(travelinputinch) * 60) * 100

            query.exec_("UPDATE results SET torqueperjack"
                        " = %.2f WHERE id = %d" % (torqueCalc, i+1))
            query.exec_("UPDATE results SET torquetotal"
                        " = %.2f WHERE id = %d" % (totalTorqueCalc, i+1))

            query.exec_("UPDATE results SET hptotal"
                        " = %.2f WHERE id = %d" % (totalHpCalc, i+1))

            if  0 <= float(hpCalc) < float(horsePower):
                query.exec_("UPDATE results SET hpperjack"
                            " = %.2f WHERE id = %d" % (hpCalc, i+1))
            else:
                query.exec_("UPDATE results SET hpperjack"
                            " = 'Exceed' WHERE id = %d" % (i+1))
            
            if loadmax > 70000:
                if travelinputrpm < 900:
                    query.exec_("UPDATE results SET travelrate"
                                " = %.0f WHERE id = %d" % \
                                (travelinputrpm, i+1))
                else:
                    query.exec_("UPDATE results SET travelrate"
                                " = 'Exceed' WHERE id = %d" % (i+1))
            else:
                if travelinputrpm < 1800:
                    query.exec_("UPDATE results SET travelrate"
                                " = %.0f WHERE id = %d" % \
                                (travelinputrpm, i+1))
                else:
                    query.exec_("UPDATE results SET travelrate"
                                " = 'Exceed' WHERE id = %d" % (i+1))

            query.exec_("UPDATE results SET dutycycle"
                        " = %.1f WHERE id = %d" % (dutyCycle, i+1))

            if float(maxInPerHour) > float(inputduty):
                query.exec_("UPDATE results SET maxinperhour"
                            " = %.1f WHERE id = %d" % (maxInPerHour, i+1))
            else:
                query.exec_("UPDATE results SET maxinperhour"
                            " = 'Exceed' WHERE id = %d" % (i+1))

            query.exec_()
            self.assetModel.select()
        self.assetModel.submitAll()

    def tableUpdate(self):
        self.assetView.resizeColumnsToContents()
        self.assetView.setVisible(True)
        self.assetModel.select()
        self.assetView.setModel(self.assetModel)
        self.assetModel.select()
        
        scrtype = self.typeReadLabel.text()
        config = self.configurationComboBox.currentText()
        trans = self.translatingComboBox.currentText()
        key = self.keyoptionComboBox.currentText()
        dyninput = self.dynloadLineEdit.text().toInt()[0]
        stainput = self.staloadLineEdit.text().toInt()[0]
        loadmax = max(dyninput, stainput)
        rpmlimit = "Exceed"
        hplimit = "Exceed"
        dutylimit = "Exceed"
        travel = self.travelLineEdit.text().toInt()[0]

        if self.selflocking.isChecked():
            selflock = "yes"
        else:
            selflock = "no"
        
        if self.antibacklash.isChecked():
            antiback = "yes"
        else:
            antiback = "no"

        if str(self.directionComboBox.currentText()) == "Tension":\
           self.assetModel.setFilter(\
               QString("jacktype like '%1' AND "
                       "translating like '%2' AND "
                       "endoption like '%3' AND "
                       "ab like '%4' AND "
                       "selflocking like '%5' AND "
                       "keyed like '%6' AND "
                       "capacitynum >= %7 AND "
                       "travelrate not like '%8' AND "
                       "hpperjack not like '%9' AND "
                       "maxinperhour not like '%10' ")
               .arg(scrtype)
               .arg(config)
               .arg(trans)
               .arg(antiback)
               .arg(selflock)
               .arg(key)
               .arg(loadmax)
               .arg(rpmlimit)
               .arg(hplimit)
               .arg(dutylimit))

        elif str(self.directionComboBox.currentText()) <> "Tension":
            if str(self.endfixComboBox.currentText()) \
               == "One end fixed & one end free":\
               self.assetModel.setFilter(
                   QString("jacktype like '%1' AND "
                           "translating like '%2' AND "
                           "endoption like '%3' AND "
                           "ab like '%4' AND "
                           "selflocking like '%5' AND "
                           "keyed like '%6' AND "
                           "capacitynum >= %7 AND "
                           "travelrate not like '%8' AND "
                           "hpperjack not like '%9' AND "
                           "maxinperhour not like '%10' AND "
                           "fixedfree >= %11 ")
                   .arg(scrtype)
                   .arg(config)
                   .arg(trans)
                   .arg(antiback)
                   .arg(selflock)
                   .arg(key)
                   .arg(loadmax)
                   .arg(rpmlimit)
                   .arg(hplimit)
                   .arg(dutylimit)
                   .arg(travel))
                
            elif str(self.endfixComboBox.currentText()) \
                 == "One end fixed & one end guided":\
                 self.assetModel.setFilter(
                     QString("jacktype like '%1' AND "
                             "translating like '%2' AND "
                             "endoption like '%3' AND "
                             "ab like '%4' AND "
                             "selflocking like '%5' AND "
                             "keyed like '%6' AND "
                             "capacitynum >= %7 AND "
                             "travelrate not like '%8' AND "
                             "hpperjack not like '%9' AND "
                             "maxinperhour not like '%10' AND "
                             "fixedguide >= %11 ")
                     .arg(scrtype)
                     .arg(config)
                     .arg(trans)
                     .arg(antiback)
                     .arg(selflock)
                     .arg(key)
                     .arg(loadmax)
                     .arg(rpmlimit)
                     .arg(hplimit)
                    .arg(dutylimit)
                    .arg(travel))
            elif str(self.endfixComboBox.currentText()) \
                 == "Pinned Ends":\
                 self.assetModel.setFilter(
                     QString("jacktype like '%1' AND "
                             "translating like '%2' AND "
                             "endoption like '%3' AND "
                             "ab like '%4' AND "
                             "selflocking like '%5' AND "
                             "keyed like '%6' AND "
                             "capacitynum >= %7 AND "
                             "travelrate not like '%8' AND "
                             "hpperjack not like '%9' AND "
                             "maxinperhour not like '%10' AND "
                             "pinends >= %11 ")
                     .arg(scrtype)
                     .arg(config)
                     .arg(trans)
                     .arg(antiback)
                     .arg(selflock)
                     .arg(key)
                     .arg(loadmax)
                     .arg(rpmlimit)
                     .arg(hplimit)
                     .arg(dutylimit)
                     .arg(travel))
        else:
            self.assetModel.select()
        self.assetModel.select()

           
    def assetChanged(self, index):
        if index.isValid():
            record = self.assetModel.record(index.row())
            id = record.value("id").toInt()[0]
            self.logModel.setFilter(QString("resultid = %1").arg(id))
        else:
            self.logModel.setFilter(QString("resultid = -1"))
        self.logModel.reset() 
        self.logModel.select()
        self.logView.horizontalHeader().setVisible(
                self.logModel.rowCount() > 0)
        if PYQT_VERSION_STR < "4.1.0":
            self.logView.setColumnHidden(ID, True)
            self.logView.setColumnHidden(RESULTID, True)

    def lineEditColor(self):
        sender = self.sender()
        if sender.text().isEmpty():
            sender.setStyleSheet('QLineEdit { background-color: #fff79a }')
        else:
            sender.setStyleSheet('QLineEdit { background-color: #c4df9b }')
            
#*                                                                         *
#*                               * TAB 1 *                                 *
#*                             ITEM   FUNCTION                             *

    def showhide(self):
        self.selflocking.show()
        self.antibacklash.show()

    def hideshow(self):
        self.selflocking.hide()
        self.antibacklash.hide()
        self.antibacklash.setChecked(False)
        self.selflocking.setChecked(False)

    def setJackType(self):
        transType = self.configurationComboBox.currentText()
        if transType in ("Upright",
                         "Inverted",
                         "Upright Rotating",
                         "Inverted Rotating",
                         "Double Clevis"):
            self.configReadLabel.show()
            pixmap = self._makeJackTypePixmap()
            self.jacktypeLable.show()
            self.jacktypeLable.setPixmap(pixmap.scaled(115,115))
        else:
            self.jacktypeLable.hide()
            self.configReadLabel.hide()

        if self.configurationComboBox.currentText() in \
           ("- Select -", "Upright", "Inverted", "Double Clevis"):
            self.bootLabel.show()
            self.bootComboBox.show()
        else:
            self.bootLabel.hide()
            self.bootComboBox.hide()

    def setJackType2(self):
        transType = self.configurationComboBox.currentText()
        if transType in ("Upright Rotating", "Inverted Rotating"):
            self.bearingoptionLabel.show()
            self.bearingoptionComboBox.setCurrentIndex(0)
            self.bearingoptionComboBox.show()
            self.keyoptionComboBox.model().item(2).setEnabled(False)
            self.keyoptionComboBox.setCurrentIndex(0)
            self.keyoptionLabel.hide()
            self.keyoptionComboBox.hide()
            self.keyedLabel.hide()
            self.keyedReadLabel.hide()
            self.keyedReadLabel.clear()
            self.radialLabel.show()
            self.radialReadLabel.show()
            self.translatingLabel.hide()
            self.endtypeLabel.clear()
            self.endtypeLabel.hide()
            self.translating1Label.hide()
            self.transReadLabel.hide()
            self.translatingComboBox.setCurrentIndex(0)
            self.translatingComboBox.hide()
        elif transType == "Double Clevis":
            self.bearingoptionLabel.hide()
            self.bearingoptionComboBox.hide()
            self.keyoptionComboBox.model().item(2).setEnabled(False)
            self.keyoptionComboBox.setCurrentIndex(1)
            self.keyoptionLabel.hide()
            self.keyoptionComboBox.hide()
            self.keyedLabel.hide()
            self.keyedReadLabel.hide()
            self.keyedReadLabel.clear()
            self.radialLabel.hide()
            self.radialReadLabel.hide()
            self.translatingLabel.hide()
            self.endtypeLabel.clear()
            self.endtypeLabel.hide()
            self.translating1Label.hide()
            self.transReadLabel.hide()
            self.translatingComboBox.setCurrentIndex(0)
            self.translatingComboBox.hide()
        else:
            self.bearingoptionComboBox.setCurrentIndex(0)
            self.bearingoptionLabel.hide()
            self.bearingoptionComboBox.hide()
            self.keyoptionLabel.show()
            self.keyoptionComboBox.show()
            self.keyoptionComboBox.model().item(2).setEnabled(True)
            self.keyedLabel.show()
            self.keyedReadLabel.show()
            self.radialLabel.hide()
            self.radialReadLabel.hide()
            self.translatingLabel.show()
            self.endtypeLabel.show()
            self.translatingComboBox.show()
            self.translating1Label.show()
            self.transReadLabel.show()

    def _makeJackTypePixmap(self):
        name = str(self.configurationComboBox.currentText())
        pixmap = QPixmap(":/%s.png" % name)
        return pixmap

    def setEndTypeImage(self):
        endType = self.translatingComboBox.currentText()
        if endType in ("Threaded End", "Top Plate", "Clevis End"):
            pixmap = self._makeEndTypePixmap()
            self.endtypeLabel.show()
            self.endtypeLabel.setPixmap(pixmap.scaled(115,115))
            self.transReadLabel.show()
        else:
            self.endtypeLabel.hide()
            self.transReadLabel.hide()

    def _makeEndTypePixmap(self):
        name = str(self.translatingComboBox.currentText())
        pixmap = QPixmap(":/%s.png" % name)
        return pixmap


    def setDirImage(self):
        direct = self.directionComboBox.currentText()
        if direct in ("Tension", "Compression",
                      "Compression & Tension"):
            pixmap = self._makeDirPixmap()
            self.directionLabel.show()
            self.directionLabel.setPixmap(pixmap.scaled(115,115))
        else:
            self.directionLabel.hide()
   
    def _makeDirPixmap(self):
        name = str(self.directionComboBox.currentText())
        pixmap = QPixmap(":/%s.png" % name)
        return pixmap

    def showEndCombo(self):
        name = str(self.directionComboBox.currentText())
        endType = self.translatingComboBox.currentText()
        if name == "Compression & Tension":
            self.endfixComboBox.show()
            if len(endType)>0:
                self.endfixLabel.show()
        elif name == "Compression":
            self.endfixComboBox.show()
            if len(endType)>0:
                self.endfixLabel.show()
        elif name == "Tension" or "- Select -":
            self.endfixComboBox.setCurrentIndex(0)
            self.endfixComboBox.hide()
            self.endfixLabel.clear()
            self.endfixLabel.hide()

    def setEndfixImage(self):
        endFix = self.endfixComboBox.currentText()
        if endFix in ("One end fixed & one end free",
                      "Pinned Ends",
                      "One end fixed & one end guided"):
            pixmap = self._makeEndPixmap()
            self.endfixLabel.setPixmap(pixmap.scaled(115,115))
            self.endfixLabel.show()
        else:
            self.endfixLabel.hide()
            
    def _makeEndPixmap(self):
        name = str(self.endfixComboBox.currentText())
        pixmap = QPixmap(":/%s.jpg" % name)
        return pixmap

    def clearAll(self, checked=False):
        
        for field in self.editFields:
            field.clear()

        for field in self.editFieldsTab2:
            field.clear()

        self.selflocking.setChecked(False)
        self.antibacklash.setChecked(False)

        self.typeRadioGroup.setExclusive(False)
        self.acmeRadioButton.setChecked(False)
        self.ballRadioButton.setChecked(False)
        self.typeRadioGroup.setExclusive(True)
        self.selflocking.hide()
        self.antibacklash.hide()
        self.jacktypeLable.hide()
        self.endtypeLabel.hide()
        self.endfixLabel.hide()
        self.endfixComboBox.hide()
        self.warmLabel.hide()

        query = QSqlQuery()
        query.exec_()

        self.arrangeComboBox.addItem("- Select -")
        self.arrangeComboBox.addItem("1")
        self.arrangeComboBox.addItem("2")
        self.arrangeComboBox.addItem("3")
        self.arrangeComboBox.addItem("4")
        self.arrangeComboBox.addItem("6")
        self.arrangeComboBox.addItem("8")

        self.directionComboBox.addItem("- Select -")
        self.directionComboBox.addItem("Tension")
        self.directionComboBox.addItem("Compression")
        self.directionComboBox.addItem("Compression & Tension")
        
        self.endfixComboBox.addItem("- Select -")
        self.endfixComboBox.addItem("One end fixed & one end free")
        self.endfixComboBox.addItem("Pinned Ends")
        self.endfixComboBox.addItem("One end fixed & one end guided")

        self.travelComboBox.addItem("inch/min")
        self.travelComboBox.addItem("inch/sec")
        self.dutyComboBox.addItem("inches/hr")
        self.dutyComboBox.addItem("hrs/day")
        self.dutyComboBox.addItem("days/week")
        self.dutyComboBox.addItem("weeks/year")

        self.configurationComboBox.addItem("- Select -")
        self.configurationComboBox.addItem("Upright")
        self.configurationComboBox.addItem("Inverted")
        self.configurationComboBox.addItem("Upright Rotating")
        self.configurationComboBox.addItem("Inverted Rotating")
        self.configurationComboBox.addItem("Double Clevis")
        
        self.translatingComboBox.addItem("- Select -")
        self.translatingComboBox.addItem("Threaded End")
        self.translatingComboBox.addItem("Top Plate")
        self.translatingComboBox.addItem("Clevis End")
        
        self.keyoptionComboBox.addItem("- Select -")
        self.keyoptionComboBox.addItem("Not Keyed")
        self.keyoptionComboBox.addItem("Keyed")

        while self.assetModel.canFetchMore():
            self.assetModel.fetchMore()

        self.assetModel.setFilter("")
        self.assetModel.select()
        self.assetModel.submitAll()
        self.assetView.setVisible(False)

        self.resize(100, 100)
        #self.resize(self.width(), self.minimumSizeHint().height())

#*                                                                         *
#*                               * TAB 2 *                                 *
#*                             ITEM   FUNCTION                             *

    def arrangTextChanged(self):
        arran = str(self.arrangeComboBox.currentText())
        if arran == "1":
            self.arrangementLabel.hide()
            self.arrangementReadLabel.hide()
        elif arran in ("2", "3", "4", "6", "8"):
            self.arrangementReadLabel.setText("%s  Jacks" % arran)
            self.arrangementLabel.show()
            self.arrangementReadLabel.show()
        else:
            #self.arrangementReadLabel.setText("%s" % arran)
            self.arrangementLabel.show()
            self.arrangementReadLabel.hide()
        if arran <> self.selector[0]:
            self.dirty = True
            self.updateStatus("Change Jack Number")
        self.selector[0] = arran
            
    def dynTextChanged(self, text):
        if len(text)>0:
            self.dynloadReadLabel.setText(text+"  lbs.")
        else:
            self.dynloadReadLabel.setText(text)
        if str(text) <> self.selector[1]:
            self.dirty = True
            self.updateStatus("Change Dynamic Load")
        self.selector[1] = str(text) 

    def staTextChanged(self, text):
        if len(text)>0:
            self.staloadReadLabel.setText(text+"  lbs.")
        else:
            self.staloadReadLabel.setText(text)
        if str(text) <> self.selector[2]:
            self.dirty = True
            self.updateStatus("Change Static Load")
        self.selector[2] = str(text)

    def btnstate(self, b):
        if b.text() == "Machine Screw Jack":
            if b.isChecked() == True:
                self.typeReadLabel.setText(b.text())
                self.selector[3] = str(b.text())
        if b.text() == "Ball Screw Jack":
            if b.isChecked() == True:
                self.typeReadLabel.setText(b.text())
                self.selector[3] = str(b.text())

    def configTextChanged(self):
        config = str(self.configurationComboBox.currentText())
        self.configReadLabel.setText("%s" % config)
        if config <> self.selector[4]:
            self.dirty = True
            self.updateStatus("Change Configuration Type")
        self.selector[4] = config

    def transTextChanged(self):
        trans = str(self.translatingComboBox.currentText())
        self.transReadLabel.setText("%s" % trans)
        if trans <> self.selector[5]:
            self.dirty = True
            self.updateStatus("Change Translating Type")
        self.selector[5] = trans

    def keyedTextChanged(self):
        keyed = str(self.keyoptionComboBox.currentText())
        self.keyedReadLabel.setText("%s" % keyed)
        if keyed <> self.selector[6]:
            self.dirty = True
            self.updateStatus("Change keyed Option")
        self.selector[6] = keyed

    def radialTextChanged(self):
        radial = str(self.bearingoptionComboBox.currentText())
        self.radialReadLabel.setText("%s" % radial)
        if radial <> self.selector[7]:
            self.dirty = True
            self.updateStatus("Change Radial Bearing Options")
        self.selector[7] = radial

    def directionChanged(self):
        direction = str(self.directionComboBox.currentText())
        if direction in ("Tension", "Compression",
                         "Compression & Tension"):
            self.direction2Label.setText("%s" % direction)
            self.endfix2Label.setText("")
        if direction == "Tension":
            self.endfix2Label.setText("  /")
        elif direction == "- Select -":
            self.direction2Label.setText("")
            self.endfix2Label.setText("")
        if direction <> self.selector[7]:
            self.dirty = True
            self.updateStatus("Change Load Direction")
        self.selector[8] = direction

    def endfixChanged(self):
        endfix = str(self.endfixComboBox.currentText())
        if endfix in ("One end fixed & one end free",
                      "Pinned Ends",
                      "One end fixed & one end guided"):
            self.endfix2Label.setText("%s" % endfix)
        else:
            self.endfix2Label.setText("")
        if endfix <> self.selector[8]:
            self.dirty = True
            self.updateStatus("Change End Fixity Condition")
        self.selector[9] = endfix
            
    def travTextChanged(self, text):
        self.travelReadLabel.setText(text+"  in.")
        if str(text) <> self.selector[9]:
            self.dirty = True
            self.updateStatus("Change Travel Length")
        self.selector[10] = str(text)
        
    def speedTextChanged(self):
        speed = self.speedLineEdit.text()
        speedunit = str(self.travelComboBox.currentText())
        self.speedReadLabel.setText(speed + "  %s" % speedunit)
        if speed <> self.selector[10] or\
           speedunit <> self.selector[11]:
            self.dirty = True
            self.updateStatus("Change Travel Rate")
        self.selector[11] = str(speed)
        self.selector[12] = str(speedunit)
        
    def dutyTextChanged(self):
        duty =  self.dutyLineEdit.text()
        dutyunit = str(self.dutyComboBox.currentText())
        self.dutyReadLabel.setText(duty + "  %s" % dutyunit)
        if str(duty) <> self.selector[12] or\
           str(dutyunit) <> self.selector[13]:
            self.dirty = True
            self.updateStatus("Change Duty")
        self.selector[13] = str(duty)
        self.selector[14] = str(dutyunit)

    def setstopnutType(self):
        if self.stopnutmatComboBox.currentText() <> "Not Required":
            self.stopnutComboBox.show()
        else:
            self.stopnutComboBox.clear()
            self.stopnutComboBox.addItem("- Select -")
            self.stopnutComboBox.addItem("Extend & Retract")
            self.stopnutComboBox.addItem("Extend")
            self.stopnutComboBox.addItem("Retract")
            self.stopnutComboBox.hide()

#*                                                                         *
#*                           * TITLE FUNCTION *                            *
#*                                                                         *

    def createAction(self, text, slot=None, shortcut=None, icon=None,
                     tip=None, checkable=False, signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action


    def addActions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)


    def closeEvent(self, event):
        if self.okToContinue():
            settings = QSettings()
            filename = QVariant(QString(self.filename)) \
                    if self.filename is not None else QVariant()
            settings.setValue("LastFile", filename)
            recentFiles = QVariant(self.recentFiles) \
                    if self.recentFiles else QVariant()
            settings.setValue("RecentFiles", recentFiles)
            settings.setValue("MainWindow/Size", QVariant(self.size()))
            settings.setValue("MainWindow/Position",
                    QVariant(self.pos()))
            settings.setValue("MainWindow/State",
                    QVariant(self.saveState()))
        else:
            event.ignore()


    def okToContinue(self):
        if self.dirty:
            reply = QMessageBox.question(self,
                            "Jack Selector - Unsaved Changes",
                            "Save unsaved changes?",
                            QMessageBox.Yes|QMessageBox.No|
                            QMessageBox.Cancel)
            if reply == QMessageBox.Cancel:
                return False
            elif reply == QMessageBox.Yes:
                self.fileSave()
        return True


    def loadInitialFile(self):
        settings = QSettings()
        fname = unicode(settings.value("LastFile").toString())
        if fname and QFile.exists(fname):
            self.loadFile(fname)


    def updateStatus(self, message):
        self.statusBar().showMessage(message, 5000)
        valueList = []
        for i, value in enumerate(self.selector):
            if value == "- Select -":
                valueLength = len(value)-10
                valueList.append(valueLength)
            else:
                valueLength = len(value)
                valueList.append(valueLength)
        if self.filename is not None:
            self.setWindowTitle("Jack Selector - %s[*]" % \
                                os.path.basename(self.filename))
        elif valueList > 0:
            self.setWindowTitle("Jack Selector - Unnamed[*]")
        else:
            self.setWindowTitle("Jack Selector[*]")
        self.setWindowModified(self.dirty)

    #def updateImage(self):
    #        self.directionButton.setIcon(icons)
    #        self.directionButton.setIconSize(QSize(120,120))
        #self.connect(self.directionComboBox, SIGNAL("activated(int)"),
        #             self.setImage)
        #self.setImage()


    def updateFileMenu(self):
        self.fileMenu.clear()
        self.addActions(self.fileMenu, self.fileMenuActions[:-1])
        current = QString(self.filename) \
                if self.filename is not None else None
        recentFiles = []
        for fname in self.recentFiles:
            if fname != current and QFile.exists(fname):
                recentFiles.append(fname)
        if recentFiles:
            self.fileMenu.addSeparator()
            for i, fname in enumerate(recentFiles): # loop the recentfiles
                action = QAction(QIcon(":/icon.ico"), "&%d %s" % (
                        i + 1, QFileInfo(fname).fileName()), self)
                action.setData(QVariant(fname))
                self.connect(action, SIGNAL("triggered()"),
                             self.loadFile)
                self.fileMenu.addAction(action)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.fileMenuActions[-1])

    def updateSelector(self):
        #self.selector = []
    
        self.selector[0] = str(self.arrangeComboBox.currentText())
        self.selector[1] = str(self.dynloadReadLabel.text())
        self.selector[2] = str(self.staloadReadLabel.text())
        if self.acmeRadioButton.isChecked():
            self.selector.append("Machine Screw Jack")
        elif self.ballRadioButton.isChecked():
            self.selector.append("Ball Screw Jack")
        else:
            self.selector.append("")
        self.selector.append(str(self.configurationComboBox.currentText()))
        self.selector.append(str(self.translatingComboBox.currentText()))
        self.selector.append(str(self.keyoptionComboBox.currentText()))
        self.selector.append(str(self.bearingoptionComboBox.currentText()))
        self.selector.append(str(self.directionComboBox.currentText()))
        self.selector.append(str(self.endfixComboBox.currentText()))
        self.selector.append(str(self.travelLineEdit.text()))
        self.selector.append(str(self.speedLineEdit.text()))
        self.selector.append(str(self.travelComboBox.currentText()))
        self.selector.append(str(self.dutyLineEdit.text()))
        self.selector.append(str(self.dutyComboBox.currentText()))

        
#*                                                                         *
#*                           * FILE FUNCTION *                             *
#*                                                                         *


    def fileNew(self):
        if not self.okToContinue():
            return
        self.clearAll()
        self.selector = [""] * 15
        self.filename = None
        self.dirty = True
        
        #for i, value in enumerate(self.selector):
        #    if len(value) == 0:
        #        self.entry = False
        #    else:
        #        self.entry = True
        #if not self.entry:
        #    self.dirty = False

        self.updateStatus("Created new file")
            
        #self.setWindowTitle("Jack Selection - New file")
        

    def fileOpen(self):
        if not self.okToContinue():
            return
        dir = os.path.dirname(self.filename) \
                if self.filename is not None else "."
        fname = unicode(QFileDialog.getOpenFileName(self,
                        "Jack Selection - Choose file", dir,
                        "Jack Selection files (*.dsj)"))
        if fname:
            self.loadFile(fname)


    def loadFile(self, fname=None):
        if fname is None:
            action = self.sender()
            if isinstance(action, QAction):
                fname = action.data().toString()
                if not self.okToContinue():
                    return
            else:
                return
        if fname:
            self.filename = None
            #self.selectors = open(fname).read()  #TEST
            if self.filename:
                message = "Failed to read %s" % fname
            else:
                self.addRecentFile(fname)
                self.dirty = False
                self.filename = fname
                self.selector = open(fname).read().split(",") #TEST
                self.arrangeComboBox.setCurrentIndex(\
                    self.arrangeComboBox.findText(self.selector[0]))
                self.dynloadLineEdit.setText(self.selector[1])
                self.staloadLineEdit.setText(self.selector[2])
                if self.selector[3] == "Machine Screw Jack":
                    self.acmeRadioButton.setChecked(True)
                elif self.selector[3] == "Ball Screw Jack":
                    self.ballRadioButton.setChecked(True)
                elif self.selector[3] == "":
                    self.acmeRadioButton.setChecked(False)
                    self.ballRadioButton.setChecked(False)
                self.configurationComboBox.setCurrentIndex(\
                    self.configurationComboBox.findText(self.selector[4]))
                if self.selector[4] in ("Upright", "Inverted"):
                    self.translatingComboBox.show()
                    self.translatingLabel.show()
                    self.keyoptionLabel.show()
                    self.keyoptionComboBox.show()
                    self.bearingoptionLabel.hide()
                    self.bearingoptionComboBox.hide()
                    self.radialLabel.hide()
                    self.radialReadLabel.hide()
                    self.translating1Label.show()
                    self.transReadLabel.show()
                    self.keyedLabel.show()
                    self.keyedReadLabel.show()
                elif self.selector[4] in ("Upright Rotating",
                                          "Inverted Rotating"):
                    self.translatingComboBox.hide()
                    self.translatingLabel.hide()
                    self.keyoptionLabel.hide()
                    self.keyoptionComboBox.hide()
                    self.bearingoptionLabel.show()
                    self.bearingoptionComboBox.show()
                    self.translating1Label.hide()
                    self.transReadLabel.hide()
                    self.keyedLabel.hide()
                    self.keyedReadLabel.hide()
                    self.radialLabel.show()
                    self.radialReadLabel.show()
                self.translatingComboBox.setCurrentIndex(\
                    self.translatingComboBox.findText(self.selector[5]))
                self.keyoptionComboBox.setCurrentIndex(\
                    self.keyoptionComboBox.findText(self.selector[6]))
                self.bearingoptionComboBox.setCurrentIndex(\
                    self.bearingoptionComboBox.findText(self.selector[7]))
                self.directionComboBox.setCurrentIndex(\
                    self.directionComboBox.findText(self.selector[8]))                
                self.endfixComboBox.setCurrentIndex(\
                    self.endfixComboBox.findText(self.selector[9]))
                self.travelLineEdit.setText(self.selector[10])
                self.speedLineEdit.setText(self.selector[11])
                self.travelComboBox.setCurrentIndex(\
                    self.travelComboBox.findText(self.selector[12]))
                self.dutyLineEdit.setText(self.selector[13])
                self.dutyComboBox.setCurrentIndex(\
                    self.dutyComboBox.findText(self.selector[14]))

                message = "Loaded %s" % os.path.basename(fname)
            self.updateStatus(message)


    def addRecentFile(self, fname):
        if fname is None:
            return
        if not self.recentFiles.contains(fname):
            self.recentFiles.prepend(QString(fname))
            while self.recentFiles.count() > 3:
                self.recentFiles.takeLast()

    def fileSave(self):
        boolen = False
        #print self.selector
        #for i, value in enumerate(self.selector):
        for item in self.selector[0:11]:
            if len(item) == 0:
                boolen = False
            else:
                boolen = True
            self.entry = self.entry or boolen
        if not self.entry:
            return
        arran = str(self.arrangeComboBox.currentText())
        dyn = str(self.dynloadReadLabel.text()).split(" ")[0]
        sta = str(self.staloadReadLabel.text()).split(" ")[0]
        if self.acmeRadioButton.isChecked():
            jacktype = "Machine Screw Jack"
        elif self.ballRadioButton.isChecked():
            jacktype = "Ball Screw Jack"
        else:
            jacktype = ""
        config = str(self.configurationComboBox.currentText())
        trans = str(self.translatingComboBox.currentText())
        keyed = str(self.keyoptionComboBox.currentText())
        bear = str(self.bearingoptionComboBox.currentText())
        direction = str(self.directionComboBox.currentText())
        endfix = str(self.endfixComboBox.currentText())
        travel = str(self.travelReadLabel.text()).split(" ")[0]
        speed = str(self.speedLineEdit.text())
        speedunit = str(self.travelComboBox.currentText())
        duty = str(self.dutyLineEdit.text())
        dutyunit = str(self.dutyComboBox.currentText())
        if self.filename is None:
            self.fileSaveAs()
        else:
            print self.selector
            error = None
            fh = None
            try:
                fh = codecs.open(unicode(self.filename), "w", CODEC)
                fh.write(u"%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" %\
                         (arran, dyn, sta, jacktype, config, trans,
                          keyed, bear, direction, endfix, travel, speed,
                          speedunit, duty, dutyunit))
            except (IOError, OSError), e:
                error = "Failed to save: %s" % e
                self.updateStatus("Failed to save %s" % self.filename)
            finally:
                if fh is not None:
                    fh.close()
                if error is not None:
                    return False, error
                self.dirty = False
                self.updateStatus("Saved as %s" % self.filename)
                

        #    with open(self.filename, "w") as output:
        #        output.write(str(values))
        #print output
        #    if self.selector.save(self.filename, None):
        #        self.updateStatus("Saved as %s" % self.filename)
        #        self.dirty = False
        #    else:
        #        self.updateStatus("Failed to save %s" % self.filename)


    def fileSaveAs(self):
        if not self.selector:
            return
        fname = self.filename if self.filename is not None else "."
        fname = unicode(QFileDialog.getSaveFileName(self,
                        "Jack Selection - Save file", fname,
                        "Jack Selection files (*.dsj)"))
        if fname:
            if "." not in fname:
                fname += ".dsj"
            self.addRecentFile(fname)
            self.filename = fname
            self.fileSave()

    #def filePreview(self):
    #    if self.image.isNull():
    #       return
    #    if self.printer is None:
    #        self.printer = QPrinter(QPrinter.HighResolution)
    #        self.printer.setPageSize(QPrinter.Letter)
    #    form = QPrintDialog(self.printer, self)
    #    if form.exec_():
    #        painter = QPainter(self.printer)
    #        rect = painter.viewport()
    #        size = self.image.size()
    #        size.scale(rect.size(), Qt.KeepAspectRatio)
    #        painter.setViewport(rect.x(), rect.y(), size.width(),
    #                            size.height())
    #        painter.drawImage(0, 0, self.image)

    def filePrint(self):
        html = u""
        date = QDate.currentDate().toString(DATE_FORMAT)
        html += ("<h1 align=left>Jack  Selection"
                 "<img src='./images/logo_36.jpg' align=right></h1>")

        html += ("<h3 align=left>"
                 "<p>&nbsp;</p><p>&nbsp;</p>"
                 "<p>&nbsp;</p>"
                 "<p><font size=4>%s</font></p>"
                 "<p><font size=4><b>www.duffnorton.com</b>"
                 "</font></p></h3>") % (date)
    
        html += ("<font size=4> Thank you for your interest "
                 "for Duff Norton products. The following "
                 "contains your requested information "
                 "regarding our product and "
                 "specification.</font></p>")
        
        html += ("</p><p>&nbsp;</p><p>"
                 "<table width=100% cellpadding=2 cellspacing=2>")
        
        html += ("<font size=4><b>INPUT</b></font>")
        
        arranType = self.arrangeComboBox.currentText()
        if arranType in ("2", "3", "4", "6", "8"):
            html += ("<tr><td align=left>Jack Arrangement:</td>"
                     "<td colspan=2><b>%s Jacks</b></td></tr>") \
                     % (arranType)
        
        html += ("<tr><td align=left>Dynamic Load:</td>"
                 "<td colspan=2><b>%s</b></td>") \
                 % (self.dynloadReadLabel.text())
        html += ("<td align=left>Load Direction:</td>"
                 "<td colspan=2><b>%s</b></td></tr>") \
                 % (self.direction2Label.text())
        html += ("<tr><td align=left>Static Load:</td>"
                 "<td colspan=2><b>%s</b></td>") \
                 % (self.staloadReadLabel.text())
        html += ("<td align=left>Column End Fixity:</td>"
                 "<td colspan=2><b>%s</b></td></tr>") \
                 % (self.endfix2Label.text())
        html += ("<tr><td align=left>Jack Type:</td>"
                 "<td colspan=2><b>%s</b></td>") \
                 % (self.typeReadLabel.text())
        html += ("<td align=left>Total Travel Length:</td>"
                 "<td colspan=2><b>%s</b></td></tr>") \
                 % (self.travelReadLabel.text())
        if self.configReadLabel.text() in ("Upright",
                                           "Inverted",
                                           "Upright Rotating",
                                           "Inverted Rotating",
                                           "Double Clevis"):
            html += ("<tr><td align=left>Configuration:</td>"
                     "<td colspan=2><b>%s</b></td>") \
                     % (self.configReadLabel.text())
        else:
            html += ("<tr><td align=left>Configuration:</td>"
                     "<td colspan=2><b>%s</b></td>") \
                     % ("")
            
        html += ("<td align=left>Input Travel Rate:</td>"
                 "<td colspan=2><b>%s</b></td></tr>") \
                 % (self.speedReadLabel.text())

        transType = self.configurationComboBox.currentText()
        if transType not in ("Upright Rotating",
                             "Inverted Rotating",
                             "Double Clevis"):
            if self.transReadLabel.text() in ("Threaded End",
                                              "Top Plate",
                                              "Clevis End"):
                html += ("<tr><td align=left>Translating:</td>"
                         "<td colspan=2><b>%s</b></td>") \
                         % (self.transReadLabel.text())
                html += ("<td align=left>Duty:</td>"
                         "<td colspan=2><b>%s</b></td></tr>") \
                         % (self.dutyReadLabel.text())
                html += ("<tr><td align=left>Keyed:</td>"
                         "<td colspan=2><b>%s</b></td></tr>")\
                         % (self.keyedReadLabel.text())
                html += ("</table></p>")
            else:
                html += ("<tr><td align=left>Translating:</td>"
                         "<td colspan=2><b>%s</b></td>") \
                         % ("")
                html += ("<td align=left>Duty:</td>"
                         "<td colspan=2><b>%s</b></td></tr>") \
                         % (self.dutyReadLabel.text())
                html += ("<tr><td align=left>Keyed:</td>"
                         "<td colspan=2><b>%s</b></td></tr>")\
                         % (self.keyedReadLabel.text())
                html += ("</table></p>")
        elif transType == "Double Clevis":
            html += ("<tr><td align=left>Duty:</td>"
                     "<td colspan=2><b>%s</b></td></tr>") \
                     % (self.dutyReadLabel.text())
            html += ("</table></p>")
        else:
            html += ("<tr><td align=left>Bearing Option:</td>"
                     "<td colspan=2><b>%s</b></td>")\
                     % (self.radialReadLabel.text())
            html += ("<td align=left>Duty:</td>"
                     "<td colspan=2><b>%s</b></td></tr>") \
                     % (self.dutyReadLabel.text())
            html += ("</table></p>")

        index1 = self.assetView.currentIndex()
        record1 = self.assetModel.record(index1.row())
        seledata = record1.value("selection").toString()
        
        html += ("</table></p>")
        
        html += ("<p><table width=100% cellpadding=2 cellspacing=2>"
                 "<font size=4><b>MODEL DETAILS</b></font>")
        
        html += ("<tr><td><b><font color=red>"
                 "<u> %s </u></b></td></tr>") \
                 % (seledata)
        index2 = self.logView.currentIndex()
        record2 = self.logModel.record(index2.row())
        capadata = record2.value("capacity").toString()
        ratodata = record2.value("sratio").toString()
        mahpdata = record2.value("hptext").toString()
        diamdata = record2.value("sdiameter").toString()
        rootdata = record2.value("srootdia").toString()
        leaddata = record2.value("slead").toString()
        tplbdata = record2.value("storqueperlbs").toString()
        tnlodata = record2.value("storquenoload").toString()
        tflodata = record2.value("storquefullload").toString()
        turndata = record2.value("sturnsofworm").toString()
        html += ("<tr><td align=left>Capacity:</td>"
                 "<td colspan=2><b>%s</b></td>"
                 "<td align=left>Max Input HP:</td>"
                 "<td colspan=2><b>%s</b></td></tr>"

                 "<tr><td align=left>Ratio:</td>"
                 "<td colspan=2><b>%s</b></td>"
                 "<td align=left>Input Turns per 1 in.:</td>"
                 "<td colspan=2><b>%s</b></td></tr>"
                 
                 "<tr><td align=left>Diameter:</td>"
                 "<td colspan=2><b>%s</b></td>"
                 "<td align=left>Torque to Raise 1 lbs.:</td>"
                 "<td colspan=2><b>%s</b></td></tr>"
            
                 "<tr><td align=left>Root Diameter:</td>"
                 "<td colspan=2><b>%s</b></td>"
                 "<td align=left>Worm Torque at No Load:</td>"
                 "<td colspan=2><b>%s</b></td></tr>"

                 "<tr><td align=left>Screw Lead:</td>"
                 "<td colspan=2><b>%s</b></td>"
                 "<td align=left>Full Load Torque:</td>"
                 "<td colspan=2><b>%s </b></td></tr>") % (
                     capadata, mahpdata, ratodata, turndata,
                     diamdata, tplbdata, rootdata, tnlodata, 
                     leaddata, tflodata)
        html += ("</table></p>")

        html += ("<p><table width=100% cellpadding=2 cellspacing=2>"
                 "<font size=4><b>MOTOR REQUIREMENTS</b></font>")

        tqreqdata = record1.value("torqueperjack").toString()
        hpreqdata = record1.value("hpperjack").toString()
        tqtotdata = record1.value("torquetotal").toString()
        hptotdata = record1.value("hptotal").toString()
        tratedata = record1.value("travelrate").toString()

        if self.arrangeComboBox.currentText() == "1":
            html += ("<tr><td align=left>Torque Required per Jack:</td>"
                     "<td colspan=2><b>%s in-lbs.</b></td>"

                     "<td align=left>HP Required per Jack:</td>"
                     "<td colspan=2><b>%s HP</b></td></tr>"

                     "<tr><td align=left>Travel Rate:</td>"
                     "<td colspan=2><b>%s RPM</b></td></tr>")\
                     % (tqreqdata, hpreqdata, tratedata)
        else:
            html += ("<tr><td align=left>Torque Required per Jack:</td>"
                     "<td colspan=2><b>%s in-lbs.</b></td>"

                     "<td align=left>HP Required per Jack:</td>"
                     "<td colspan=2><b>%s HP</b></td></tr>"

                     "<tr><td align=left>Total Torque Required:</td>"
                     "<td colspan=2><b>%s in-lbs.</b></td>"

                     "<td align=left>Total HP Required:</td>"
                     "<td colspan=2><b>%s HP</b></td></tr>"

                     "<tr><td align=left>Travel Rate:</td>"
                     "<td colspan=2><b>%s RPM</b></td></tr>")\
                     % (tqreqdata, hpreqdata, tqtotdata,
                        hptotdata, tratedata)

        maxInPerHour = record1.value("maxinperhour").toString()
        dutyCycle = record1.value("dutycycle").toString()

        html += ("<p><table width=100% cellpadding=2 cellspacing=2>"
                 "<font size=4><b>REFERENCE</b></font>")

        html += ("<tr><td align=left>Max Travel:</td>"
                 "<td colspan=2><b>%s in/hr</b></td>"
                 
                 "<td align=left>Duty Cycle:</td>"
                 "<td colspan=2><b>%s %%</b></td></tr>")\
                 % (maxInPerHour, dutyCycle)
        
        html += ("</table></p>")

        bootdata = self.bootComboBox.currentText()
        paintdata = self.paintComboBox.currentText()
        stopNutMatdata = self.stopnutmatComboBox.currentText()
        if self.stopnutComboBox.currentText() == "- Select -":
            stopNutdata = ""
        else:
            stopNutdata = self.stopnutComboBox.currentText()
        greasedata = self.greaseComboBox.currentText()

        html += ("<p><table width=100% cellpadding=2 cellspacing=2>"
                 "<font size=4><b>ACCESSORIES</b></font>")

        html += ("<tr><td align=left>Boot:</td>"
                 "<td colspan=2><b>%s </b></td>"
                 
                 "<td align=left>Paint:</td>"
                 "<td colspan=2><b>%s </b></td></tr>"

                 "<tr><td align=left>Stop Nut:</td>"
                 "<td colspan=2><b>%s ; %s</b></td>"
                 
                 "<td align=left>Grease:</td>"
                 "<td colspan=2><b>%s </b></td></tr>")\
                 % (bootdata, paintdata, stopNutMatdata, \
                    stopNutdata, stopNutMatdata)
        
        html += ("<p>&nbsp;</p>")
        html += ("<p><font size=4>Should you have any further"
                 " questions, please contact our Application Engineer or"
                 " Customer service at 800-477-5002 or 704-588-4610 "
                 "and send email to duffnorton@cmworks.com</p>"
                 "<p>"
                 "<font size=4> We appreciate your interest"
                 " in our products.<br>"
                 "</font></p>")

        doc = QTextDocument()
        doc.setHtml(html) 
        dialog = QPrintPreviewDialog()
        dialog.paintRequested.connect(doc.print_)
        dialog.setWindowTitle("%s Print" % QApplication.applicationName())
        dialog.exec_()

    def printPreview(self, printer):
        self.image.print_(printer)

    def duffPage(self):
        webbrowser.open('http://duffnorton.com/')

    def viewLiterature(self):
        webbrowser.open('http://duffnorton.com/category.aspx?id=7788')

    def viewOnlineModel(self):
        webbrowser.open('http://productpage.3dpublisher.net/'
                        '3dproductpage/QSvalidlogin.asp?GUID=1130881382437')

    def requestQuote(self):
        form = sendquote.SendQuote(self)
        form.show()
        
    def showImage(self, percent=None):
        if self.image.isNull():
            return
        if percent is None:
            percent = self.zoomSpinBox.value()
        factor = percent / 100.0
        width = self.image.width() * factor
        height = self.image.height() * factor
        image = self.image.scaled(width, height, Qt.KeepAspectRatio)
        self.imageLabel.setPixmap(QPixmap.fromImage(image))


    def helpAbout(self):
        QMessageBox.about(self, "About Jack Selector",
                """<b>Jack Selector</b> %s
                <p>Copyright &copy; 2017 Duff Norton Ltd. 
                All rights reserved.
                <p>This application can be used to perform
                Screw Jack Selection.
                <hr><br>
                <img src=":/logo_361.jpg"/>
                """ % (
                __version__, ))


    def helpHelp(self):
        form = helpform.HelpForm("index.html", self)
        form.show()

    def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except AttributeError:
                base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
        

def main():
    app = QApplication(sys.argv)
    app.setOrganizationName("Duff Norton Ltd.")
    app.setOrganizationDomain("duffnorton.com")
    app.setApplicationName("Jack Selector")
    app.setWindowIcon(QIcon(":/icon.png"))

    form = MainWindow()
    form.resize(400,580)
    form.show()
    app.exec_()


main()

