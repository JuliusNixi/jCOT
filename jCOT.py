import pandas as pd
import zipfile
import datetime
import xlrd
from numpy import datetime64, timedelta64
from bs4 import BeautifulSoup
from requests import get
from os.path import isdir, isfile, join
from os import mkdir, listdir, read, rename, remove, devnull
from os.path import basename
from sys import exit, argv
from datetime import date, datetime, timedelta

def Exit():
    input()
    exit()

def CreateDataDirectory():
    try:
        mkdir(foldername)
    except Exception as e:
        print("Error during the creation of COTData folder. Press enter to exit...")
        Exit()
    print("Directory COTData created succesfully!")

def GetLinks(year = None):
    try:
        req = get("https://www.cftc.gov/MarketReports/CommitmentsofTraders/HistoricalCompressed/index.htm")
        if int(req.status_code) != 200:
            raise Exception("")
        pagcont = req.content
        soup = BeautifulSoup(pagcont, "html.parser")
        atags = soup.find('table', style="width: 501px;").findAll("a")
        linksexcel = []
        for atag in atags:
            if str(atag.text) == "Excel":
                linksexcel.append(str(atag["href"]))
        linkyear = ""
        if year != None:
            for i in range(len(linksexcel)):
                if str(year) in linksexcel[i]:
                    linkyear = linksexcel[i]
                    break
        if year != None and linkyear == "":
            #New Year bug fix.
            return GetLinks(int(AddYears(date.today(), -1).year))
        print("Links/Link of files/file successfully obtained!")
        if linkyear != "":
            return [linkyear]
        return linksexcel
    except Exception as e:
        print("Error while getting links. Press enter to exit...")
        Exit()

def DownloadData(linksexcel):
    try:
        baselink = "https://www.cftc.gov/sites/default/files"
        for link in linksexcel:
            url = baselink + link
            fname = link.split("/")[4]
            req = get(url, allow_redirects=True)
            with open(foldername + fname, 'wb') as file:
                file.write(req.content)
                file.close()
            if (len(linksexcel) == 1):
                try:
                    remove(foldername + fname.replace(".zip", ".xls"))
                except Exception as e:
                    pass
        try:
            filetodelete = "deafut_xls_1986_2016.zip"
            remove(foldername + filetodelete)
        except Exception as e:
            pass
        print("New files/Updated file dowloaded succesfully!")
    except Exception as e:
        print("Error while downloading/saving the COT data. Press enter to exit...")
        Exit()

def UnzipData():
    try:
        files = [file for file in listdir(foldername) if isfile(join(foldername, file))]
        for file in files:
            if not ".zip" in file:
                continue
            inzipfilename = ""
            with zipfile.ZipFile(foldername + file, 'r') as zip:
                inzipfilename = zip.namelist()[0]
                zip.extractall(foldername)
            rename(foldername + inzipfilename, foldername + file.replace(".zip", ".xls"))
            remove(foldername + file)
        print("New files/Updated file extracted succesfully!")
    except Exception as e:
        print("Error while unzipping the COT data. Press enter to exit...")
        Exit()

def CheckData():
    if not isdir(foldername):
        print("COTData folder not found. I start downloading and processing the COT data.")
        CreateDataDirectory()
        DownloadData(GetLinks())
    else:
        print("COTData folder found. I update the current year COT file.")
        DownloadData(GetLinks(int(date.today().year)))
    UnzipData()
    print("DONE!")

def AddYears(d, years):
    try:
        return d.replace(year = d.year + years)
    except ValueError:
        return d + (date(d.year + years, 1, 1) - date(d.year, 1, 1))

def NoneRow(row):
    if "NoneType" in str(type(row)):
        return True
    return False

