import QtQuick 2.0
import QtQuick.Controls 2.12

Item {
    Rectangle{
        id: textEdit
        property alias text: ed.text
        width: 500
        height: 40
        color:"white"
        anchors{
            horizontalCenter: parent.horizontalCenter
            top:parent.top
            topMargin: 20
        }
        TextEdit {
            id:ed
            property string placeholderText: "Введите вдресс (URL)"
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
            Text{
                font.pixelSize: 18
                text:ed.placeholderText
                color: "#aaa"
                visible: !ed.text && !ed.activeFocus
                anchors.verticalCenter: parent.verticalCenter
            }
        }
    }


    Button {
        id: button
        anchors.top:textEdit.bottom
        anchors.topMargin: 10
        anchors.horizontalCenter: parent.horizontalCenter
        width: 200
        height: 30
        text: "Начать парсинг"
        font.pixelSize: 16
        onClicked: {
//            По нажатию кнопки берет текст из textEdit и передает в класс parser url. И вызывает функцию parse
            if (textEdit.text.length != 0){
                if (parser.parse_html(textEdit.text)){
//                    parser.get_tags_stats()
                    console.log("parsing poshel")
                    pw.visible = true
                }
            }
        }
    }
    Button{
        id:drawGraph
        anchors.top:button.bottom
        anchors.topMargin: 10
        anchors.horizontalCenter: parent.horizontalCenter
        width:200
        height:30
        text: "Показать граф"
        font.pixelSize: 16
        enabled: false
        onClicked: {
            parser.show_graph()
        }
    }
    Rectangle{
        id:tagCountT
        height:15
        width:tag.width+tgCount.width+10
        color: "white"
        anchors{
            top: drawGraph.bottom
            topMargin: 5
            left:parent.left
            leftMargin: 10
        }
        Text{
            id:tag
            text:"Колличество тегов:"
            font.pixelSize: 14
            anchors{
                verticalCenter: parent.verticalCenter
                left: parent.left
//                leftMargin: 5
            }
        }
        Text{
            id:tgCount
            text: "0"
            font.pixelSize: 14
            anchors{
                verticalCenter: parent.verticalCenter
                left:tag.right
                leftMargin: 5
            }
        }

    }


//    Соединям сигнал finished от парсера с функцией которая написана.
    Connections{
        target:parser
        function onFinished() {
//            Преобразуем JSObject полученный после вызова функцию get_stat в массив data, где один элемент это [tag, count]
            var tags = parser.get_stat_results()
//            Задаем tableView модель data
            ftable.model = Object.entries(tags[0])
            stable.model = Object.entries(tags[1])
            ttable.model = Object.entries(tags[2])
            drawGraph.enabled = true
            pw.visible = false
            var tag_count = parser.get_tags_count()
            tgCount.text = tag_count
        }
        function onParseProgressChanged(progress){
            pw.value = progress
        }
    }
    ProgressWindow{
        id:pw
        text:"Идет парсинг сайта. Подождите..."
        visible:false
    }

    Item{
        anchors{
            top: tagCountT.bottom
            bottom: parent.bottom
            right: parent.right
            left: parent.left
            margins: 5
        }
        clip: true
        ListView{
            id:ftable
            width:200
            height: parent.height
            anchors{
                left:parent.left
                leftMargin:5
            }
            delegate: TableItem{
                width:parent.width
                height:15
                header: ftable.model[index][0]
                value: ftable.model[index][1]
            }
        }

        ListView{
            id:stable
            width:200
            height:parent.height
            anchors{
                left:ftable.right
                leftMargin: 10
            }
            delegate: TableItem{
                width:parent.width
                height:15
                header: stable.model[index][0]
                value: stable.model[index][1]
            }
        }

        ListView{
            id:ttable
            width:200
            height:parent.height
            anchors{
                left:stable.right
                leftMargin: 10
            }
            delegate: TableItem{
                width:parent.width
                height:15
                header: ttable.model[index][0]
                value: ttable.model[index][1]
            }
        }
    }


}
