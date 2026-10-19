; ============================================
; Installateur Inno Setup pour Relevé de Notes
; VERSION SANS LIEN WEB - Propre
; ============================================

#define MyAppName "Relevé de Notes"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Maryson SEGLA"
#define MyAppURL "https://github.com/seglamaryson/releve-de-notes"
#define MyAppExeName "ReleveDeNotes.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-1234-567890ABCDEF}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=LICENSE.txt
OutputDir=installer
OutputBaseFilename=ReleveDeNotes-Setup-v1.0.0
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
WizardSizePercent=120
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog
SetupIconFile=icone.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\ReleveDeNotes\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
