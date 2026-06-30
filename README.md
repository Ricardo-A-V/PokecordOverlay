# Pokémon Discord Voice Overlay

Un overlay de escritorio ligero que muestra sprites de Pokémon reaccionando en tiempo real a las comunicaciones de voz en Discord. Diseñado para atravesar la barra de tareas de Windows y funcionar sin consumir recursos excesivos.

## ⚠️ REQUISITO CRÍTICO DE EJECUCIÓN

El archivo `PokemonOverlay.exe` **NO** puede ejecutarse de forma aislada. Para que el programa funcione, debe estar siempre en la misma carpeta que:

1. El archivo `config.json`
2. La carpeta `assets/` (que contiene los sprites)

Si sacas el `.exe` al escritorio y dejas las carpetas atrás, el programa colapsará inmediatamente. Crea un acceso directo del `.exe` si deseas lanzarlo desde otro lugar.

---

## ⚙️ Configuración Inicial

Para usar la aplicación, debes renombrar el archivo `config.example.json` a `config.json` y configurarlo con tus datos.

### 1. Obtener la URL de StreamKit (El puente de conexión)

Debido a las restricciones de privacidad de Discord, la aplicación extrae la información de voz mediante la herramienta oficial para streamers.

1. Abre tu navegador y ve a: [https://streamkit.discord.com/overlay](https://streamkit.discord.com/overlay)
2. Haz clic en **Install for OBS**.
3. En la parte superior, selecciona la pestaña **Voice Widget**.
4. En los menús desplegables de la izquierda, selecciona tu **Servidor** y el **Canal de voz** en el que sueles estar.
5. Copia la URL larguísima que aparece en el recuadro gris de la derecha.
6. Abre tu archivo `config.json` y pega esa URL dentro del bloque `"channels"`. Puedes guardar varias salas poniéndoles un nombre distintivo.

### 2. Asignar Pokémon a los Usuarios

El bloque `"users"` del `config.json` empareja la ID de Discord de un usuario con un sprite de Pokémon.

**Cómo obtener una ID de Discord:**

1. En Discord, ve a Ajustes de Usuario > Avanzado > Activa el **Modo Desarrollador**.
2. Haz clic derecho sobre el avatar de cualquier persona en un canal de voz o chat y selecciona **Copiar ID de usuario**.
3. Pega esa ID como clave en el `config.json`.

**Parámetros por usuario:**

- `"species"`: El nombre del Pokémon. Debe coincidir exactamente con el nombre de la carpeta dentro de `assets/sprites/` (ej. `"gengar"`).
- `"offset_y"`: Ajuste vertical en píxeles. Si el sprite queda muy alto, usa números negativos (ej. `-10`) para bajarlo; si queda hundido, usa números positivos.

_Nota: Si un usuario entra a la llamada y no está registrado en tu `config.json`, la aplicación renderizará automáticamente la especie definida en la variable `"default"` (por defecto, Ditto)._

---

## 🚀 Uso de la Aplicación

1. Haz doble clic en `PokemonOverlay.exe`. No aparecerá ninguna ventana principal, esto es normal.
2. Los Pokémon aparecerán instantáneamente en la parte inferior izquierda de tu pantalla principal cuando los usuarios entren al canal de voz configurado.
3. **Cambiar de Canal o Cerrar:** Busca el icono con forma de computadora en tu bandeja del sistema (esquina inferior derecha de Windows, junto al reloj).
   - **Clic Izquierdo:** Despliega un menú rápido para alternar entre las distintas salas de Discord que hayas guardado en tu `config.json`.
   - **Clic Derecho / Cerrar:** Termina el proceso de la aplicación limpiamente.
