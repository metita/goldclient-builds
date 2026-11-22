# goldclient-builds

Instalador de **Counter-Strike 1.6 GoldClient 2.6.0 (beta)**, listo para jugar:

- instala CS 1.6 vanilla con la configuración por defecto,
- crea el acceso directo en el escritorio (`hl.exe -game cstrike -steam -noforcemparms -forceupdate -beta`),
- instala Visual C++ x86 solo si la PC no lo tiene.

Descarga: [CS16_GoldClient_Setup.exe](https://github.com/metita/goldclient-builds/releases/latest/download/CS16_GoldClient_Setup.exe)
(el enlace apunta siempre a la última release). Las versiones anteriores (`CS16_GoldClient.rar`, 2.5.7.0) quedan obsoletas.

## Reconstruir el instalador

Requisitos: Python 3, Inno Setup 6 (`%LOCALAPPDATA%\Programs\Inno Setup 6`) y el redistribuible VC++ x86 de Visual Studio Build Tools.

1. Copiar una instalación limpia de GoldClient a una carpeta aparte y actualizarla una vez con el actualizador del propio cliente:
   `hl.exe -game cstrike -steam -noforcemparms -forceupdate -beta` (no jugar en esa carpeta ni cambiar opciones).
   Si hay otro `hl.exe` abierto, el `hl.exe` viejo se queja de instancia única: cerrar el otro primero.
2. `python -I installer/build.py "<carpeta actualizada>" --out <salida>`

`build.py` copia el cliente, borra el estado de usuario (config, favoritos, resolución, avatar, caché, locales extra),
deja `config_default.cfg` como `config.cfg`, verifica que `bin\launcher.dll` sea la 2.6.x y que `hl.exe` no esté parcheado,
genera `setup.iss` desde `GoldClient.iss.tpl` y compila con ISCC.

Con `-forceupdate -beta` el cliente se mantiene en la última beta en cada arranque.
