import os
import sys
import shutil
import subprocess

# Inyección de contexto absoluto para evitar errores de ruta en terminal
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

def build_app():
    app_name = "PokecordOverlay"
    icon_file = "chatot.ico"
    main_script = "main.py"
    exe_name = f"{app_name}.exe"

    print(f"[*] Iniciando compilación de {app_name} en modo ONEFILE...")

    # Validación estricta
    if not os.path.exists(icon_file):
        print(f"[-] ERROR FATAL: No se encontró '{icon_file}'.")
        sys.exit(1)

    # Limpiar ejecutable anterior si existe en la raíz
    if os.path.exists(exe_name):
        try:
            os.remove(exe_name)
        except PermissionError:
            print(f"[-] CRÍTICO: No se puede borrar '{exe_name}'. ¿Está el programa abierto?")
            sys.exit(1)

    # Instrucciones para PyInstaller (Añadido --onefile)
    pyinstaller_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",
        "--onefile",
        f"--name={app_name}",
        f"--icon={icon_file}",
        main_script
    ]

    # Proceso de empaquetado
    print("[*] Compilando binarios en un único archivo (esto tardará bastante)...")
    try:
        subprocess.run(pyinstaller_cmd, check=True)
    except subprocess.CalledProcessError:
        print("[-] CRÍTICO: Falló el motor de PyInstaller.")
        sys.exit(1)

    print("[*] Moviendo el ejecutable a la raíz...")
    
    # Extraer el .exe de 'dist' y ponerlo en la raíz
    dist_exe_path = os.path.join("dist", exe_name)
    if os.path.exists(dist_exe_path):
        shutil.move(dist_exe_path, exe_name)

    # Aniquilación de carpetas temporales
    print("[*] Ejecutando limpieza profunda (borrando dist, build y specs)...")
    shutil.rmtree("dist", ignore_errors=True)
    shutil.rmtree("build", ignore_errors=True)
    
    spec_file = f"{app_name}.spec"
    if os.path.exists(spec_file):
        os.remove(spec_file)

    print("-" * 60)
    print(f"[+] COMPILACIÓN ONEFILE COMPLETADA.")
    print(f"[+] Tienes el archivo '{exe_name}' suelto en tu raíz.")
    print(f"[!] RECUERDA: Este .exe necesita que 'config.json' y 'assets' estén a su lado para funcionar.")
    print("-" * 60)

if __name__ == "__main__":
    build_app()