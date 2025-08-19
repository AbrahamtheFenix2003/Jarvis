# backend/scan_apps.py
# VERSIÓN MEJORADA: Detecta aplicaciones populares con mapeo inteligente de nombres

import os
import json
import re

def clean_name(filename):
    """Limpia el nombre de un archivo .exe para que sea más amigable."""
    name = filename.replace('.exe', '').replace('_', ' ').replace('-', ' ')
    # Intenta separar palabras en camelCase (ej. VisualStudio -> Visual Studio)
    name = re.sub(r'(?<!^)(?=[A-Z])', ' ', name)
    return name.lower().strip()

def get_friendly_name(filename, full_path):
    """Mapea nombres de archivos a nombres más amigables para aplicaciones populares."""
    filename_lower = filename.lower()
    path_lower = full_path.lower()
    
    # Mapeo de aplicaciones populares
    name_mappings = {
        'chrome.exe': 'google chrome',
        'msedge.exe': 'microsoft edge',
        'firefox.exe': 'firefox',
        'whatsapp.exe': 'whatsapp',
        'telegram.exe': 'telegram',
        'discord.exe': 'discord',
        'spotify.exe': 'spotify',
        'code.exe': 'visual studio code',
        'notepad++.exe': 'notepad++',
        'vlc.exe': 'vlc',
        'steam.exe': 'steam',
        'zoom.exe': 'zoom',
        'teams.exe': 'microsoft teams',
        'skype.exe': 'skype',
        'winrar.exe': 'winrar',
        'obs64.exe': 'obs studio',
        'photoshop.exe': 'adobe photoshop',
        'illustrator.exe': 'adobe illustrator',
        'acrobat.exe': 'adobe acrobat',
        'word.exe': 'microsoft word',
        'excel.exe': 'microsoft excel',
        'powerpoint.exe': 'microsoft powerpoint',
        'outlook.exe': 'microsoft outlook',
        'onenote.exe': 'microsoft onenote',
        'virtualbox.exe': 'virtualbox',
        'vmware.exe': 'vmware',
        'opera.exe': 'opera',
        'brave.exe': 'brave',
        'itunes.exe': 'itunes',
        'winamp.exe': 'winamp',
        'gimp.exe': 'gimp',
        'blender.exe': 'blender',
        'unity.exe': 'unity',
        'androidstudio.exe': 'android studio',
        'intellijidea.exe': 'intellij idea',
        'pycharm.exe': 'pycharm',
        'eclipse.exe': 'eclipse',
        'netbeans.exe': 'netbeans',
        'sublimetext.exe': 'sublime text',
        'atom.exe': 'atom',
        'brackets.exe': 'brackets',
        'nodejs.exe': 'node.js',
        'python.exe': 'python',
        'java.exe': 'java',
        'git.exe': 'git',
        'putty.exe': 'putty',
        'filezilla.exe': 'filezilla',
        'torrent.exe': 'bittorrent',
        'utorrent.exe': 'utorrent',
        'malwarebytes.exe': 'malwarebytes',
        'ccleaner.exe': 'ccleaner',
        'defraggler.exe': 'defraggler',
        'recuva.exe': 'recuva',
        'speccy.exe': 'speccy',
        'hwinfo.exe': 'hwinfo',
        'cpuz.exe': 'cpu-z',
        'gpuz.exe': 'gpu-z',
        'crystaldiskinfo.exe': 'crystaldiskinfo',
        'msiafterburner.exe': 'msi afterburner',
        'rivatuner.exe': 'rivatuner',
        'fraps.exe': 'fraps',
        'bandicam.exe': 'bandicam',
        'camtasia.exe': 'camtasia',
        'audacity.exe': 'audacity',
        'handbrake.exe': 'handbrake',
        'vlc.exe': 'vlc media player',
        'kmplayer.exe': 'kmplayer',
        'potplayer.exe': 'potplayer',
        'minecraft.exe': 'minecraft',
        'roblox.exe': 'roblox',
        'origin.exe': 'ea origin',
        'uplay.exe': 'ubisoft connect',
        'epicgameslauncher.exe': 'epic games launcher',
        'battle.net.exe': 'battle.net',
        'gog.exe': 'gog galaxy',
        'parsec.exe': 'parsec',
        'teamviewer.exe': 'teamviewer',
        'anydesk.exe': 'anydesk',
        'calculator.exe': 'calculadora',
        'notepad.exe': 'bloc de notas',
        'mspaint.exe': 'paint',
        'wordpad.exe': 'wordpad',
        'explorer.exe': 'explorador de archivos'
    }
    
    # Buscar mapeo directo
    if filename_lower in name_mappings:
        return name_mappings[filename_lower]
    
    # Buscar por patrones en el nombre del archivo
    for pattern, friendly_name in name_mappings.items():
        if pattern.replace('.exe', '') in filename_lower:
            return friendly_name
    
    # Buscar por patrones en la ruta
    if 'whatsapp' in path_lower:
        return 'whatsapp'
    elif 'telegram' in path_lower and 'telegram.exe' in filename_lower:
        return 'telegram'
    elif 'discord' in path_lower and 'discord.exe' in filename_lower:
        return 'discord'
    elif 'spotify' in path_lower and 'spotify.exe' in filename_lower:
        return 'spotify'
    elif 'chrome' in path_lower and 'chrome.exe' in filename_lower:
        return 'google chrome'
    elif 'edge' in path_lower and ('msedge.exe' in filename_lower or 'microsoftedge.exe' in filename_lower):
        return 'microsoft edge'
    elif 'firefox' in path_lower and 'firefox.exe' in filename_lower:
        return 'firefox'
    elif 'steam' in path_lower and ('steam.exe' in filename_lower or 'steamlauncher.exe' in filename_lower):
        return 'steam'
    elif 'zoom' in path_lower and 'zoom.exe' in filename_lower:
        return 'zoom'
    elif 'teams' in path_lower and ('teams.exe' in filename_lower or 'msteams.exe' in filename_lower):
        return 'microsoft teams'
    elif 'obs' in path_lower and ('obs.exe' in filename_lower or 'obs64.exe' in filename_lower):
        return 'obs studio'
    
    # Si no hay mapeo, usar el nombre limpio
    return clean_name(filename)

