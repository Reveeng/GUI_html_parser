import QtQuick 2.12
import QtQuick.Controls 2.12

Item {
    property alias header : headText.text
    property alias value : valueText.text
    width: (headText.width > 40) || (valueText.width > 40) ?
                headText.width > valueText.width ?
                   headText.width+10 :
                   valueText.width+10
                : 40
    Rectangle{
        id:headerBack
        color: "lightgrey"
        border.width: 1
        border.color: "black"
        height:parent.height/2-1
        width:parent.width
        anchors{
            top:parent.top
            topMargin: 1
            left:parent.left
            leftMargin: 1
        }
        Text{
            id:headText
            font.pixelSize: 14
            anchors.centerIn: parent
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignHCenter
            clip:true
        }
    }
    Rectangle{
        id:valueBack
        color: "white"
        border.width: 1
        border.color: "black"
        height:parent.height/2-1
        width:parent.width
        anchors{
            top:headerBack.bottom
            left:parent.left
            leftMargin: 1
        }
        Text{
            id:valueText
            font.pixelSize: 14
            anchors.centerIn: parent
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignHCenter
            clip:true
        }
    }
}
