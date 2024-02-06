# CodyFight-Bot
Client and Bot for the videogame Codyfight, improvements to make the code more readable, maintainable, etc, are welcome

# Setting up Python on Windows and Mac
The code is in Python so first we need to install it

Windows

1. Download Python
  - Visit the oficial Python website: python.org
  - Go to the "Downloads" section and choose the latest version for Windows
2. Run the installer
  - Open the downloaded file
  - **Check the box that says "Add Python x.x to PATH" during installation**  __IMPORTANT__
3. Verify the installation
  - Open the Command Prompt or PowerShell
  - Type 'python --version' to verify Python is installed

Mac

1. Check Python Version
  - Mac usually comes with Python pre-installed
  - Open the terminal
  - Type 'python3 --version' to check the version
2. Install Homebrew (if needed):
  - If Python isn't installed or you want to manage versions, install Homebrew: brew.sh
  - Install Python using Homebrew: 'brew install python'
3. Verify Installation
  - Type 'python3 --version' again to confirm Python is installed

# Stay up to date

BugsAndFixes files has info about bugs found that are not solved yet and temporal changes if something doesn't work as expected check this file, in case there is no info about your problem submit a Issue or report it in the Codyfight discord

# Coping the repository
You can copy all the repository manually if you want but its better if you use Git Bash to do it as it is easier to keep it up to date

# How to install Git Bash (Windows)

Windows

1. Download Git 
  - Open your web browser and navigate to the official Git website: https://git-scm.com/ and download
2. Run the installer
  - Follow the on-screen instructions in the installer, you can leave the default settings 

# How to install Git Bash (Unix Systems)
We can install Git Bash with the command line typing the following commands

-This command updates the package lists, accept if it asks for confirmation to download
```
sudo apt-get update
```
-Installing git
```
sudo apt-get install git
```
-Verify installation and version installed
```
git --version
```

# Nevigating with the command line/cmd
Before cloning the repository you must navigate to the directory where you want to clone it
- On Windows use the 'dir' command to list/view the names of the files in the directory where you are located and 'cd' command to move to the directory where you want to store the cloned repository. For example:

List/view the files of the directory
```
dir
```

Move to another directory
```
cd YourFolder
```

- In Unix Systems use the 'ls' command to view the files of a directory, is similar to the 'dir' command in windows and same as in windows we use 'cd' to move to another directory

List/view the files of the directory
```
ls
```

Move to another directory
```
cd YourFolder
```

Creating a folder
```
mkdir FolderName
```

# How to copy/clone and update the repository
-You can clone the repository in your device with Git Bash by typing:
```
git clone <repository_url>
```
Replace the <repository_url> with the url, in this case https://github.com/SleatherT/CodyFight-Bot

```
git clone https://github.com/SleatherT/CodyFight-Bot
```

Once the cloning process is complete, you should see a new directory in your chosen location with the contents of the cloned repository

-To check if your copy is up to date you can use 
```
git status
```
This command it also show us the name of the branch we are on, keep in mind this name since it will be used to update the cloned repository

-If it tells us that we are behind we can update it by typing:
```
git pull origin <branch_name>
```
Replace the <branch_name> by the name that the previous command showed you. If you cloned this repository it should be 'main', so it would end up lokking like this

```
git pull origin main
```

# Deploy bot, Change the game mode and other configuration options

The easy way to deploy the bot is just editing the config.py file with your ckey and execute the bot file (e.g. hunterbot.py)

That works if the repository it would never be updated but since its not the case, you should use the ckey.py.template file to create a ckey.py file, so when pulling/updating the repository you dont need to edit again the config file with your ckey

To change the game mode, edit the config.py file

At the time of writing there are configuration options to make the hunterbot go only to exits and an option to not create/save a history.txt file, usefull when deploying the bot in the cloud

# Files and Classes

The **core** folder as his name implies, has the framework to make possible code bots. His files are:
  - client.py contains the Client class use this to make requests to the api, each request sent responds with info that we can use, like the status of the game or if its our turn, the functions of the Client class are get_status(), create_room(), cast_skill(), move_player() and surrender(), names are self-explanatory 
  - nodemap.py has the Graph, Node, Connection classes and the dijkstra, getMap functions, you can see his properties and get an idea of what information they hold

The **strategies** folder has some strategies i have build to some codyfigthers:
  - baseStrategy.py as his name says is a example of a basic strategy using the classes and data obtained from the Graph, you can use it as a point of start for your own strategy
  - swapStrategy.py this is a more complex strategy for the Trickster codyfigther with swap
  - hunterStrategy. build for Hunter codyfigther, in comparison to the swapStrategy the strategyAttack function is more developed here

The **tests** folder has files to test the code:
  - testmap.txt and tests.py, names self-explanatory

Outside we have the bots:
  - swapbot.py is the implementation of all the files mentioned to create a bot to deploy using swapStrategy
  - hunterbot.py same as exitbot using hunterStrategy
  - history.txt everytime we make a request to the api this file is written with the info recieved, if we found a map that cause errors or we want to test something we can copy one of the responses in the testmap.py

# How to create your own bots / Contribute to the repository
You can start by reading the core files, and after the strategy files, almost all the functions are commented or have type hints

# Skill/Attacks not supported right now
This change constantly so i am going to forget to update this probably, you can always ask me in the codyfight discord if you want to make sure the skill is still not supported
- Skills that can be casted on traps
- Skills that can create traps
- Almost all the movement skills, like double time
- Skills that can create structures like walls
