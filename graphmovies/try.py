import requests
import re

headers = {
    'Host': 'www.graphmovies.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
}

home_url = 'http://www.graphmovies.com/home/2/'

response = requests.get(home_url, headers=headers)
print(response)

pattern = re.compile('get.php\?orkey=(.*?)\',', re.S)
result = re.search(pattern, response.text)
print(result.group(1))

token = result.group(1)

print(token)

data = {
    'p': '0',
    'type': 'movie',
    't': '0',
    'sort': '1',
    'tag': '3',
    'zone': '2',
    'showtime': '11',
    'level': '0',
}

index_headers = {
    'Host': 'www.graphmovies.com',
    'Origin': 'http://www.graphmovies.com',
    'Referer': 'http://www.graphmovies.com/home/2/',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
}

index_url = 'http://www.graphmovies.com/home/2/get.php?orkey=' + token

response = requests.post(index_url, data=data, headers=index_headers)
print(response.status_code)

# print(response.json())
print(response.text)

items = response.json().get('data', [])
for item in items:
    print(item)
    orkey = item['orkey']
    print(orkey)
    
    
    
    
    
