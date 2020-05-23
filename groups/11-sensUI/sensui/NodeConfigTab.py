from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QLabel, QLineEdit, QDoubleSpinBox, QCheckBox, QComboBox, QPushButton
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QAbstractItemView, QHBoxLayout, QFrame, QGridLayout
from PyQt5.QtCore import QVariant, Qt
from PyQt5 import uic
import os

from sensui.Node import Node
from sensui.Tools import Tools

class NodeConfigTab(QWidget):

    def __init__(self, nodes, callbackModified=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "NodeConfigTab.ui"), self)

        self.__callbackModified = callbackModified

        self.timeUnits = {"Sekunden": 1, "Minuten": 60, "Stunden": 3600, "Tage":86400}

        self.__sensorSelectCheckboxes = {}

        self.__nodes = nodes

        self.__nodeConfigSelectedId = None
        self.__initNodeConfigTab()
        self.nodeConfigUpdateList()

    '''
        NodeConfig-Tab Methods
    '''
    def __initNodeConfigTab(self):
        # Node Config
        self.uiNodeConfigName = self.findChild(QLineEdit, "lineEditConfigNodeName")
        self.uiNodeConfigId = self.findChild(QLabel, "labelConfigNodeId")

        self.uiNodeConfigSave = self.findChild(QPushButton, "pushButtonConfigNodeSave")
        self.uiNodeConfigUpdate = self.findChild(QPushButton, "pushButtonConfigNodeUpdate")
        self.uiNodeConfigList = self.findChild(QListWidget, "listWidgetConfigNodeList")

        self.uiNodeConfigSensorContainer = self.findChild(QFrame, "frameSensors")

        self.uiNodeConfigPosition = {
            Node.POSITION_LATITUDE: self.findChild(QDoubleSpinBox, "doubleSpinBoxConfigNodePositionLatitude"),
            Node.POSITION_LONGITUDE: self.findChild(QDoubleSpinBox, "doubleSpinBoxConfigNodePositionLongitude"),
            Node.POSITION_ELEVATION: self.findChild(QDoubleSpinBox, "doubleSpinBoxConfigNodePositionAltitude")
        }

        self.uiNodeConfigInterval = self.findChild(QDoubleSpinBox, "doubleSpinBoxConfigNodeInterval")
        self.nodeIntervalTimeUnit = self.findChild(QComboBox, "comboBoxConfigNodeIntervalTimeUnit")

        self.uiNodeConfigList.setSelectionMode(QAbstractItemView.SingleSelection)
        self.uiNodeConfigList.itemSelectionChanged.connect(self.__nodeConfigListSelectedHandler)
        self.uiNodeConfigSave.clicked.connect(self.__nodeConfigSaveCurrentSelected)

        self.uiNodeConfigSensorContainer.setLayout(QGridLayout())

        self.__nodeConfigFillTimeComboBox()
        self.nodeConfigBuildSensorTypeSelector()

        self.nodeConfigToggleControls(False)

    def nodeConfigBuildSensorTypeSelector(self):
        layout = self.uiNodeConfigSensorContainer.layout()
        row = 0
        col = 0
        for id, quantity in Tools.measurementSizes.items():
            checkbox = QCheckBox(f"{quantity.name} ({quantity.unit})")
            self.__sensorSelectCheckboxes[id] = checkbox
            layout.addWidget(checkbox, row, col)
            if col < 1:
                col += 1
            else:
                col = 0
                row += 1


    def nodeConfigIsViewSelected(self):
        if self.__nodeConfigSelectedId is None or self.__nodeConfigSelectedId not in self.__nodes:
            return False

        return True

    def nodeConfigCurrentSelectedNode(self):
        if not self.nodeConfigIsViewSelected():
            return None

        return self.__nodes[self.__nodeConfigSelectedId]

    def nodeConfigSave(self):
        if self.__callbackStore is not None:
            self.__callbackStore(self.__nodes, NodeConfigTab.FILENAME_CONFIG_NODES)

    def __nodeConfigListSelectedHandler(self):
        items = self.uiNodeConfigList.selectedItems()
        if len(items) == 1 and items[0] is not None:
            id = items[0].data(Qt.UserRole)
            if id is not None and id in self.__nodes:
                self.__nodeConfigSelectedId = str(id)
            else:
                self.__nodeConfigSelectedId = None
            self.__nodeConfigDisplayCurrentSelected()

    def __nodeConfigShowInList(self, node):
        if node is None:
            return
        item = QListWidgetItem(node.name)
        item.setData(Qt.UserRole, QVariant(str(node.id)))
        self.uiNodeConfigList.addItem(item)

    def nodeConfigUpdateList(self):
        if self.__nodes is None:
            return

        self.uiNodeConfigList.clear()
        for node in self.__nodes.values():
            self.__nodeConfigShowInList(node)

    def nodeConfigAdd(self, node):
        if node is None:
            return

        self.__nodes[str(node.id)] = node
        self.__nodeConfigShowInList(node)

    def __nodeConfigSelectedIntervalTime(self):
        timeUnit = self.nodeIntervalTimeUnit.currentText()
        interval = self.uiNodeConfigInterval.value()
        if timeUnit in self.timeUnits and int(interval) == interval:
            timeMuliplier = self.timeUnits[timeUnit]
            return interval * timeMuliplier
        return None

    def __nodeConfigSaveCurrentSelected(self):
        node = self.nodeConfigCurrentSelectedNode()

        if node is None:
            return False

        node.name = self.uiNodeConfigName.text()

        interval = self.__nodeConfigSelectedIntervalTime()
        if interval is not None:
            node.interval = interval

        for p in Node.POSITION:
            node.position[p] = self.uiNodeConfigPosition[p].value()

        #for s in Node.SENSORS:
        #    node.sensors[s] = self.uiNodeConfigSensorsSelect[s].isChecked()

        for id, checkbox in self.__sensorSelectCheckboxes.items():
            node.setSensor(id, checkbox.isChecked())

        # Update Name on List
        items = self.uiNodeConfigList.selectedItems()
        if len(items) == 1:
            items[0].setText(node.name)

        self.__nodes[self.__nodeConfigSelectedId] = node

        if self.__callbackModified:
            self.__callbackModified()
        #self.nodeConfigSave()

        return True

    def nodeConfigToggleControls(self, enabled):
        if enabled is None:
            return

        self.uiNodeConfigName.setEnabled(enabled)

        self.uiNodeConfigSave.setEnabled(enabled)
        self.uiNodeConfigUpdate.setEnabled(enabled)

        self.uiNodeConfigInterval.setEnabled(enabled)
        self.nodeIntervalTimeUnit.setEnabled(enabled)

        for field in self.uiNodeConfigPosition.values():
            field.setEnabled(enabled)

        for field in self.__sensorSelectCheckboxes.values():
            field.setEnabled(enabled)

        #for field in self.uiNodeConfigSensorsSelect.values():
        #    field.setEnabled(enabled)

    def __nodeConfigFillTimeComboBox(self):
        self.nodeIntervalTimeUnit.addItems(self.timeUnits.keys())
        self.nodeIntervalTimeUnit.setCurrentIndex(0)

    def __nodeConfigDisplayCurrentSelected(self):
        self.nodeConfigDisplay(self.nodeConfigCurrentSelectedNode())


    def nodeConfigDisplay(self, node):
        if node is None or node.id is None:
            self.nodeConfigToggleControls(False)
            return

        self.uiNodeConfigId.setText(str(node.id))

        if node.name is not None:
            self.uiNodeConfigName.setText(node.name)

        if node.position is not None:
            for p in Node.POSITION:
                if node.position[p] is not None:
                    self.uiNodeConfigPosition[p].setValue(node.position[p])

        if node.interval is not None:
            self.uiNodeConfigInterval.setValue(node.interval)
            self.nodeIntervalTimeUnit.setCurrentIndex(0)

        nodeSensors = node.getSensors()
        for id, checkbox in self.__sensorSelectCheckboxes.items():
            if id in nodeSensors:
                checkbox.setChecked(nodeSensors[id])
            else:
                checkbox.setChecked(False)

        self.nodeConfigToggleControls(True)