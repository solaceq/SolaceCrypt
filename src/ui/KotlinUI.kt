import javafx.application.Application
import javafx.scene.Scene
import javafx.scene.control.*
import javafx.scene.layout.VBox
import javafx.stage.Stage

class SolaceCryptUI : Application() {
    override fun start(stage: Stage) {
        val root = VBox(10.0)
        val scene = Scene(root, 800.0, 600.0)
        
        val menuBar = MenuBar().apply {
            menus.add(Menu("File").apply {
                items.add(MenuItem("Exit").apply {
                    setOnAction { stage.close() }
                })
            })
        }
        
        val fileChooser = Button("Select File").apply {
            setOnAction {
                // File selection logic
            }
        }
        
        root.children.addAll(menuBar, fileChooser)
        
        stage.apply {
            title = "SolaceCrypt"
            scene = scene
            show()
        }
    }
} 