def Search(indate, symbol, getlast = False, range = False):
    if not isdir(foldername):
        print("Error COTData folder not found. First get the COT data and then retry. Press enter to exit...")
        Exit()
    filename = "dea_fut_xls_YEAR.xls".replace("YEAR", str(indate.year))
    try:
        wb = xlrd.open_workbook(foldername + filename, logfile=open(devnull, 'w'))
        df = pd.read_excel(wb, dtype = {'CFTC_Contract_Market_Code': 'str'})
    except Exception as e:
        print(f"Error filename {filename} not found in the COTData folder. Try to get/update the COT Data. Press enter to exit...")
        Exit()
    try:
        df = df.loc[df['CFTC_Contract_Market_Code'] == symbol]
        df = df.iloc[::-1]
        lastrow = df.tail(1)
        if getlast:
            return lastrow
        lrows = len(df.index)
        resultrow = None
        cotdate = ""
        if lrows == 0:
            print("Error the excel file is empty or data not found for the given instrument at the given date. Check the instruments list with -l or try a recent date in the same year. Press enter to exit...")
            Exit()
        elif lrows == 1:
            r = df.head(1)['Report_Date_as_MM_DD_YYYY'].values[0]
            ts = (r - datetime64('1970-01-01')) / timedelta64(1, 's')
            td = datetime.utcfromtimestamp(ts)
            cotdate = td
            if indate >= td:
                resultrow = df.head(1)
            else:
                resultrow = Search(AddYears(indate, -1), symbol, True)
                r = resultrow.head(1)['Report_Date_as_MM_DD_YYYY'].values[0]
                ts = (r - datetime64('1970-01-01')) / timedelta64(1, 's')
                td = datetime.utcfromtimestamp(ts)
                cotdate = td
                if len(resultrow.index) == 0:
                    print("Error the excel file is empty or data not found for the given instrument at the given date. Check the instruments list with -l or try a recent date in the same year. Press enter to exit...")
                    Exit()
        else:
            prevrow = None
            for index, row in df.iterrows():
                if NoneRow(prevrow):
                    prevrow = row
                    continue
                currentdate = row['Report_Date_as_MM_DD_YYYY'].to_pydatetime()
                prevdate =  prevrow['Report_Date_as_MM_DD_YYYY'].to_pydatetime()
                if (indate > prevdate and indate < currentdate) or indate == prevdate:
                    resultrow = prevrow
                    break
                prevrow = row
            if NoneRow(resultrow):
                r = lastrow['Report_Date_as_MM_DD_YYYY'].values[0]
                ts = (r - datetime64('1970-01-01')) / timedelta64(1, 's')
                td = datetime.utcfromtimestamp(ts)
                if indate >= td:
                    resultrow = lastrow
                    cotdate = td
                else:
                    resultrow = Search(AddYears(indate, -1), symbol, True)
                    r = resultrow.head(1)['Report_Date_as_MM_DD_YYYY'].values[0]
                    ts = (r - datetime64('1970-01-01')) / timedelta64(1, 's')
                    td = datetime.utcfromtimestamp(ts)
                    cotdate = td
                    if len(resultrow.index) == 0:
                        print("Error the excel file is empty or data not found for the given instrument at the given date. Check the instruments list with -l or try a recent date in the same year. Press enter to exit...")
                        Exit()
            else:
                cotdate = resultrow['Report_Date_as_MM_DD_YYYY'].to_pydatetime()
    except Exception as e:
        print(f"Error while processing the SearchQuery in the filename {filename}. Press enter to exit...")
        Exit()
    result = {}
    marketname = ""
    try:
        marketname = resultrow['Market_and_Exchange_Names'].values[0]
    except Exception as e:
        marketname = resultrow['Market_and_Exchange_Names']
    try:
        # Modify the output here.
        result = {
            "MarketName": marketname,
            "InputDate": indate.strftime("%d/%m/%y"),
            "COTDate": cotdate.strftime("%d/%m/%y"),
            "OpenInterest": int(resultrow['Open_Interest_All']),
            "NonCommercialLong": int(resultrow['NonComm_Positions_Long_All']),
            "NonCommercialShort": int(resultrow['NonComm_Positions_Short_All']),
            "CommercialLong": int(resultrow['Comm_Positions_Long_All']),
            "CommercialShort": int(resultrow['Comm_Positions_Short_All']),
            "NonReptLong": int(resultrow['NonRept_Positions_Long_All']),
            "NonReptShort": int(resultrow['NonRept_Positions_Short_All']),
        }
    except Exception as e:
        print("Error data cannot be parsed. Press enter to exit...")
        Exit()
    if not range:
        PrintResult(result)
    else:
        return result