def is_valid_executable(filename, full_path):
    """Determina si un ejecutable es válido (no es un instalador, desinstalador, etc.)"""
    filename_lower = filename.lower()
    path_lower = full_path.lower()
    
    # Archivos que queremos evitar
    invalid_patterns = [
        'unins', 'uninstall', 'setup', 'installer', 'updater', 'update',
        'crashhandler', 'crash', 'maintenancetool', 'helper', 'service',
        'daemon', 'background', 'vc_redist', 'redist', 'browser_broker',
        'elevation_service', 'notification_helper', 'chrmstp'
    ]
    
    # Carpetas que contienen archivos no deseados
    invalid_folders = [
        'update', 'temp', 'cache', 'backup', 'installer', 'redist',
        'crash', 'debug', 'tools\\', 'bin\\cef', 'bin\\debug'
    ]
    
    # Verificar patrones inválidos en el nombre del archivo
    for pattern in invalid_patterns:
        if pattern in filename_lower:
            return False
    
    # Verificar carpetas inválidas en la ruta
    for folder in invalid_folders:
        if folder in path_lower:
            return False
    
    return True

def find_apps():
    """Busca aplicaciones en carpetas comunes y las guarda en commands.json."""
    print("🔍 Iniciando escaneo inteligente de aplicaciones...")
    
    commands = {}
    
    # --- RUTAS DE BÚSQUEDA AMPLIADAS ---
    appdata = os.environ.get('APPDATA')
    local_appdata = os.environ.get('LOCALAPPDATA')
    program_files = os.environ.get('ProgramFiles')
    program_files_x86 = os.environ.get('ProgramFiles(x86)')
    
    # Rutas específicas donde se instalan aplicaciones populares
    search_paths = [
        program_files,
        program_files_x86,
        local_appdata,
        appdata,
        os.path.join(local_appdata, 'Programs'),
        os.path.join(local_appdata, 'Microsoft', 'WindowsApps'),
        os.path.join(appdata, 'Microsoft', 'Windows', 'Start Menu', 'Programs'),
        # Rutas específicas para apps populares
        os.path.join(local_appdata, 'WhatsApp'),
        os.path.join(local_appdata, 'Discord'),
        os.path.join(local_appdata, 'Spotify'),
        os.path.join(program_files, 'Google', 'Chrome', 'Application'),
        os.path.join(program_files_x86, 'Google', 'Chrome', 'Application'),
        os.path.join(program_files, 'Microsoft', 'Edge', 'Application'),
        os.path.join(program_files_x86, 'Microsoft', 'Edge', 'Application'),
    ]
    
    # Filtra las rutas que existan
    search_paths = [path for path in search_paths if path and os.path.exists(path)]
    
    # Lista de ejecutables que queremos ignorar
    ignore_list = [
        'unins000.exe', 'uninstall.exe', 'setup.exe', 'updater.exe', 
        'crashhandler.exe', 'maintenancetool.exe', 'vc_redist.x64.exe',
        'helper.exe', 'installer.exe', 'update.exe', 'crash.exe',
        'service.exe', 'daemon.exe', 'background.exe'
    ]
    
    # Contadores para estadísticas
    found_count = 0
    popular_apps_found = []
    
    for path in search_paths:
        print(f"📂 Escaneando: {path}")
        try:
            # Limitar profundidad para evitar escanear demasiadas subcarpetas
            for root, dirs, files in os.walk(path):
                # Limitar profundidad (máximo 3 niveles)
                level = root[len(path):].count(os.sep)
                if level >= 3:
                    dirs[:] = []  # No ir más profundo
                    continue
                
                for file in files:
                    if file.lower().endswith('.exe') and is_valid_executable(file, root):
                        full_path = os.path.join(root, file)
                        friendly_name = get_friendly_name(file, full_path)
                        
                        # Dar prioridad a aplicaciones principales vs herramientas de sistema
                        is_main_app = not any(folder in full_path.lower() for folder in [
                            'update', 'temp', 'cache', 'backup', 'tools', 'helper', 
                            'service', 'redist', 'common files'
                        ])
                        
                        if friendly_name not in commands or is_main_app:
                            commands[friendly_name] = full_path
                            found_count += 1
                            
                            # Detectar aplicaciones populares
                            popular_keywords = ['chrome', 'edge', 'whatsapp', 'telegram', 'discord', 
                                              'spotify', 'steam', 'zoom', 'teams', 'firefox']
                            if any(keyword in friendly_name.lower() for keyword in popular_keywords):
                                popular_apps_found.append(friendly_name)
                                print(f"  ⭐ {friendly_name}")
                            else:
                                print(f"  📱 {friendly_name}")
        except Exception as e:
            print(f"  ❌ Error escaneando {path}: {e}")
    
    # Agregar comandos del sistema
    print("\n🔧 Agregando comandos del sistema...")
    system_commands = {
        'calculadora': 'calc.exe',
        'bloc de notas': 'notepad.exe',
        'explorador de archivos': 'explorer.exe',
        'paint': 'mspaint.exe',
        'cmd': 'cmd.exe',
        'powershell': 'powershell.exe',
        'configuración': 'ms-settings:',
        'panel de control': 'control.exe',
        'administrador de tareas': 'taskmgr.exe',
        'editor de registro': 'regedit.exe',
        'servicios': 'services.msc',
        'información del sistema': 'msinfo32.exe'
    }
    
    commands.update(system_commands)
    
    # Verificar aplicaciones específicas y agregar si no están
    specific_apps = {
        'google chrome': [
            'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
            'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe'
        ],
        'microsoft edge': [
            'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
            'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe'
        ],
        'whatsapp': [
            f'{local_appdata}\\WhatsApp\\WhatsApp.exe',
            f'{local_appdata}\\Programs\\WhatsApp\\WhatsApp.exe'
        ],
        'steam': [
            'C:\\Program Files (x86)\\Steam\\steam.exe',
            'C:\\Program Files\\Steam\\steam.exe'
        ],
        'discord': [
            f'{local_appdata}\\Discord\\Update.exe --processStart Discord.exe',
            f'{local_appdata}\\Discord\\app-*\\Discord.exe'
        ],
        'spotify': [
            f'{appdata}\\Spotify\\Spotify.exe',
            f'{local_appdata}\\Microsoft\\WindowsApps\\Spotify.exe'
        ],
        'telegram': [
            f'{appdata}\\Telegram Desktop\\Telegram.exe'
        ],
        'zoom': [
            f'{appdata}\\Zoom\\bin\\Zoom.exe',
            'C:\\Program Files\\Zoom\\bin\\Zoom.exe',
            'C:\\Program Files (x86)\\Zoom\\bin\\Zoom.exe'
        ],
        'firefox': [
            'C:\\Program Files\\Mozilla Firefox\\firefox.exe',
            'C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe'
        ]
    }
    
    print("\n🔎 Verificando aplicaciones específicas...")
    for app_name, possible_paths in specific_apps.items():
        if app_name not in commands:
            for path in possible_paths:
                if os.path.exists(path):
                    commands[app_name] = path
                    print(f"  ✅ Encontrado: {app_name}")
                    break
            else:
                print(f"  ❌ No encontrado: {app_name}")
    
    # Guardar resultado
    output_path = os.path.join(os.path.dirname(__file__), 'commands.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(commands, f, indent=4, ensure_ascii=False)
    
    # Mostrar estadísticas
    print(f"\n🎉 ¡Escaneo completado!")
    print(f"📊 Total de aplicaciones encontradas: {len(commands)}")
    print(f"⭐ Aplicaciones populares detectadas: {len(popular_apps_found)}")
    if popular_apps_found:
        print("   " + ", ".join(popular_apps_found))
    print(f"💾 Guardado en: {output_path}")
    print("\n🚀 Ahora puedes ejecutar 'python server.py' para iniciar Jarvis.")

if __name__ == '__main__':
    find_apps()
