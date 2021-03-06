import looter as lt
import os
import json
import requests
import pytest
import random
import re


domain = 'konachan.com'
broken_domain = 'konichee.com'

# test main functions


@pytest.mark.ok
def test_fetch():
    tree = lt.fetch(f'{domain}/post')
    imgs = tree.css('a.directlink::attr(href)').extract()
    assert len(imgs) > 0 and isinstance(imgs[0], str)
    assert not lt.fetch(broken_domain)


@pytest.mark.ok
def test_alexa_rank():
    r = lt.alexa_rank(domain)
    assert isinstance(r, tuple) and len(r) == 3
    assert not lt.alexa_rank(broken_domain)


@pytest.mark.ok
def test_links():
    res = lt.send_request(domain)
    r = lt.links(res)
    wikis = lt.links(res, search='wiki')
    assert isinstance(r, list)
    assert '#' not in r and '' not in r
    assert len(set(r)) == len(r)
    assert all(['wiki' in wiki for wiki in wikis])


@pytest.mark.ok
def test_re_links():
    res = lt.send_request(f'{domain}/post')
    hrefs = lt.re_links(res, r'https://konachan.com/wiki/.*?')
    assert isinstance(hrefs, list) and len(hrefs) > 5


@pytest.mark.ok
def test_save_as_json():
    data = [{'rank': 2, 'name': 'python'}, {'rank': 1, 'name': 'js'}, {'rank': 3, 'name': 'java'}]
    lt.save_as_json(data, sort_by='rank')
    with open('data.json', 'r') as f:
        ordered_data = json.loads(f.read())
    assert ordered_data[0]['rank'] == 1
    os.remove('data.json')
    dup_data = [{'a': 1}, {'a': 1}, {'b': 2}]
    lt.save_as_json(dup_data, no_duplicate=True)
    with open('data.json', 'r') as f:
        unique_data = json.loads(f.read())
    assert len(dup_data) > len(unique_data)
    os.remove('data.json')


@pytest.mark.ok
def test_parse_robots():
    robots_url = lt.parse_robots(f'{domain}/post')
    assert isinstance(robots_url, list) and len(robots_url) > 5
    assert not lt.parse_robots(broken_domain)


@pytest.mark.ok
def test_login():
    params = {'df': 'mail126_letter', 'from': 'web', 'funcid': 'loginone', 'iframe': '1', 'language': '-1', 'passtype': '1', 'product': 'mail126',
              'verifycookie': '-1', 'net': 'failed', 'style': '-1', 'race': '-2_-2_-2_db', 'uid': 'webscraping123@126.com', 'hid': '10010102'}
    postdata = {'username': 'webscraping123@126.com', 'savelogin': '1',
                'url2': 'http://mail.126.com/errorpage/error126.htm', 'password': '0up3VmfKCh22'}
    url = "https://mail.126.com/entry/cgi/ntesdoor?"
    res, ses = lt.login(url, postdata, params=params)
    index_url = re.findall(r'href = "(.*?)"', res.text)[0]
    index = ses.get(index_url)
    message_count = re.findall(
        r"('messageCount'.*?).*?('unreadMessageCount'.*?),", index.text)[0]
    assert message_count[0] == "'messageCount'"
    assert not lt.login(broken_domain, postdata)

# test utils

@pytest.mark.ok
def test_ensure_schema():
    assert lt.ensure_schema(domain).startswith('http')
    assert not lt.ensure_schema(f'http://{domain}').startswith('https')
    assert lt.ensure_schema('//fuckshit.png').startswith('https://')


@pytest.mark.ok
def test_get_domain():
    assert lt.get_domain(f'http://{domain}') == domain
    assert lt.get_domain(f'https://{domain}/post') == domain


@pytest.mark.ok
def test_send_request():
    res = lt.send_request(domain)
    assert isinstance(res, requests.models.Response)
    assert res.status_code == 200


@pytest.mark.ok
def test_rectify():
    name = '?sdad<>:4rewr?'
    r = lt.rectify(name)
    assert r == 'sdad4rewr'


@pytest.mark.ok
def test_get_img_name():
    tree = lt.fetch(f'{domain}/post')
    img = tree.css('a.directlink::attr(href)').extract_first()
    name = lt.get_img_name(img)
    random_name = lt.get_img_name(img, random_name=True)
    assert '%' not in name
    assert random_name != name


@pytest.mark.ok
def test_save_img():
    tree = lt.fetch(f'{domain}/post')
    img = tree.css('a.directlink::attr(href)').extract_first()
    name = lt.get_img_name(img)
    lt.save_img(img)
    with open(name, 'rb') as f:
        img_data = f.read()
    assert isinstance(img_data, bytes) and len(img_data) > 100
    assert not lt.save_img(broken_domain)
    os.remove(name)


@pytest.mark.ok
def test_expand_num():
    assert lt.expand_num('61.8K') == 61800
    assert lt.expand_num('61.8M') == 61800000
    assert lt.expand_num('61.8') == 61.8
    assert lt.expand_num('61') == 61


@pytest.mark.ok
def test_read_cookies():
    url = 'http://httpbin.org/cookies'
    cookies = lt.read_cookies(filename='./looter/examples/cookies.txt')
    r = lt.send_request(url, cookies=cookies)
    assert dict(cookies.items()) == r.json()['cookies']
