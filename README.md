# 🔎 jCOT 🔍
## ❓ FAQ
### What are COT data?
COT is the acronym of Commitments of Traders. COT data are published reports to help the public understand market dynamics of the main financial instruments. Learn more [here](https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm).

### What does jCOT allow you to do?
jCOT is a Python script that allows you to bulk download all of these data from 1986 to the present. It also allows you to update the current year's data by integrating them when new data are released. And finally it allows you to perform simple search queries to query these data to get their value for a specific instrument at a specific date.

### Why can it be useful?
To make quantitative analysis or to write trading algorithms having these data and easily interrogate them can be convenient. The strong point of jCOT is that it's possible to make searches invoking it through shell (CLI interface) and it is therefore callable and usable by any external software or language. It can be used for example to create an indicator on platforms like MetaTrader or cTrader.

### Where do the data come from and how are they stored?
Data are downloaded from the official website [here](https://www.cftc.gov/MarketReports/CommitmentsofTraders/HistoricalCompressed/index.htm). They are saved on the disk in a folder in the format of Excel (.xsl). This allows you to use them later even without an internet connection.

## ⬇ Installation
### Requirements
   * A PC with Windows (developed and tested on Windows 10) or Linux or MacOS.
   * Python 3 (developed and tested on 3.10 version).
   * Dependencies packages (read below to install them).
   * Internet connection to download/update data (optional for a search query).
   * Microsoft Excel to view (without doing search query with the script) or edit data directly (optional).
### Install Python 3
Download and install Python 3 from [here](https://www.python.org/downloads/).
Make sure to select 'Add Python to PATH' during installation on Windows.
If you use MacOS or Linux, Python 3 may already be preinstalled. In this case, check it, open a shell and type:
```bash
python --version 
```
then enter. If you have at least Python 3 go ahead. Otherwise try typing:
```bash
python3 --version
```
then enter. If it works proceed, otherwise install it. **From now I will write only python, otherwise it could become unnecessarily long writing python or python3, but if you noticed that you have to call the interpreter with python3, of course always do it in this way.** 
### Download jCOT
Click on the top-right green button 'Code' and then 'Download Zip'on this page.
### Extract jCOT
Use 7Zip or WinRAR or any other archive manager to extract the downloaded .zip file in a folder wherever you want.
### Install the dependecies
Open the extracted folder. Open a shell here (on Windows SHIFT + right click on a blank space and then 'Open PowerShell here' or 'Open Terminal here'. MacOS or Linux users should be experienced enough to do this 😂). Then type:
```bash
python -m pip install -r requirements.txt
```
and then press enter. If there are no errors, the installation is complete. 

## 💪 Usage
There are two ways to use jCOT. The first is to simply open the program (in the extracted folder locate jCOT.py), or invoke it by shell without passing any parameters to it, so you will use the command line GUI. The second way is to invoke it by passing arguments through the shell. The latter is especially useful if you plan to write programs that will interface with jCOT.
### Fist usage
If you are using jCOT for the first time, you will need to download the COT data. You can't research what you don't have 😂. Open the program and when asked to download the data answer with 'Y' and then enter. Otherwise, if you want to proceed via shell, open it in the extracted folder and then try:
```bash
python jCOT.py -u
```
note '-u' which means update (or get) the data. It's recommended (but not mandatory) to have a look also at the list of available symbols. To do that via CLI GUI reply 'Y' when will be asked. To do it in a nerd way, in the shell execute:
```bash
python jCOT.py -l
```
### Normal usage
During each execution (subsequent to the first one) of jCOT you can choose between:
 * View the symbols list.
 * Update the data.
 * Doing a search.
 
All these actions can be carried out through the CLI GUI, simply by opening the jCOT.py or via shell, passing these arguments:
 * -u: Get the COT Data or update it if already downloaded, in this last case, it's optional.
 * -l: Get the list of found symbols with the corrisponding code avaible for a query search.
 * -h: To see an help page similar to this one.
 * -s <symbolCODE>: The symbol code used for a query search. Required. To get this you can first call the program with -l.
 * -d <date>: The date used for a query search. Required. Format dd/mm/yyyy.
 
 Examples of usage with shell:
 * python COTData.py -u
 * python COTData.py -l
 * python COTData.py -u -s 099741 -d 03/04/2005
 * python COTData.py -s 099741 -d 05/06/2006
