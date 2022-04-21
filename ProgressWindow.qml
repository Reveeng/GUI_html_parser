import QtQuick 2.0
import QtQuick.Controls 2.12

Rectangle {
    property alias value: pB.value
    property alias text:txt.text
    width:parent.width-20
    height:70
    anchors.centerIn: parent
    border.color:"black"
    border.width:1
    Text{
        id:txt
        anchors{
            top:parent.top
            topMargin: 5
            horizontalCenter: parent.horizontalCenter
        }
    }

    ProgressBar{
        id:pB
        value: 0
        anchors{
            top:txt.bottom
            right:parent.right
            left:parent.left
            margins: 5
        }
        width:parent.width
    }
}
