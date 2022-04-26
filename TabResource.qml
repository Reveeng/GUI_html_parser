import QtQuick 2.0
import QtQuick.Controls 2.12


Item {

    Text{
        id:txt
        text:"Полученные ресурсы сайта"
        font.pixelSize: 18
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top:parent.top
        anchors.topMargin: 10
    }

    Connections{
        target: parser
        function onGetAllImagesUrl(names){
            var data = Object.entries(names)
//            console.log(data)
            if (data.length === 0){
                noData.visible = true
            }else{
                gv.model = data
                console.log("site is ",gv.model[0][1])
            }
            pw.visible = false
        }
        function onDownloadProgressChanged(progress){
            pw.value = progress
            pw.visible = true
        }

    }
    Text{
        id:noData
        z:2
        text:"Визуальные ресурсы на сайте не найдены"
        font.pixelSize: 18
        anchors.centerIn: parent
        visible: false
    }
    ProgressWindow{
        id:pw
        text:"Идет загрузка изображений. Подождите..."
        visible:false
    }

    ScrollView{
        id:sc
        clip:false
        ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
        ScrollBar.vertical.policy: ScrollBar.AlwaysOff
        anchors{
            right:parent.right
            left:parent.left
            top:txt.bottom
            margins: 5
        }

        GridView{
            id:gv
            width:parent.width
//            height:parent.height
            flow: GridView.FlowLeftToRight
            cellHeight: 210
            cellWidth: 210
            onModelChanged:{
                if (model.length == 0 )
                    noData.visible = true
            }
            delegate: Item{
                width:210
                height:210
                Rectangle{
                    width:200
                    height:200
                    border.color:"black"
                    border.width: 1
//                    color:"transparent"
                    Image{
                        id:img
                        anchors.fill:parent
                        sourceSize.height: height
                        sourceSize.width: width
                        source: gv.model[index][1]
                    }
                }
            }
        }
    }

}
