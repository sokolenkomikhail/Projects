import requests
from lxml import html
from datetime import datetime
import time
import json
import os
import numpy as np


def get_dom(url):
    header = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0'}
    response = requests.get(url, headers=header)
    dom = html.fromstring(response.text)
    return dom


def get_token_id(block):
    try:
        name_block = block[0].xpath('.//div[@class="sc-16r8icm-0 gpRPnR nameHeader"]')
        src = name_block[0].xpath('.//img[@src]//@src')[0]
        token_id = src.split('/')[-1][:-4]
        alt = name_block[0].xpath('.//img[@src]//@alt')[0]
        name = name_block[0].xpath('.//h2[@class="sc-1q9q90x-0 jCInrl h1"]')[0].text
        name = name.replace(' ', '-')
    except IndexError:
        token_id = name = alt = None
    return token_id, name, alt


def get_tags(block):
    path = './/div[@class="sc-16r8icm-0 sc-10up5z1-1 gGKCJe"]//a[@class="cmc-link"]//div[@class="tagBadge"]'
    tags_list = []
    try:
        tags = block[0].xpath(path)
        for el in tags:
            tag = el.text.replace(' ', '-')
            tags_list.append(tag)
    except IndexError:
        return
    return tuple(set(tags_list))


def get_project_link(block):
    try:
        link_block = block[0].xpath('.//div[@class="sc-16r8icm-0 sc-10up5z1-1 eUVvdh"]//ul[@class="content"]//li')[0]
        project_link = link_block.xpath('.//a[@class="link-button"]//@href')[0]
    except IndexError:
        project_link = None

    return project_link


def get_supply(block):
    try:
        max_supply_block = block[0].xpath('.//div[@class="sc-16r8icm-0 dwCYJB"]')
        max_supply = max_supply_block[0].xpath('.//div[@class="maxSupplyValue"]')[0].text
        max_supply = max_supply.replace(',', '')
        if max_supply.isdigit():
            max_supply = float(max_supply)
    except IndexError:
        max_supply = None

    try:
        total_supply_block = block[0].xpath('.//div[@class="sc-16r8icm-0 hWTiuI"]')
        total_supply = total_supply_block[0].xpath('.//div[@class="maxSupplyValue"]')[0].text
        total_supply = total_supply.replace(',', '')
        if total_supply.isdigit():
            total_supply = float(total_supply)
    except IndexError:
        total_supply = None

    return max_supply, total_supply


def get_holders_ratio(params):
    url = 'https://api.coinmarketcap.com/data-api/v3/cryptocurrency/detail/holders/ratio'
    time.sleep(0.5)
    response = requests.get(url, params=params)
    try:
        data = json.loads(response.text)['data']
        points = data['points']
    except KeyError:
        return
    holders_ratio = {}
    keys = sorted(points.keys())
    for key in keys:
        date = str(datetime.strptime(key.split('T')[0], "%Y-%m-%d").replace(day=1))
        if date not in holders_ratio:
            holders_ratio[date] = {
                'topTenHolderRatio': [],
                'topTwentyHolderRatio': [],
                'topFiftyHolderRatio': [],
                'topHundredHolderRatio': []
            }
            continue
        for k, value in points[key].items():
            holders_ratio[date][k].append(value)

    for date in holders_ratio.keys():
        for key in holders_ratio[date].keys():
            if holders_ratio[date][key]:
                holders_ratio[date][key] = round(np.mean(holders_ratio[date][key]), 2)
            else:
                holders_ratio[date][key] = None

    return holders_ratio


def get_holders_count(params):
    url = 'https://api.coinmarketcap.com/data-api/v3/cryptocurrency/detail/holders/count'
    time.sleep(0.5)
    response = requests.get(url, params=params)
    try:
        data = json.loads(response.text)['data']
        points = data['points']
    except KeyError:
        return
    holders_count = {}
    keys = sorted(points.keys())
    for key in keys:
        date = str(datetime.strptime(key.split('T')[0], "%Y-%m-%d").replace(day=1))
        if date not in holders_count:
            holders_count[date] = [1, points[key]]
            continue
        holders_count[date][1] += points[key]
        holders_count[date][0] += 1

    for date in holders_count:
        n, value = holders_count[date]
        value /= n
        holders_count[date] = round(value)

    return holders_count


