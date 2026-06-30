from PyQt6.QtCore import pyqtSignal, QObject, QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage

class ConsoleScraperPage(QWebEnginePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_obj = parent

    def javaScriptConsoleMessage(self, level, message, line, source):
        if message.startswith("STATUS:"):
            try:
                _, user_id, state = message.split(":")
                is_speaking = (state == "1")
                self.parent_obj.speaking_signal.emit(user_id, is_speaking)
            except ValueError:
                pass
        elif message.startswith("PRESENT:"):
            # Extrae la lista de IDs de los usuarios que están actualmente en la llamada
            users_str = message.replace("PRESENT:", "")
            user_list = users_str.split(",") if users_str else []
            self.parent_obj.presence_signal.emit(user_list)
        elif message == "INYECCION_OK":
            print("[+] Enlace con StreamKit establecido. Analizando usuarios...")

class DiscordWebScraper(QObject):
    speaking_signal = pyqtSignal(str, bool)
    presence_signal = pyqtSignal(list)

    def __init__(self, streamkit_url):
        super().__init__()
        
        self.browser = QWebEngineView()
        self.page = ConsoleScraperPage(self)
        self.browser.setPage(self.page)
        self.browser.loadFinished.connect(self.inject_js)
        
        print(f"[*] Cargando URL de StreamKit en segundo plano...")
        self.browser.load(QUrl(streamkit_url))

    def inject_js(self, ok):
        if not ok:
            print("[-] CRÍTICO: Error al cargar la página.")
            return
            
        js_code = """
        window.lastState = {};
        window.lastUsersStr = "";

        function analizarEstado() {
            let currentUsers = [];
            document.querySelectorAll('img[class*="Voice_avatar"]').forEach(img => {
                const src = img.getAttribute('src');
                if (!src) return;
                
                const match = src.match(/avatars\\/(\\d+)\\//);
                if (!match) return;
                
                const userId = match[1];
                currentUsers.push(userId);
                
                const isSpeaking = img.className.includes('Speaking');
                if (window.lastState[userId] !== isSpeaking) {
                    window.lastState[userId] = isSpeaking;
                    console.log("STATUS:" + userId + ":" + (isSpeaking ? "1" : "0"));
                }
            });

            // Si hay un cambio en quién está en la sala, notifica a Python
            const currentUsersStr = currentUsers.sort().join(',');
            if (window.lastUsersStr !== currentUsersStr) {
                window.lastUsersStr = currentUsersStr;
                console.log("PRESENT:" + currentUsersStr);
            }
        }

        const observer = new MutationObserver(analizarEstado);
        observer.observe(document.body, { 
            attributes: true, 
            childList: true, 
            subtree: true, 
            attributeFilter: ['class'] 
        });
        
        analizarEstado(); // Ejecución inicial por si ya hay gente dentro
        console.log("INYECCION_OK");
        """
        self.browser.page().runJavaScript(js_code)

    def change_url(self, new_url):
        """Ordena al navegador invisible que cargue un nuevo canal de StreamKit."""
        print(f"[*] Cambiando de canal de voz...")
        self.browser.load(QUrl(new_url))