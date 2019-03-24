"""This function used to get various IP proxies which enables us to scrape the websites faster
The function returns a list of 110 working porxies"""

def ip_fetcher():

    try:

        working_proxy = []
        # you can sign-up on https://www.proxyrotator.com/ for free to get your own APIKey
        keys = ['API_KEY_1', 'API_KEY_2'] #enter your API keys for the IP fetcher
        for key in keys: #this block is used to gather the proxies
            for i in range(50): #since the daily limit per account is 50 IPs
                url = 'http://falcon.proxyrotator.com:51337/'

                params = dict(
                apiKey= key
                )

                resp = requests.get(url=url, params=params)
                data = json.loads(resp.text)

                working_proxy.append(data['ip'] + ":" + data['port'])

        #this loop fetches the proxies from yet another free proxy service
        for i in range(10):
            url = "https://gimmeproxy.com/api/getProxy"
            r = requests.get(url)
            dat = r.json()
            working_proxy.append(dat['ipPort'])

        #saves the proxy to a text file which can be accessed within any program
        with io.open(f'proxies.txt', 'w', encoding='utf-8') as f:
            f.write(json.dumps(working_proxy, ensure_ascii=False))

        print("Successfully retrieved all the proxy IPs!")

    except:
        print("Daily proxy limit crossed. Fetching saved proxies.....")
        working_proxy = eval(open('proxies.txt', encoding='utf-8').read())

    return working_proxy
