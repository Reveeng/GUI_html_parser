import QtQuick 2.12
import QtQuick.Controls 2.12

Item {
    property alias header : headText.text
    property alias value : valueText.text
    Rectangle{
        color: "transparent"
        border.width: 1
        border.color: "black"
        height:parent.height
        width:parent.width
        Rectangle{
            id:headerBack
            color: "lightgrey"
            height:parent.height-1
            width:parent.width/2
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
            height:parent.height-1
            width:parent.width/2
            anchors{
                verticalCenter: headerBack.verticalCenter
                left:headerBack.right
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

}
