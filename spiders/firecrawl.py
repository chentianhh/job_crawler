# Install with pip install firecrawl-py
from firecrawl import FirecrawlApp

app = FirecrawlApp(api_key='fc-fa37e7a3bfdb45549eb380c4bef5a6ef')

response = app.scrape_url(url='https://www.yupao.com/zhaogong/a2c686c687c688c689c690c1095/', params={
	'formats': [ 'markdown' ],
})