#####################################################################
#                                                                   #
#      Check and install dependencies for the Sblackfell Shell      #
#                                                                   #
#       Author : Blackfell                                          #
#      Twitter : @Blackf3ll                                         #
#        email : info@blackfell.net                                 #
#          Web : https://blackfell.net                              #
#         Repo : https://github.com/Blackfell/BlackfellShell        #
#                                                                   #
#####################################################################

Function Prnt-Success {
  Param ($text)
  Write-Host "[+] " -ForegroundColor Green -NoNewline
  Write-Host $text
}

Function Prnt-Fail {
  Param ($text)
  Write-Host "[!] " -ForegroundColor Red -NoNewline
  Write-Host $text
}

Function Prnt-Info {
  Param ($text)
  Write-Host "[-] " -ForegroundColor Cyan -NoNewline
  Write-Host $text
}

Function Prompt-Fancy {
  Param ($prompt)
  Write-Host "[-] " -ForegroundColor Cyan -NoNewLine
  Write-Host $prompt -NoNewLine
  $ans = Read-Host
  return $ans
}

Function Check-Installed {
  Param ($software)
  $installed = (Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* | Where { $_.DisplayName -Match $software })
  IF ($installed.count -gt 0){
    return $true
  }
  return $false
}

####################### Python 3 Install #########################

IF (Check-Installed "Python 3"){
  Prnt-Success "- Python3 installed OK."
}
ELSE {
  Prnt-Fail "- Python3 not installed."
  $confirmation = Prompt-Fancy "Would you like to automatically install Python3.8.2? [y/n]"
  IF ($confirmation -eq 'y') {
    Prnt-Info "Downloading Python Installer"
    Invoke-WebRequest https://www.python.org/ftp/python/3.8.2/python-3.8.2-amd64.exe -OutFile python-3.8.2-amd64.exe
    prnt-Info("Checking installer hash.")
    IF ( $(Get-Filehash -Path ./python-3.8.2-amd64.exe -Algorithm SHA1 | select -ExpandProperty hash) -eq "068bca4ae5678a9f8db721066ee029d4dd4bf3f4" ){
      Prnt-Success "- Python3.8.2 Downloaded. Follow GUI Installer."
      Prnt-Info "- Don't forget to tick 'Add to PATH' on page 1!"
      start-process ./python-3.8.2-amd64.exe
    }
    ELSE {
      Prnt-Fail "File didn't download correctly, try again, or download manually."
    }
  }
  ELSE {
    #Download prompts
    Prnt-Info "Please download a 'Windows executable installer' for Python 3"
    Prnt-Info "Testing has been against 3.8.2, this would be a good choice of version."
    Start-Sleep -s 2
    Prnt-info "Opening Browser"
    Start-Sleep -s 2
    Prnt-Info "Place the exectuable file in this working directory once downloaded"
    Start-Sleep -s 4
    Start-Process https://www.python.org/downloads/

    #Check if user has done the thing
    while($true){
      $confirmation = Prompt-Fancy "Have you placed the installer in the working directory? [y/n]"
      IF ($confirmation -eq 'y') {break}
    }
    #Now we have an installer on the machine, install python
    IF (Test-Path ./python-3.8.2-amd64.exe) {$installer="./python-3.8.2-amd64.exe"}
    ELSE {
      Prnt-Fail "Cannot auto-detect Python Installer File, please manually rename your installer to 'pyi.exe'"
      Prnt-Info "You'll need to place the installer file in the script's working directory."
      $confirm = Prompt-Fancy "Press Enter to continue."
      #Loop until file is There
      while ($true){
        IF (Test-Path ./pyi.exe) {
          Prnt-Success "Found Python installer. Configuring."
          $installer = './pyi.exe'
          break
        }
        ELSE {
          Prnt-Fail "pyi.exe still not found, please rename python installer to pyi.exe"
          Prompt-Fancy "Press Enter when done."
        }
      }
    }
    IF ( $(Get-Filehash -Path $installer -Algorithm SHA1 | select -ExpandProperty hash) -eq "068bca4ae5678a9f8db721066ee029d4dd4bf3f4" ){
      Prnt-Success "- Python3.8.2 Downloaded. Follow GUI Installer."
      Prnt-Info "- Don't forget to tick 'Add to PATH' on page 1!"
      start-process $installer
    }
  }
}

######################## WSL and Ubuntu #######################
$cmdName = "ubuntu"
IF (Get-Command $cmdName -errorAction SilentlyContinue) {
    Prnt-Success "$cmdName Already installed."
}
ELSE {
  Prnt-Info "Enabling Windows Subsystem for Linux"
  Start-Process Powershell -Verb RunAs -ArgumentList "Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux"
  Prnt-Info "Install the Ubuntu WSL environment. Opening Store."
  Start-Sleep -s 8
  Start-Process "https://www.microsoft.com/en-us/p/ubuntu/9nblggh4msv6?activetab=pivot:overviewtab"
  while($true){
    $confirmation = Prompt-Fancy "Have you installed the Ubuntu Environment? [y/n]"
    IF ($confirmation -eq 'y') {
      IF (Get-Command ubuntu -errorAction SilentlyContinue) {
          Prnt-Success "$cmdName installed and acessible."
          Prnt-Success "Launching Ubuntu, follow configuration and close."
          Start-Process ubuntu
          break
      }
      ELSE {
        Prompt-Fancy "Are you sure Ubuntu is installed? Can't access it through shell."
        break
      }
    }
  }
  #Now Ubuntu is installed, continue with python etc.
  while($true){
    $confirmation = Prompt-Fancy "Is your Ubuntu environment set up, complete with username and password? [y/n] "
    IF ($confirmation -eq 'y') {break}
  }
}

###################### Python Requirements #####################

Prnt-Info "Installing Windows Python dependencies"
py -3 -m pip install -r requirements.txt
#Install Python on Ubuntu
Prnt-Info "Installing python on Linux"
ubuntu -c 'if [ -z ""$(command -v python3)"" ]; then sudo apt update && sudo apt install python3 python3-pip; fi'
ubuntu -c 'if [ -z ""$(command -v python3-pip)"" ]; then sudo apt update && sudo apt install python3-pip; fi'
Prnt-Info "Installing Linux Python dependencies"
ubuntu -c 'python3 -m pip install -r requirements.txt'
#Linux path amendments to treat pip warning
ubuntu -c 'echo "export PATH=$PATH:$HOME/.local/bin" >> ~/.bash_profile'
