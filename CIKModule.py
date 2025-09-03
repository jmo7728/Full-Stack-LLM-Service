import requests

class Edgar:
    def __init__(self, fileurl):
        self.fileurl = fileurl
        self.namedict = {}
        self.ticker = {}
        self.cik_data = {}


        headers = {'user-agent': 'MLT GS jmo7728@nyu.edu'}
        r = requests.get(self.fileurl, headers=headers)
        self.filejson = r.json

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
    def name_to_cik(self, name):
        cik = self.namedict.get(name.lower())
        if cik:
            return self.cik_data[cik]
        else:
            return "Company not found."     

    """
    Retrieves the full company info by searching with the company's
    stock ticker symbol.
    """
    def ticker_to_cik(self, ticker):
        cik = self.ticker.get(ticker.lower())
        if cik:
            return self.cik_data[cik]
        else:
            return "Ticker not found."


se = Edgar("https://www.sec.gov/files/company_tickers.json")