def get_historical_data(params):
    url = 'https://api.coinmarketcap.com/data-api/v3/cryptocurrency/historical'
    time.sleep(0.5)
    response = requests.get(url, params=params)
    try:
        data = json.loads(response.text)['data']
        quotes = data['quotes']
    except KeyError:
        return
    historical_data = {}
    for el in quotes:
        date = el['timeOpen']
        date = datetime.strptime(date.split('T')[0], "%Y-%m-%d").replace(day=1)
        if (date.year == 2020 and date.month < 9) or date.year < 2020:
            return
        date = str(date)
        if date not in historical_data:
            historical_data[date] = {
                'open': [],
                'volume': [],
                'marketCap': []
            }
        for key in historical_data[date].keys():
            historical_data[date][key].append(el['quote'][key])

    for date in historical_data.keys():
        for key in historical_data[date].keys():
            if historical_data[date][key]:
                historical_data[date][key] = round(np.mean(historical_data[date][key]), 2)
            else:
                historical_data[date][key] = None

    return historical_data


def get_project_info(params):
    url = 'https://api.coinmarketcap.com/data-api/v3/project-info/detail'
    time.sleep(0.5)
    response = requests.get(url, params=params)
    try:
        data = json.loads(response.text)['data']
        distrib = data['trs']['distributions']
    except KeyError:
        return
    distributions = {}
    for elem in distrib:
        distributions[elem['holder']] = elem['percentage']
    return distributions


def get_markets(params):
    url = 'https://api.coinmarketcap.com/data-api/v3/cryptocurrency/market-pairs/latest'
    time.sleep(0.5)
    response = requests.get(url, params=params)
    try:
        data = json.loads(response.text)['data']
        market_pairs = data['marketPairs']
    except KeyError:
        return
    markets = []
    for pairs in market_pairs:
        markets.append(pairs['exchangeName'])
    return tuple(set(markets))


def get_data_from_api(token_id, name, main_block):
    blocks_xpath = './/div[@class="container routeSwitcher"]/span/a'
    blocks = main_block[0].xpath(blocks_xpath)

    token_distr = holders_count = holders_ratio = markets = None
    for block in blocks:
        href = block.xpath('.//@href')[0]
        href_tokens = href.split('/')
        if href_tokens[3] == 'project-info':
            params = {
                'slug': name
            }
            token_distr = get_project_info(params)

        elif href_tokens[3] == 'holders':
            params = {
                'id': token_id,
                'range': '1y'
            }
            holders_count = get_holders_count(params)
            holders_ratio = get_holders_ratio(params)

        elif href_tokens[3] == 'markets':
            params = {
                'slug': name
            }
            markets = get_markets(params)

    return token_distr, holders_count, holders_ratio, markets


def put_to_holders(name, holders_count, holders_ratio):
    months = (
        '2020-09-01 00:00:00',
        '2020-10-01 00:00:00',
        '2020-11-01 00:00:00',
        '2020-12-01 00:00:00',
        '2021-01-01 00:00:00',
        '2021-02-01 00:00:00',
        '2021-03-01 00:00:00',
        '2021-04-01 00:00:00',
        '2021-05-01 00:00:00',
        '2021-06-01 00:00:00',
        '2021-07-01 00:00:00',
        '2021-08-01 00:00:00',
        '2021-09-01 00:00:00'
    )
    data = [name]
    for m in months:
        tmp = []
        if holders_count is not None:
            if m in holders_count:
                tmp += [holders_count[m]]
            else:
                tmp += [None]
        else:
            tmp += [None]
        if holders_ratio is not None:
            if m in holders_ratio:
                tmp += [
                    holders_ratio[m]['topTenHolderRatio'],
                    holders_ratio[m]['topTwentyHolderRatio'],
                    holders_ratio[m]['topFiftyHolderRatio'],
                    holders_ratio[m]['topHundredHolderRatio']
                ]
            else:
                tmp += [None] * 4
        else:
            tmp += [None] * 4

        data += tmp
    filename = 'holders.tsv'
    if filename not in os.listdir():
        columns = [
            'Holders count',
            'Top 10 holders',
            'Top 20 holders',
            'Top 50 holders',
            'Top 100 holders'
        ]
        columns = ['Name'] + columns * len(months)
        with open(filename, 'a') as f:
            f.write('\t'.join(columns) + '\n')

    with open(filename, 'a') as f:
        f.write('\t'.join(map(str, data)) + '\n')

    return


