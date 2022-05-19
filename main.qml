//Импортируются  объекты из стандартной библиотеки qt
import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.12

//Это класс окна, создает нативное для платформы окно с кнопка закрыть и свернуть
Window {
    width: 640
    height: 655
    minimumHeight: 655
    minimumWidth: 640
    maximumHeight: 655
    maximumWidth: 640
    visible: true
    color: "grey"
    title: qsTr("HTML parser")

    Connections{
        target:parser
        function onFinished() {
            resb.enabled = true
        }
    }

    TabBar {
        id: bar
        width: parent.width
        anchors.top:parent.top
        TabButton {
            text: qsTr("Результаты парсинга")
        }
        TabButton {
            id:resb
            text: qsTr("Ресурсы сайта")
            enabled: false
        }
    }

    StackLayout {
        width: parent.width
        anchors.top:bar.bottom
        anchors.bottom: footer.top
        currentIndex: bar.currentIndex
        TabResults{
            id:res
            Layout.fillHeight: true
            Layout.fillWidth: true
        }
        TabResource{
            id:reso
            Layout.fillHeight: true
            Layout.fillWidth: true
        }
    }

    Connections{
        target: parser
        function onStateChanged(strState){
            txtState.text = strState
        }
    }

    Rectangle{
        id:footer
        color: "white"
        height:15
        anchors{
            right:parent.right
            left: parent.left
            bottom: parent.bottom

        }
        Text{
            id:txtState
            font.pixelSize: 14
            text:"Нет выполняемых процессов"
            color: "black"
            anchors{
                right:parent.right
                rightMargin: 10
                verticalCenter: parent.verticalCenter
            }
        }
    }
}
