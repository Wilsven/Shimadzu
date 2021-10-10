from bs4 import BeautifulSoup
import requests
import csv


def get_data(url): # function to parse data from webpage and append to csv 

	html_text = requests.get(url)
	soup = BeautifulSoup(html_text.text, 'lxml')

	with open('data.csv', 'a', encoding='utf8', newline='') as f:
		csv_writer = csv.writer(f)

		# get all articles with relevant tag and class
		articles = soup.find_all('li', class_='mb-2 vm-summary-link') 

		# try and except clause to circumvent missing components (i.e. some doesn't have summaries)
		for article in articles:
			try:
				headline = article.find('a', class_='d-block').text
			except:
				headline = None

			try:
				link = 'https://www.laboratorynetwork.com' + article.find('a', class_='d-block')['href']
			except:
				link = None

			try:
				published_date = article.find('em', class_='vm-hub-date').text
			except:
				published_date = None

			try:
				summary = article.find('div', class_='pt-1').p.text
			except:
				summary = None

			info = [headline, link, published_date, summary] # order entry by row
			csv_writer.writerow(info)


def get_nextpage(url):

    html_text = requests.get(url)
    soup = BeautifulSoup(html_text.text, 'lxml')
    page = soup.find('ul', class_='pagination')

    def forloop(page):
        for p in page.find_all('a', class_='page-link'):
            if p.text == 'Next':
                url = 'https://www.laboratorynetwork.com' + p['href']
                return url
    
    try:
        if page.find('li', class_='disabled page-item').text == 'Next':
            return
        else:
            return forloop(page)
    except:
        return forloop(page)


# Input url
url = 'https://www.laboratorynetwork.com/hub/bucket/homelatestheadlines' 

while True:
	get_data(url)
	url = get_nextpage(url) 

	if not url:
		print('Done!')
		break
    
