#!/bin/bash

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

#python -m pip install -r requirements.txt

get_OS() {
  if [ -f /etc/debian_version ]; then
    # Older Debian/Ubuntu/etc.
    OS="debian"
    VER=$(cat /etc/debian_version)
    ID_LIKE="debian"
  elif [ -f /etc/os-release ]; then
    # freedesktop.org and systemd
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
    ID_LIKE=$ID_LIKE
  elif type lsb_release >/dev/null 2>&1; then
    # linuxbase.org
    OS=$(lsb_release -si)
    VER=$(lsb_release -sr)
    ID_LIKE=$OS
  elif [ -f /etc/lsb-release ]; then
    # For some versions of Debian/Ubuntu without lsb_release command
    . /etc/lsb-release
    OS=$DISTRIB_ID
    VER=$DISTRIB_RELEASE
    ID_LIKE=$OS
  else
    # Fall back to uname, e.g. "Linux <version>", also works for BSD, etc.
    OS=$(uname -s)
    VER=$(uname -r)
    ID_LIKE=$OS
  fi
echo "$ID_LIKE"
}

check_and_install()  {
  OS=$1
  PKG=$2

  a=""$(command -v $PKG)""
  if [ -z "$a" ]
    then
      if [ "$OS" = "arch" ]
        then
          if [ $EUID != 0 ]; then
            sudo pacman -S $PKG
          else
            pacman -S $PKG
          fi
      elif [ "$OS" = "debian" ]
        then
          if [ $EUID != 0 ]; then
            sudo apt install $PKG
          else
            apt install $PKG
          fi
      elif [ "$OS" = "fedora" ]
        then
        if [ $EUID != 0 ]; then
          sudo dnf install $PKG
        else
          dnf install $PKG
        fi
      else
        printf "${ORG}[!]${NC} - Couldn't detect package manager, please install $PKG manually before continuing.\n"
        echo
        while true
        do
          printf "${GRN}[+]${NC} - Have you installed $PKG ? [Y/n] "; read -r
          if [[ $REPLY =~ ^[Yy]$ ]]
            then break
          fi
        done
      fi
  else
    printf "${GRN}[-]${NC} - $PKG already installed.\n"
  fi

  #Manual install option in case of failure
  while true
  do
    a=""$(command -v $PKG)""
    if [ -z "$a" ]
      then
        printf "${ORG}[!]${NC} - Couldn't call $PKG is it installed? [Y/n] " ; read -r
        if [[ $REPLY =~ ^[Yy]$ ]]
          then
            #echo
            printf "${ORG}[!]${NC} - Forcing continue, you may experience issues when $PKG Is called by the application.\n"
            break
        else
          #echo
          printf "${GRN}[+]${NC} - Try installing $PKG again now.\n"
          printf "${GRN}[-]${NC} - Press any key to test again." ; read -r -n 1 -s
          echo
        fi
    else
      printf "${GRN}[+]${NC} - $PKG installation OK.\n"
      break
    fi
  done

}

download_python() {

  #Ask about auto install
  read -p "Would you like to automatically download Python3.8.2 installer for Wine? [Y/n] "  -r
  if [[ $REPLY =~ ^[Yy]$ ]]
    then
      #Auto download of python executable
      wget https://www.python.org/ftp/python/3.8.2/python-3.8.2-amd64.exe
      if [ "$(sha1sum ./python-3.8.2-amd64.exe | cut -d ' ' -f 1)" = "068bca4ae5678a9f8db721066ee029d4dd4bf3f4" ]
        then
          printf "${GRN}[+]${NC} - Python installer successfully downloaded.\n"
          return
        else
          printf "${ORG}[!]${NC} - Couldn't automatically download Python installer, reverting to manual installation.\n"
      fi
  fi

  #Manual installation
  echo
  echo "Please download a 'Windows executable installer' for Python 3"
  echo "Testing has been against 3.8.2, this would be a good choice of version."
  sleep 2
  echo "Opening browser."
  sleep 2
  echo "Place the exectuable file in this working directory once downloaded"
  sleep 4

  xdg-open https://www.python.org/downloads/ 2>/dev/null

  while true
  do
    read -p "Have you place the Python installer in the working directory? [Y/n] "  -r
    if [[ $REPLY =~ ^[Yy]$ ]]
      then break
    fi
  done
}


########### Install script starts here ###########

GRY='\033[0;36m'
GRN='\033[0;34m'
NC='\033[0m' # No Color
ORG='\033[0;31m'


OS=$(get_OS)
printf "${GRN}[-]${NC} - Base OS detected as : $OS\n"

#Install al OS based packages
InsPackages=("wine" "python3" "python3-pip")
for package in ${InsPackages[@]}; do
  check_and_install $OS $package
done

if [ "$OS" = "debian" ]
  then
    #Needs Wine fixes
    sudo dpkg --add-architecture i386
    sudo apt update
    sudo apt install wine32
fi

#Next, we'll call the pip requirements, because we may have needed python first
printf "${GRN}[-]${NC} - Installing Python dependencies\n"
printf "${GRY}$(python3 -m pip install --upgrade pip 2>&1)${NC}"
printf "${GRY}$(python3 -m pip install -r requirements.txt 2>&1)${NC}\n"
echo
printf "${GRN}[+]${NC} - Python dependencies installed\n"

#Now Wine and python configuration

#Check if wine can call python
if [[ "$(wine py -3 -V 2>/dev/null)" = *"not found"* ]] || [[ "$(wine py -3 -V 2>/dev/null)" = "" ]]
  then
    echo
    echo "Your Wine environment is missing Python 3."
    download_python
    if [ -f ./python-3.8.2-amd64.exe ]
      then
        echo "Found Python installer. Configuring."
        echo "Follow GUI promtps - next-next-finish."
        wine ./python-3.8.2-amd64.exe 2>/dev/null
    else
      echo "Cannot auto-detect Python Installer File, please manually rename to 'pyi.exe'"
      echo "You'll need to place the installer file in the script's working directory."
      read -p "Press any key to continue."  -r -n 1 -s
      echo
      while true
      do
        if [ ! -f ./pyi.exe ]
          then
          echo "pyi.exe still not found, please rename python installer to pyi.exe"
          read -p "Press any key when done."  -r -n 1 -s
          echo
        else
          echo "Found Python installer. Configuring."
          echo "Follow GUI prompts - next-next-finish."
          echo "BE sure to 'add python to PATH' on page 1!"
          wine pyi.exe 2>/dev/null
          break
        fi
      done
    fi
fi

echo
printf "${GRN}[+]${NC} - Configuring wine Python environment.\n"
echo
#Finally configure python on Wine


printf "${GRY} $(wine 2>&1 py -3 -m pip install --upgrade pip) ${NC}\n"
printf "${GRY} $(wine 2>&1  py -3 -m pip install -r requirements.txt) ${NC}\n"
echo
printf "${GRN}[+]${NC} - Adding ~/.local/bin to PATH.\n"
echo
#echo "export PATH=$PATH:$HOME/.local/bin" >> $HOME/.profile
PATH=$PATH:$HOME/.local/bin
printf "${GRN}[+]${NC} - Setup complete.\n"
echo
