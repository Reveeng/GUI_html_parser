//Импортируются  объекты из стандартной библиотеки qt
import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.12

//Это класс окна, создает нативное для платформы окно с кнопка закрыть и свернуть
Window {
    width: 640
    height: 640
    minimumHeight: 640
    minimumWidth: 640
    maximumHeight: 640
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
        anchors.bottom: parent.bottom
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
}