def PrintBanner():
    banner = """
        _  ___ ___ _____
       (_)/ __/ _ \_   _|
       | | (_| (_) || |
      _/ |\___\___/ |_|
     |__/

     https://github.com/JuliusNixi/jCOT

        """
    print(banner)

def PrintSymbols():
    print("Please wait, this can take a while with a large amount of data...")
    symbols = GetSymbols()
    print("Avaible symbols (format: CODE | MARKET | FUNDINDATAYEAR1-FUNDINDATAYEAR2-...):\n")
    for symbol in symbols:
        print(symbol)
    print("\n")

def UI():
    PrintBanner()
    while 1:
        choice = input("Do you want to get/update the COT Data? [Y/n]: ").replace(" ", "")
        if choice == "" or choice[0].lower() == "y":
            CheckData()
            break
        elif choice[0].lower() == "n":
            break
        else:
            print("Invalid choice.")
    while 1:
        choice = input("Do you want to see the avaible symbols? [Y/n]: ").replace(" ", "")
        if choice == "" or choice[0].lower() == "y":
            PrintSymbols()
            break
        elif choice[0].lower() == "n":
            break
        else:
            print("Invalid choice.")
    while 1:
        indate = input("Insert a date for a search query (type 'q' to quit).\nUse 'date' for a direct search or 'date:date' for a range search.\nDate is in format dd/mm/yyyy: ").replace(" ", "")
        edate = ""
        date1 = ""
        date2 = ""
        try:
            if indate == "":
                raise Exception("")
            if indate[0].lower() == 'q':
                print("Bye!")
                Exit()
            if indate.count(':') == 1:
                date1 = datetime.strptime(indate.split(":")[0], '%d/%m/%Y')
                date2 = datetime.strptime(indate.split(":")[1], '%d/%m/%Y')
                if date1 > date2:
                    raise Exception("")
            elif indate.count(':') > 1:
                raise Exception("")
            else:
                edate = datetime.strptime(indate, '%d/%m/%Y')
        except Exception as e:
            print("Invalid date, wrong format, empty, or start date most recent than stop date.")
            continue
        while 1:
            symbol = input("Insert the symbol for a search query (type 'q' to quit): ").replace(" ", "")
            if symbol == "":
                print("Empty symbol.")
                continue
            if indate[0].lower() == 'q':
                print("Bye!")
                Exit()
            if edate != "":
                Search(edate, symbol)
            elif date1 != "" and date2 != "" and edate == "":
                RangeSearch(date1, date2, symbol)
            break

def RangeSearch(date1, date2, symbol):
    print("Range date search require processing a large amount of data, it may take a while, please be patient.\nIf you need the data on a specific date, I recommend doing a direct search.")
    resultarray = [Search(date1, symbol, range=True)]
    processdate = datetime.strptime(resultarray[0]["COTDate"], '%d/%m/%y')
    while (processdate <= date2):
        processdate += timedelta(days=7)
        resultarray.append(Search(processdate, symbol, range=True))
    PrintResult(resultarray[0], printheader=True)
    for result in resultarray[1:]:
        PrintResult(result, printheader=False)

def GetSymbols():
    symbols = []
    if not isdir(foldername):
        print("Error COTData folder not found. First get the COT data and then retry. Press enter to exit...")
        Exit()
    if len(listdir(foldername)) == 0:
        print("Error COTData folder is empty. Press enter to exit...")
        Exit()
    for filename in listdir(foldername):
        if not ".xls" in filename:
            print("Error unrecognized files in the COTData folder. Press enter to exit...")
            Exit()
        else:
            try:
                wb = xlrd.open_workbook(foldername + filename, logfile=open(devnull, 'w'))
                df = pd.read_excel(wb, dtype = {'CFTC_Contract_Market_Code': 'str'})
                for index, row in df.iterrows():
                    sym = str(row['CFTC_Contract_Market_Code']) + " | " + row['Market_and_Exchange_Names']
                    year = str(filename.replace("dea_fut_xls_", "").replace("deafut_xls_","").replace(".xls", ""))
                    found = -1
                    for i in range(len(symbols)):
                        if sym in symbols[i]:
                            found = i
                            break
                    if found != -1:
                        if not year in symbols[found]:
                            symbols[found] += "-" + year
                    else:
                        symbols.append(sym + " | " + year)
            except Exception as e:
                print(f"Error reading {filename} in the COTData folder. Press enter to exit...")
    return symbols

