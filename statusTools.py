from rich.console import Console
from rich.traceback import install
from rich.table import Table
from rich.text import Text
import pyperclip
import requests
install()
c = Console()

class Scanner:
    def __init__(self, verbose=False) -> None:
        self.database = []
        self.timeout = 2
        self.verbose = verbose
    
    def ping(self, host) -> bool:
        try:
            if self.verbose:
                c.print(f"[?] Checking URL: {host}")
            response = requests.get(f"http://{host}", timeout=self.timeout)
            if self.verbose:
                c.print(f"[?] Status code is {response.status_code}")
            return response.status_code == 200
        except requests.exceptions.ConnectTimeout:
            if self.verbose:
                c.print(f"[?] Except ConnectTimeout", style="red")
            return False
        except requests.exceptions.ReadTimeout:
            if self.verbose:
                c.print(f"[?] Except ReadTimeout", style="red")
            return False
        except requests.exceptions.Timeout:
            if self.verbose:
                c.print(f"[?] Except Timeout", style="red")
            return False
    
    def getTableFromClipboard(self) -> None:
        pasteDump = pyperclip.paste()
        RowSplit = pasteDump.split('\n')
        if self.verbose:
            c.print(f"[?] Found {len(RowSplit)} records")
        self.database = []
        for i in RowSplit:
            tempList = i.split('\t')
            DeviceName = tempList[0]
            IP = tempList[1].replace('\r', '')
            self.database.append({"device": DeviceName, "IP": IP, "status": "UnKown"})

    def parseInput(self, input, saveToDB=True, overwriteDB=True) -> list:
        if "." in input[0][0]:
            IPInd = 0
            NameInd = 1
        elif "." in input[0][1]:
            IPInd = 1
            NameInd = 0
        outDB = []
        for i in input:
            outDB.append({"IP": i[IPInd], "device": input[NameInd]})
        
        if saveToDB and overwriteDB:
            self.database = outDB
        elif saveToDB:
            self.database.append(outDB)
    
    def showTable(self) -> None:
        table = Table(title="Device")
        table.add_column("Device", justify="left")
        table.add_column("IP Addres", justify="center")
        table.add_column("Status", justify="center")

        for i in self.database:
            if i["status"] == "Online":
                statusStyle = "green"
            elif i["status"] == "Checking":
                statusStyle = "yellow"
            elif i["status"] == "Offline":
                statusStyle = "red"
            else:
                statusStyle = "white"
                
            table.add_row(i["device"], i["IP"], Text(i["status"], style=statusStyle, justify="center"))
        c.print(table)

    def generateStatistics(self) -> dict:
        stats = {}
        stats['totalDevices'] = len(self.database)
        stats['onlineDevices'] = 0
        for i in self.database:
            if i["status"] == "Online":
                stats['onlineDevices'] += 1
        onlinePercent = stats['onlineDevices'] / stats['totalDevices']
        stats['percentOnline'] = str(round((onlinePercent * 100), 1)) + "%"
        return stats
        

    def run(self) -> None:
        self.getTableFromClipboard()
        for i in self.database:
            c.clear()
            i["status"] = "Checking"
            self.showTable()
            if self.ping(i["IP"]):
                i["status"] = "Online"
            else:
                i["status"] = "Offline"
        
        c.clear()
        self.showTable()
        stats = self.generateStatistics()
        c.print(f"Total of {stats['totalDevices']} Devices")
        c.print(f"{stats['onlineDevices']} or {stats['percentOnline']} Online")

scanner = Scanner()
scanner.run()