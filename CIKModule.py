import requests
import boto3
from datetime import date


class Edgar:

    #Simple Initialization
    def __init__(self, fileurl):
        self.fileurl = fileurl
        self.namedict = {}
        self.ticker = {}
        self.cik_data = {}


        # Date variables
        todayDate =  date.today()
        self.year = int(todayDate.strftime("%Y"))
        self.month = int(todayDate.strftime("%m"))

        #SEC Authorization
        self.headers = {'user-agent': 'MLT JO jmo7728@nyu.edu'}
        r = requests.get(self.fileurl, headers=self.headers)
        self.filejson = r.json 

        #Saving all company cik data
        for item in self.filejson().values():
            cik = item.get('cik_str')
            name = item['title'].lower()
            ticker = item['ticker'].lower()
            self.namedict[name] = cik
            self.ticker[ticker] = cik
            self.cik_data[cik] = (cik, name, ticker)

        

    """
    Looks up a company's Central Index Key (CIK) using it's name and
    returns the full company info as a tuple.
    """

    """
    Private methods
    """
    def _get_json_details(self,cik,year):
        r = requests.get(f"https://data.sec.gov/submissions/CIK{cik}.json", headers=self.headers)
        return r.json


     # Get Requests from a url
    def _run_requests_command(self,url):
        result = requests.get(url, headers=self.headers)
        return result.text

    def _quarter_calculation(self, month):
        if month == "":
            return 0
        if(int(month) <= 4):
            return 1
        if(int(month) <= 6):
            return 2
        if(int(month) <= 9):
            return 3
        return 4
    
    # Type the name of company to get cik data
    def name_to_cik(self, name):
        cik = self.namedict.get(name.lower())
        if cik:
            return self.cik_data[cik]
        else:
            return "Company not found."     


   # Retrieves the full company info by searching with the company's stock ticker symbol
    def ticker_to_cik(self, ticker):
        cik = self.ticker.get(ticker.lower())
        if cik:
            return self.cik_data[cik]
        else:
            return "Ticker not found."

    #Get a companys 10-K proving their cik number and year
    def annual_filing(self, cik, year):
        if year > self.year or (year >= self.year and self.month > 11):
            print("Report has not been filed yet")

        jsonfile = self._get_json_details(cik,year)()
        accessionNumber = ""
        primaryDocument = ""
        for index, item in enumerate(jsonfile.get('filings').get('recent').get('accessionNumber')):
            currItem = item.split("-")
            if currItem[1] == str(year)[2:4] and jsonfile.get('filings').get('recent').get('form')[index] == "10-K":
                accessionNumber = "".join(currItem)
                primaryDocument = jsonfile.get('filings').get('recent').get("primaryDocument")[index]

        print(f"https://www.sec.gov/Archives/edgar/data/{cik}/{accessionNumber}/{primaryDocument}")

        
                
        # content = self._run_requests_command(f"https://www.sec.gov/Archives/edgar/data/{cik}/{accessionNumber}/{primaryDocument}")
        # if content:
        #     print(content)
        # else:
        #     print("DNE")

    

    #Get a company's 10-Q using cik number, year of report, and quarter
    def quarterly_filing(self, cik, year, quarter):
        if year > self.year or (year >= self.year and self._quarter_calculation(self.month) > quarter):
            print("Filing has not been reported yet")
        jsonfile = self._get_json_details(cik,year)()
        accessionNumber = ""
        primaryDocument = ""
        yearOffset = 0
        jsonfileAccessPath = jsonfile.get('filings').get('recent')

        for index, item in enumerate(jsonfileAccessPath.get('accessionNumber')):
            currItem = item.split("-")
            try:
                currQuarter = self._quarter_calculation(jsonfileAccessPath.get('reportDate')[index].split("-")[1])
            except:
                continue
            if currQuarter == 4:
                yearOffset = 1


            # DEBUGGING
            # if(jsonfileAccessPath.get('form')[index] == "10-Q"):
            #     print("Date split up=",jsonfileAccessPath.get('reportDate')[index].split("-")[1])
            #     print("currYear=",currItem[1])
            #     print("formType=", jsonfileAccessPath.get('form')[index])
            #     print("currQuarter=", currQuarter)
            #     print("Accession Number=", item)
            #     print("\n")

            if currItem[1] == str(year + yearOffset)[2:4] and jsonfileAccessPath.get('form')[index] == "10-Q" and currQuarter == quarter:

                
                accessionNumber = "".join(currItem)
                primaryDocument = jsonfileAccessPath.get('primaryDocument')[index]


            yearOffset = 0

        print(f"https://www.sec.gov/Archives/edgar/data/{cik}/{accessionNumber}/{primaryDocument}")

    # def lambda_handler(event,context):
    #     s3 = boto3.client('s3')
    #     url = "https://www.sec.gov/files/company_tickers.json"
    #     response = requests.get(url)
    #     s3.put_object(Bucket='sec-edgar-john', Key='company_tickers.json', Body=response.content)

se = Edgar("https://www.sec.gov/files/company_tickers.json")

# # se.annual_filing("0000320193",2024)
# se.quarterly_filing("0000320193", 2024, 2)

print("\n--- Annual Filing Test (Apple 10-K 2023) ---")
se.annual_filing("0000320193", 2023)
# Expected: accession number pieces for Apple’s 10-K in 2023 and its primary document (e.g. aapl-20230930.htm)

print("\n--- Quarterly Filing Test (Apple 10-Q Q2 2024) ---")
se.quarterly_filing("0000320193", 2024, 2)
# Expected: accession number and primary document for Apple’s Q2 2024 10-Q

print("\n--- Quarterly Filing Test (Apple 10-Q Q1 2023) ---")
se.quarterly_filing("0000320193", 2023, 1)
# Expected: accession number and primary document for Apple’s Q1 2023 10-Q