def PrintResult(result, printheader = True):
    if printheader:
        print("""

                ----------------------
                |        RESULT      |
                ----------------------

        """)
    separator = ''.join(['-' for e in list("MarketName: " + result["MarketName"])])
    print(separator)
    for key in result:
        print(key + ": " + str(result[key]))
    print(separator)
    print('\n')

foldername = "COTData\\"
if __name__ == '__main__':
    if len(argv) <= 1:
        UI()
    else:
        if "--help" in argv or "-help" in argv or "-HELP" in argv or "--HELP" in argv or "-h" in argv or "--h" in argv or "-H" in argv or "--H" in argv:
            PrintBanner()
            print(f"""

Args list:
-h: Print this message.
-l: Get the list of found symbols with the corrisponding code avaible for a query search.
-u: Get the COT Data or update it if already downloaded, in this last case, it's optional.
-s <symbolCODE>: The symbol code used for a query search. Required. To get this you can first call the program with -l.
-d <date>: The date used for a query search. Required. Format dd/mm/yyyy.
           You can also perform a range data query between two dates. In this case the format will be dateStart:dateStop
           Where the dateStart and dateStop are in the format dd/mm/yyyy. Range data queries are slow, use it only if needed.

Examples of usage:
python {basename(__file__)} -u
python {basename(__file__)} -l
python {basename(__file__)} -u -s 099741 -d 03/04/2005
python {basename(__file__)} -s 099741 -d 05/06/2006
python {basename(__file__)} -s 099741 -d 01/01/2021:31/12/2021
            """)
        elif '-l' in argv or '--l' in argv or '--L' in argv or '-L' in argv:
            PrintBanner()
            PrintSymbols()
        else:
            PrintBanner()
            symbol = ""
            indate = ""
            date1 = ""
            date2 = ""
            update = False
            for i in range(len(argv)):
                if i == 0:
                    continue
                if argv[i][0] == '-' and not argv[i].lower() in ['-s', '-u', '-d']:
                    print("Error Unrecognized arg passed. Use -help for info.")
                    break
                if argv[i].lower() == "-s":
                    try:
                        symbol = argv[i + 1]
                    except Exception as e:
                        print("Error Wrong arg passed. Use -help for info.")
                        break
                elif argv[i].lower() == "-d":
                    try:
                        if argv[i + 1].count(':') == 1:
                            date1 = datetime.strptime(argv[i + 1].split(":")[0], '%d/%m/%Y')
                            date2 = datetime.strptime(argv[i + 1].split(":")[1], '%d/%m/%Y')
                            if date1 > date2:
                                raise Exception("")
                        elif argv[i + 1].count(':') > 1:
                            raise Exception("")
                        else:
                            indate = datetime.strptime(argv[i + 1], '%d/%m/%Y')
                    except Exception as e:
                        print("Error Wrong arg passed or wrong date or wrong format range date. Use -help for info.")
                        break
                elif argv[i].lower() == "-u":
                    update = True
                else:
                    try:
                        if not argv[i-1] in ['-s', '-u', '-d']:
                            raise Exception("Error")
                    except Exception as e:
                        print("Error Unrecognized arg passed. Use -help for info.")
                        break
            if (symbol != "" and indate == "" and date1 == "" and date2 == "") or (symbol == "" and (indate != "" or (date1 != "" and date2 != ""))):
                print("Error missing symbol or date.")
            if update:
                CheckData()
            if symbol != "" and indate != "":
                Search(indate, symbol)
            elif symbol != "" and indate == "" and date1 != "" and date2 != "":
                RangeSearch(date1, date2, symbol)
                