def put_to_cap(name, hist_data):
    months = (
        '2020-09-01 00:00:00',
        '2020-10-01 00:00:00',
        '2020-11-01 00:00:00',
        '2020-12-01 00:00:00',
        '2021-01-01 00:00:00',
        '2021-02-01 00:00:00',
        '2021-03-01 00:00:00',
        '2021-04-01 00:00:00',
        '2021-05-01 00:00:00',
        '2021-06-01 00:00:00',
        '2021-07-01 00:00:00',
        '2021-08-01 00:00:00',
        '2021-09-01 00:00:00'
    )
    data = [name]
    for m in months:
        tmp = []
        if hist_data is not None:
            if m in hist_data:
                tmp += [
                    hist_data[m]['open'],
                    hist_data[m]['volume'],
                    hist_data[m]['marketCap']
                ]
            else:
                tmp += [None] * 3
        else:
            tmp += [None] * 3

        data += tmp
    filename = 'cap.tsv'
    if filename not in os.listdir():
        columns = [
            'Avg Price',
            'Avg Volume',
            'Avg Market Capitalization'
        ]
        columns = ['Name'] + columns * len(months)
        with open(filename, 'a') as f:
            f.write('\t'.join(columns) + '\n')

    with open(filename, 'a') as f:
        f.write('\t'.join(map(str, data)) + '\n')

    return


def put_to_tokens(name, link, markets, tags, total_supply, max_supply, distribution):
    filename = 'tokens.tsv'
    data = (name, link, markets, tags, total_supply, max_supply, distribution)
    if filename not in os.listdir():
        columns = ('Name', 'Site', 'Markets', 'Tags', 'Total Supply', 'Max Supply', 'Token distribution')
        with open(filename, 'a') as f:
            f.write('\t'.join(columns) + '\n')
    with open(filename, 'a') as f:
        f.write('\t'.join(map(str, data)) + '\n')
    return


def main():
    hist_params = {
      'id': None,
      'convertId': 2781,
      'timeStart': int(datetime(2020, 1, 1).timestamp()),
      'timeEnd': int(datetime.today().timestamp())
    }

    root_url = 'https://coinmarketcap.com'
    main_block_xpath = './/div[@class="grid full-width-layout"]'
    dom = get_dom(root_url + '/tokens')

    last_page = dom.xpath('.//li[@class="page"]')[-1]
    href_last_page = last_page.xpath('.//a[@role="button"]//@href')[0]
    n_pages = int(href_last_page.split('=')[-1])
    # n_pages = 1
    start_time = time.time()
    for i in range(1, n_pages + 1):
        page_href = href_last_page.replace(str(n_pages), str(i))
        dom = get_dom(root_url + page_href)
        tokens = dom.xpath('.//div[@class="h7vnx2-1 bFzXgL"]//tr')
        print(f'Page: {i}')
        for token in tokens:
            href = token.xpath('.//a[@class="cmc-link"]//@href')
            if len(href) == 0:
                continue
            time.sleep(0.5)
            token_url = root_url + href[0]
            dom = get_dom(token_url)
            main_block = dom.xpath(main_block_xpath)

            token_id, name, alt = get_token_id(main_block)
            if token_id is None:
                continue

            tags = get_tags(main_block)

            hist_params['id'] = token_id
            hist_data = get_historical_data(hist_params)
            if hist_data is None:
                continue

            token_distr, holders_count, holders_ratio, markets = get_data_from_api(token_id, name, main_block)

            project_link = get_project_link(main_block)
            max_supply, total_supply = get_supply(main_block)

            name = ', '.join((name, alt))

            put_to_tokens(name, project_link, markets, tags, total_supply, max_supply, token_distr)
            put_to_holders(name, holders_count, holders_ratio)
            put_to_cap(name, hist_data)
        print(
            'Duration: '
            f'{str(int((time.time() - start_time) // 60)).zfill(2)}:'
            f'{str(int((time.time() - start_time) % 60)).zfill(2)}\n'
        )

    duration = time.time() - start_time

    hours = duration // 3600
    total_minutes = duration % 3600
    minutes = total_minutes // 60
    seconds = total_minutes % 60
    print(
        'Parsing is finished! \n'
        'Total duration: '
        f'{str(int(hours)).zfill(2)}:'
        f'{str(int(minutes)).zfill(2)}:'
        f'{str(int(seconds)).zfill(2)}'
    )


if __name__ == '__main__':
    main()
