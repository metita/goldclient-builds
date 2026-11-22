"""Arma el instalador de GoldClient (Counter-Strike 1.6) listo para jugar.

Uso:
    python -I installer/build.py "<cliente ya actualizado a la beta>" [--out <carpeta>] [--no-compile]

El cliente de entrada es una carpeta de GoldClient que ya corrio el actualizador
con `-forceupdate -beta` (su bin\\launcher.dll y platform\\.appcache lo delatan).
El script:
  1. copia el cliente a una carpeta de trabajo sin tocar el original,
  2. quita todo el estado de usuario (config, favoritos, resolucion, avatar,
     locales extra, cache) para dejar CS vanilla con valores por defecto;
     config.cfg y los favoritos de ZGaming van aparte (solo si no existen),
  3. genera setup.iss desde GoldClient.iss.tpl y lo compila con Inno Setup 6.

Salida: <out>\\CS16_GoldClient_Setup.exe
"""
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ISCC = os.path.expandvars(r'%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe')
REDIST = r'C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Redist\MSVC\v143\vc_redist.x86.exe'

# Parametros por defecto del acceso directo.
RUN_PARAMS = '-game cstrike -steam -noforcemparms -forceupdate -beta'

# Raiz del cliente que NO va en el instalador.
DROP_ROOT = ['!INSTALAR.bat', '!LEEME.txt', 'debug.log', 'discord-rpc.dll', 'steam_appid.txt']
DROP_ROOT_GLOB = re.compile(r'^(unins\d+\.(exe|dat)|.*\.apptmp|.*\.log|.*\.lnk|.*\.mdmp)$', re.I)
# Carpetas completas que se regeneran solas o son de usuario.
DROP_DIRS = ['htmlcache', 'logs', 'renderer_cache', 'cstrike_downloads',
             'localization/valve_spanish', 'localization/cstrike_spanish',
             'platform/shaders']
# Estado de usuario dentro del cliente.
DROP_FILES = [
    'cstrike/config.cfg', 'cstrike/userconfig.cfg', 'cstrike/custom.hpk', 'cstrike/voice_ban.dt',
    'platform/config/App.vdf', 'platform/config/GoldNetConfigData.vdf',
    'platform/config/InGameDialogConfig.vdf', 'platform/config/ServerBrowser.vdf',
    'platform/config/serverbrowser_history.vdf',
]


def fail(msg):
    print('ERROR:', msg)
    sys.exit(1)


def stage(src, dst):
    if os.path.exists(dst):
        shutil.rmtree(dst)
    print('copiando', src, '->', dst)
    r = subprocess.run(['robocopy', src, dst, '/E', '/NFL', '/NDL', '/NJH', '/NJS', '/NP'],
                       capture_output=True, text=True, errors='replace')
    if r.returncode >= 8:
        fail('robocopy fallo:\n' + r.stdout[-800:])
    for name in os.listdir(dst):
        p = os.path.join(dst, name)
        if os.path.isfile(p) and (name in DROP_ROOT or DROP_ROOT_GLOB.match(name)):
            os.remove(p)
    for d in DROP_DIRS:
        shutil.rmtree(os.path.join(dst, *d.split('/')), ignore_errors=True)
    for f in DROP_FILES:
        p = os.path.join(dst, *f.split('/'))
        if os.path.exists(p):
            os.remove(p)
    # Archivos de usuario: van aparte y el instalador solo los crea si no existen,
    # para que reinstalar no pise la config ni los favoritos de nadie.
    extra = os.path.join(os.path.dirname(dst), 'extra')
    shutil.rmtree(extra, ignore_errors=True)
    os.makedirs(extra)
    # config.cfg vanilla = el config_default.cfg que trae el propio juego.
    default = os.path.join(dst, 'cstrike', 'config_default.cfg')
    if not os.path.exists(default):
        fail('falta cstrike/config_default.cfg')
    shutil.copyfile(default, os.path.join(extra, 'config.cfg'))
    # Favoritos: los servidores de ZGaming.
    shutil.copyfile(os.path.join(HERE, 'serverbrowser_history.vdf'),
                    os.path.join(extra, 'serverbrowser_history.vdf'))


def check(dst):
    launcher = os.path.join(dst, 'bin', 'launcher.dll')
    if not os.path.exists(launcher):
        fail('no hay bin/launcher.dll: el cliente no esta actualizado a la 2.6.0')
    blob = open(launcher, 'rb').read()
    m = re.search(rb'2\.\d+\.\d+ \+\d+', blob)
    if not m:
        fail('no encuentro la version en launcher.dll')
    hl = open(os.path.join(dst, 'hl.exe'), 'rb').read()
    if b'ValveHalfLifeLauncherMutex' not in hl:
        fail('hl.exe esta parcheado: usa el original')
    if not os.path.isdir(os.path.join(dst, 'platform', '.appcache')):
        fail('falta platform/.appcache (estado del actualizador)')
    return m.group(0).decode()


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not args:
        fail(__doc__)
    src = os.path.abspath(args[0])
    out = os.path.join(HERE, 'out')
    if '--out' in sys.argv:
        out = os.path.abspath(sys.argv[sys.argv.index('--out') + 1])
    work = os.path.join(out, 'payload')
    os.makedirs(out, exist_ok=True)
    stage(src, work)
    version = check(work)
    print('version del cliente:', version)
    short = version.split(' ')[0]  # 2.6.0

    tpl = open(os.path.join(HERE, 'GoldClient.iss.tpl'), encoding='utf-8').read()
    iss = (tpl.replace('@SRC@', work)
              .replace('@OUT@', out)
              .replace('@EXTRA@', os.path.join(out, 'extra'))
              .replace('@VERSION@', short)
              .replace('@BUILD@', version)
              .replace('@RUN@', RUN_PARAMS)
              .replace('@REDIST@', REDIST))
    path = os.path.join(out, 'setup.iss')
    with open(path, 'w', encoding='utf-8-sig', newline='\r\n') as f:
        f.write(iss)
    print('iss listo:', path)
    if '--no-compile' in sys.argv:
        return
    r = subprocess.run([ISCC, '/Qp', path], capture_output=True, text=True, errors='replace')
    print(r.stdout[-1500:], r.stderr[-1500:])
    sys.exit(r.returncode)


if __name__ == '__main__':
    main()
