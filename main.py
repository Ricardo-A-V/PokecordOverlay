import sys
import json
import os
from PyQt6.QtWidgets import (QApplication, QWidget, QHBoxLayout, QLabel, 
                             QSystemTrayIcon, QMenu, QStyle)
from PyQt6.QtGui import QPixmap, QAction, QCursor
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QPoint

from discord_ipc import DiscordWebScraper

class PokemonWidget(QWidget):
    def __init__(self, species, offset_y=0, parent=None):
        super().__init__(parent)
        self.setFixedSize(140, 250) 
        self.species = species
        self.is_speaking = False

        self.sprites_normal = []
        self.sprites_dark = []
        
        self.base_x = 6
        self.base_y = 122 - offset_y 

        self.load_sprites()

        self.sprite_label = QLabel(self)
        self.sprite_label.setFixedSize(128, 128)
        self.sprite_label.move(self.base_x, self.base_y) 

        if self.sprites_dark:
            self.sprite_label.setPixmap(self.sprites_dark[0])

        self.anim = QPropertyAnimation(self.sprite_label, b"pos")
        self.anim.setDuration(250) 
        self.anim.setStartValue(QPoint(self.base_x, self.base_y))
        self.anim.setKeyValueAt(0.1, QPoint(self.base_x, self.base_y - 20))
        self.anim.setEndValue(QPoint(self.base_x, self.base_y))

        self.frame_idx = 0
        self.timer_anim = QTimer(self)
        self.timer_anim.timeout.connect(self.update_frame)

        self.silence_timer = QTimer(self)
        self.silence_timer.setSingleShot(True)
        self.silence_timer.timeout.connect(self._apagar_animacion)

    def load_sprites(self):
        base_path = os.path.join("assets", "sprites", self.species)
        for i in range(4):
            path = os.path.join(base_path, f"idle_{i}.png")
            if os.path.exists(path):
                pix = QPixmap(path)
                scaled_pix = pix.scaled(
                    128, 128, 
                    Qt.AspectRatioMode.IgnoreAspectRatio, 
                    Qt.TransformationMode.FastTransformation
                )
                self.sprites_normal.append(scaled_pix)
                self.sprites_dark.append(self.darken_pixmap(scaled_pix))

    def darken_pixmap(self, pixmap):
        img = pixmap.toImage()
        for y in range(img.height()):
            for x in range(img.width()):
                color = img.pixelColor(x, y)
                if color.alpha() > 0: 
                    color.setRed(int(color.red() * 0.4))
                    color.setGreen(int(color.green() * 0.4))
                    color.setBlue(int(color.blue() * 0.4))
                    img.setPixelColor(x, y, color)
        return QPixmap.fromImage(img)

    def set_speaking(self, state):
        if state:
            self.silence_timer.stop()
            if not self.is_speaking:
                self.is_speaking = True
                self.anim.start()
                self.timer_anim.start(250)
        else:
            if self.is_speaking and not self.silence_timer.isActive():
                self.silence_timer.start(500)

    def _apagar_animacion(self):
        self.is_speaking = False
        self.timer_anim.stop()
        self.frame_idx = 0
        self.anim.stop()
        self.sprite_label.move(self.base_x, self.base_y)
        if self.sprites_dark:
            self.sprite_label.setPixmap(self.sprites_dark[0])

    def update_frame(self):
        if not self.sprites_normal: return
        self.frame_idx = (self.frame_idx + 1) % len(self.sprites_normal)
        self.sprite_label.setPixmap(self.sprites_normal[self.frame_idx])


class OverlayWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.WindowTransparentForInput |
            Qt.WindowType.Tool 
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(20, 0, 0, 0)
        self.layout.setSpacing(10) 
        self.layout.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)

        self.pokemon_widgets = {}
        self.load_config()

        # Configuración del System Tray
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        
        # Interceptar clics (izquierdo = canales, derecho = menú clásico de Windows)
        self.tray_icon.activated.connect(self.on_tray_activated)
        
        self.quit_action = QAction("Cerrar Overlay Pokémon", self)
        self.quit_action.triggered.connect(QApplication.instance().quit)
        
        self.tray_icon.show()

        # Iniciar motor web
        self.active_channel_key = self.config.get("active_channel_name", "")
        streamkit_url = self.config.get("channels", {}).get(self.active_channel_key, "")

        if streamkit_url:
            self.ipc = DiscordWebScraper(streamkit_url)
            self.ipc.speaking_signal.connect(self.handle_voice_event)
            self.ipc.presence_signal.connect(self.handle_presence_event)

    def load_config(self):
        with open("config.json", "r", encoding="utf-8") as f:
            self.config = json.load(f)

        for user_id, user_data in self.config["users"].items():
            species = user_data.get("species", self.config.get("default", "ditto"))
            offset_y = user_data.get("offset_y", 0)
            widget = PokemonWidget(species, offset_y)
            widget.hide() 
            self.pokemon_widgets[user_id] = widget
            self.layout.addWidget(widget)

    # ==========================================
    # GESTIÓN DE MENÚS Y CAMBIO DE CANAL
    # ==========================================
    def on_tray_activated(self, reason):
        # Trigger detecta el clic izquierdo principal
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show_channel_menu()

    def show_channel_menu(self):
        menu = QMenu()
        
        # Generar dinámicamente botones para cada canal en tu config.json
        for channel_name, url in self.config.get("channels", {}).items():
            action = QAction(channel_name, self)
            
            # Usar lambda para capturar las variables estáticas y enviarlas a la función
            action.triggered.connect(lambda checked, u=url, n=channel_name: self.switch_channel(n, u))
            
            # Marcar visualmente en qué canal estamos ahora mismo
            if channel_name == self.active_channel_key:
                action.setCheckable(True)
                action.setChecked(True)
                action.setEnabled(False) # No puedes cambiar al canal en el que ya estás
            
            menu.addAction(action)
        
        menu.addSeparator()
        menu.addAction(self.quit_action)
        
        # Desplegar el menú exactamente donde está el cursor del ratón
        menu.exec(QCursor.pos())

    def switch_channel(self, channel_name, url):
        self.active_channel_key = channel_name
        self.config["active_channel_name"] = channel_name
        
        # Sobrescribir config.json para guardar el estado
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
            
        # Ocultar todos los Pokémon actuales instantáneamente
        for widget in self.pokemon_widgets.values():
            widget.hide()
            widget.set_speaking(False)
            
        # Ordenar al navegador que cambie de sala
        self.ipc.change_url(url)

    # ==========================================
    # GESTIÓN DE VOZ Y PRESENCIA (DITTO DINÁMICO)
    # ==========================================
    def handle_voice_event(self, user_id, is_speaking):
        if user_id in self.pokemon_widgets:
            self.pokemon_widgets[user_id].set_speaking(is_speaking)

    def handle_presence_event(self, active_user_ids):
        # 1. Comprobar si hay IDs nuevas que no teníamos mapeadas
        for user_id in active_user_ids:
            if user_id not in self.pokemon_widgets:
                # CREACIÓN AL VUELO: Instanciamos el Pokémon por defecto y lo añadimos al Layout
                default_species = self.config.get("default", "ditto")
                print(f"[*] Usuario no configurado detectado. Generando: {default_species}")
                widget = PokemonWidget(default_species, 0)
                self.pokemon_widgets[user_id] = widget
                self.layout.addWidget(widget)

        # 2. Actualizar visualización de la sala
        for user_id, widget in self.pokemon_widgets.items():
            if user_id in active_user_ids:
                widget.show()
            else:
                widget.hide()
                widget.set_speaking(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    window = OverlayWindow()
    screen_geometry = app.primaryScreen().geometry()
    window.setGeometry(screen_geometry)
    
    window.show()
    sys.exit(app.exec())