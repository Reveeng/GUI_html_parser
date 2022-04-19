//Импортируются  объекты из стандартной библиотеки qt
import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Controls 2.12

//Это класс окна, создает нативное для платформы окно с кнопка закрыть и свернуть
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
//            По нажатию кнопки берет текст из textEdit и передает в класс parser url. И вызывает функцию parse
            if (textEdit.text.length != 0){
                if (parser.parse_html(textEdit.text)){
                    parser.get_tags_stats()
                    console.log("parsing poshel")
                }
            }
        }
    }
    Button{
        id:drawGraph
        anchors.verticalCenter: button.verticalCenter
        anchors.left:button.right
        anchors.leftMargin: 10
        width:150
        height:20
        text: "Показать граф"
        enabled: false
        onClicked: {
            parser.show_graph()
        }
    }
    Button{
        id:downlImgs
        anchors.verticalCenter: button.verticalCenter
        anchors.left:drawGraph.right
        anchors.leftMargin: 10
        width:150
        height:20
        text: "скачать изображения"
        enabled: false
        onClicked: {
            parser.download_images()
        }
    }

//    Соединям сигнал finished от парсера с функцией которая написана.
    Connections{
        target:parser
        function onFinished() {
//            Преобразуем JSObject полученный после вызова функцию get_stat в массив data, где один элемент это [tag, count]
            var data = Object.entries(parser.get_stat())
//            Задаем tableView модель data
            tableView.model = data
            drawGraph.enabled = true
            downlImgs.enabled = true
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
//    Отвечает за то, что таблица будет скроллится
    ScrollView{
        id:scView
        height:100
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
//        "таблица", чтобы в ней что-то начало отображаться нужно задать ей модель. Здесь расчитано на модель [tag, count]
        ListView{
            id:tableView
            height:parent.height
            orientation: ListView.Horizontal
            width:parent.width
            spacing: 0
            onModelChanged:{
//                Как только выставил модель, убираю с экрана надпись про то, что нет данных
                if (model.length != 0)
                    errText.visible = false
            }
//            На каждый элемент модели создается объект, который задан в delegate. У нас это две ячейки таблицы
//            Разметка ячеек в файле TableItem
            delegate: TableItem{
                height:scView.height
                header: tableView.model[index][0]
                value:tableView.model[index][1]
            }
        }
    }


}
