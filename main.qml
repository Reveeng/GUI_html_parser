import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Controls 2.12

Window {
    width: 640
    height: 480
    visible: true
    color: "grey"
    title: qsTr("HTML parser")

    Button {
        id: button
        anchors.top:textEdit.bottom
        anchors.topMargin: 5
        anchors.right: textEdit.right
        width: 150
        height: 20
        text: "Начать парсинг"
        onClicked: {
            if (textEdit.text.length != 0){
                if (parser.parse_html(textEdit.text)){
                    parser.get_tags_stats_recursive()
                    console.log("parsing poshel")
//                    console.log(data)
//                    tableView.model = data
//                    parser.get_all_images()
                }
//                console.log("zero data "+data[0])
//                for (var key in data){
//                    var value = data[key]
//                    console.log(key, value)
//                }
            }
        }
    }

    Connections{
        target:parser
        onFinished:{
            console.log("parse finished")
            var data = Object.entries(parser.get_stat())
            tableView.model = data
        }
    }



    Rectangle{
        id: textEdit
        property alias text: ed.text
        width: 254
        height: 40
        color:"white"
        anchors{
            left:parent.left
            leftMargin: 10
            top:parent.top
            topMargin: 10
        }
        TextEdit {
            id:ed
            anchors{
                left:parent.left
                leftMargin: 5
                top:parent.top
                bottom:parent.bottom
                right:parent.right
            }
            clip: true
            font.pixelSize: 16
            horizontalAlignment: Text.AlignLeft
            verticalAlignment: Text.AlignVCenter
        }
    }

    ScrollView{
        id:scView
        height:100
//        width:parent.width-20
        background: Rectangle{
            anchors.fill:parent
            color:"white"
        }
        clip: true
        anchors{
            right:parent.right
            rightMargin: 10
            left:parent.left
            leftMargin: 10
            top: button.bottom
            topMargin: 10
        }
        ScrollBar.horizontal.policy:ScrollBar.AlwaysOf
        ScrollBar.horizontal.interactive:false
        Text{
            id:errText
            anchors.centerIn: parent
            font.pixelSize: 16
            text: "Нет данных"
            visible: true
        }

        ListView{
            id:tableView
            height:parent.height
            orientation: ListView.Horizontal
            width:parent.width
            spacing: 0
            onModelChanged:{
                if (model.length != 0)
                    errText.visible = false
                console.log("model lenght "+model.length)
            }
            delegate: TableItem{
                height:scView.height
//                width:40
                header: tableView.model[index][0]
                value:tableView.model[index][1]
//                Component.onCompleted: console.log("item created "+height + width)
            }
            onContentXChanged: {
                var  pos = scView.ScrollBar.horizontal.position
            }
        }
    }


}
