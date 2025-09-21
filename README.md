# Neoquest II Auto - A Neoquest II Autoplayer

## Disclaimer

This is an automated game player and very obviously not permitted by site rules. Use at your own risk, as I will not be held liable if you get iced! Use sensibly, and take breaks between usages.

By the way, it has its share of issues. 85% of the time, it works 100% of the time. Sometimes the Neopets site may hiccup and submit actions more than once, causing desync between the program and your game. Make sure the site is stable and try to play during off-peak hours with a **stable** internet connection for best results. If your connection drops, good luck finding your way back to the next starting point.

## What This Program Is

Neoquest II Auto is exactly what it sounds like: an autoplayer for the PHTML game Neoquest II on neopets.com. It is meant to help you grab all the game trophies and minimize the time you have to spend clicking away. What would normally take you weeks should now ideally take you hours with minimal user interaction.

## Features
- Beginning-to-end game completion methods sorted by act
- Automated skillpoint spending based on well-tested builds
  - Some manual supervision may be required
- Mouse-free map navigation - custom or predefined
- Fully automated in-game battle completion
  - Automatic potion usage based on efficiency

## Setup Instructions

First, clone the repo into a location of your choice:

```
git clone https://github.com/wngo1337/neoquestII-auto.git
```

Next, create a virtual environment, activate it, and install the requirements from requirements.txt:

```
python3 -m venv .venv
source .venv/bin/activate

# Use the line below if you are using Windows CMD, or the one below it if you are using Powershell
# .venv\Scripts\activate.bat
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

You also have to install the browser binary (Chromium) after you install Playwright:

```
playwright install
```

Now for the hardest part, you have to copy your Chromium browser's adblock extension into the RequiredData/AdblockDir folder in side this project. This allows the browser instance to run quicker by not loading ads. The assumption is that everyone is on Ublock Origin Lite, which has folder name ddkjiahejlhfcafbddmgiahcphecmpfh. You will copy the folder **inside** this folder that contains the actual extension info.

On Linux/Mac, the folder should be located at: ~/<YourUsername/.config/google-chrome/Default/Extensions/ddkjiahejlhfcafbddmgiahcphecmpfh

I'm not actually sure where this container folder is located on Windows. My guess is: C:\Users\<YourUsername>\AppData\Local\Google\Chrome\User Data\Default\Extensions\ddkjiahejlhfcafbddmgiahcphecmpfh

Inside this folder, you will find a folder with a name of something like 2025.911.1335_0. Copy this folder itself into neoquestII-auto/RequiredData/AdblockDir

Lastly, you will just need to enter in the correct login information in the user_info.txt file located in RequiredData/TextFiles.

For Neopass login, you will need to provide your Neopass email, Neopass password, and account username like this:

![NeopassLogin](ReadmeResources/neopass_login.png)

For traditional login, you just need to provide your account username and password like this:

![TraditionalLogin](ReadmeResources/traditional_login.png)

## Using the Program

At this point, the program should be ready to run. If you are using Neopass, there is an extra flag that you should provide like this:

```
python3 autoplayer_launcher.py --use-neopass
```

## Built With

- Python
- Playwright

