; Plantilla de GoldClient.iss: build.py reemplaza los @MARCADORES@ y compila.
; Sin #define a proposito: ISCC de 32 bits se queda sin memoria con este volumen.

[Setup]
AppId={{6B0D2F0A-5C1E-4C8E-9E3A-7D1A4F3B2C90}
AppName=Counter-Strike 1.6 GoldClient
AppVersion=@VERSION@ beta
AppVerName=Counter-Strike 1.6 GoldClient @BUILD@
AppPublisher=GoldClient
AppPublisherURL=https://descargarcs.com
DefaultDirName={autopf}\Counter-Strike 1.6 GoldClient
DefaultGroupName=Counter-Strike 1.6 GoldClient
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
DisableProgramGroupPage=yes
OutputDir=@OUT@
OutputBaseFilename=CS16_GoldClient_Setup
SetupIconFile=@SRC@\cstrike\cstrike.ico
UninstallDisplayIcon={app}\cstrike\cstrike.ico
UninstallDisplayName=Counter-Strike 1.6 GoldClient
WizardStyle=modern
Compression=lzma2/max
SolidCompression=yes
LZMAUseSeparateProcess=yes
LZMANumBlockThreads=1
DiskSpanning=no
ArchitecturesAllowed=x86compatible
VersionInfoVersion=@VERSION@.0
VersionInfoDescription=Counter-Strike 1.6 GoldClient
CloseApplications=no

[Languages]
Name: "es"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "en"; MessagesFile: "compiler:Default.isl"
Name: "pt"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[CustomMessages]
es.PlayNow=Jugar ahora
en.PlayNow=Play now
pt.PlayNow=Jogar agora
es.InstallingVC=Instalando Visual C++ 2015-2022 (x86)...
en.InstallingVC=Installing Visual C++ 2015-2022 (x86)...
pt.InstallingVC=Instalando Visual C++ 2015-2022 (x86)...

[Files]
Source: "@SRC@\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; platform\.appcache es una carpeta oculta con el estado del actualizador: sin ella no hay chequeo de updates.
Source: "@SRC@\platform\.appcache\*"; DestDir: "{app}\platform\.appcache"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "@EXTRA@\config.cfg"; DestDir: "{app}\cstrike"; Flags: onlyifdoesntexist uninsneveruninstall
Source: "@EXTRA@\serverbrowser_history.vdf"; DestDir: "{app}\platform\config"; Flags: onlyifdoesntexist uninsneveruninstall
Source: "@REDIST@"; DestDir: "{tmp}"; Flags: deleteafterinstall; Check: NeedsVCRedist

[Dirs]
Name: "{app}"; Permissions: users-modify

[Icons]
Name: "{autodesktop}\Counter-Strike 1.6 GoldClient"; Filename: "{app}\hl.exe"; Parameters: "@RUN@"; WorkingDir: "{app}"; IconFilename: "{app}\cstrike\cstrike.ico"
Name: "{group}\Counter-Strike 1.6 GoldClient"; Filename: "{app}\hl.exe"; Parameters: "@RUN@"; WorkingDir: "{app}"; IconFilename: "{app}\cstrike\cstrike.ico"
Name: "{group}\{cm:UninstallProgram,Counter-Strike 1.6 GoldClient}"; Filename: "{uninstallexe}"

[Run]
Filename: "{tmp}\vc_redist.x86.exe"; Parameters: "/install /quiet /norestart"; StatusMsg: "{cm:InstallingVC}"; Flags: waituntilterminated; Check: NeedsVCRedist
Filename: "{app}\hl.exe"; Parameters: "@RUN@"; WorkingDir: "{app}"; Description: "{cm:PlayNow}"; Flags: postinstall nowait skipifsilent

[UninstallDelete]
; Lo que el juego y el actualizador crean despues de instalar.
Type: filesandordirs; Name: "{app}\bin"
Type: filesandordirs; Name: "{app}\cstrike"
Type: filesandordirs; Name: "{app}\cstrike_addon"
Type: filesandordirs; Name: "{app}\cstrike_downloads"
Type: filesandordirs; Name: "{app}\cstrike_hd"
Type: filesandordirs; Name: "{app}\htmlcache"
Type: filesandordirs; Name: "{app}\localization"
Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\platform"
Type: filesandordirs; Name: "{app}\renderer_cache"
Type: filesandordirs; Name: "{app}\reshade-shaders"
Type: filesandordirs; Name: "{app}\server"
Type: filesandordirs; Name: "{app}\valve"
Type: files; Name: "{app}\steam_appid.txt"

[Code]
function NeedsVCRedist: Boolean;
var Installed: Cardinal;
begin
  Result := True;
  if RegQueryDWordValue(HKLM32, 'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x86', 'Installed', Installed) then
    Result := Installed <> 1;
  if Result and FileExists(ExpandConstant('{syswow64}\vcruntime140.dll')) and FileExists(ExpandConstant('{syswow64}\msvcp140.dll')) then
    Result := False;
end;
