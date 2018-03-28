from io import BytesIO
from zipfile import ZipFile
import requests
import optparse
import os
from common import common

REQUEST_TOKEN = '06034873-f3e1-47b8-8bfb-45b11b3fc83d'
CLIENT_SECRET = 'e606642e20667a6b7b46b9644ce40a85d11a84da173d4d26f65cd5826121ec01'


def get_access_token():
    correct = False
    token = ''
    while not correct:
        r = requests.post("https://datos.hacienda.gov.py:443/odmh-api-v1/rest/api/v1/auth/token",
                          headers={"Authorization": REQUEST_TOKEN}, json='{"clientSecret": "%s"}' % CLIENT_SECRET)
        try:
            token = r.json()['accessToken']
            correct = True
        except:
            correct = False
    return token


def get_tender_ids(year):
    url = 'https://datos.hacienda.gov.py/odmh-core/rest/cdp/datos/cdp_%s.zip' % year
    print('Getting url %s' % url)
    resp = requests.get(url).content
    zipfile = ZipFile(BytesIO(resp))
    ids = []
    for line in zipfile.open('cdp_%s.csv' % year).readlines():
        print(line)
    return ids[1:]


def fetch_release(folder, id, bigquery=False):
    url = 'https://datos.hacienda.gov.py:443/odmh-api-v1/rest/api/v1/ocds/release-package/%s' % id
    print('Getting url %s' % url)
    data = common.getUrlAndRetry(url, folder, requestHeader={"Authorization": get_access_token()})
    if data:
        if bigquery:
            common.writeReleases(
                [data['releases']], folder, data, url)
        else:
            common.writeFile('%s.json' % str(id), folder, data, url)


def main():
    usage = 'Usage: %prog [ --all --cont ]'
    parser = optparse.OptionParser(usage=usage)

    parser.add_option('-a', '--all', action='store_true', default=False,
                      help='Fetch all records, rather than a small extract')
    parser.add_option('-R', '--resume', action='store_true', default=False,
                      help='Continue from the last page (in page.n), for when \
                      download broken')
    parser.add_option('-y', '--year', action='store', type="int", default=2016,
                      help='Which year to fetch activities from')
    parser.add_option('-s', '--skip', action='store_true',
                      default=False,
                      help='Skip downloads if file already exists')
    parser.add_option('-b', '--bigquery', action='store_true',
                      default=False, help='Fetch records in bigquery format')
    (options, args) = parser.parse_args()

    release_package_ids = []
    if options.all:
        for year in range(2011, 2012):
            release_package_ids += get_tender_ids(year)
    else:
        release_package_ids += get_tender_ids(options.year)
    release_package_ids = set(release_package_ids)
    release_package_ids = list(release_package_ids)
    print('%s record packages to retrieve' % len(release_package_ids))
    page = 0
    folder = os.path.dirname(os.path.realpath(__file__))
    page_file = folder + "/page.n"
    if options.resume:
        with open(page_file, 'r') as n:
            page = int(n.read())

    if options.all:
        folder += '/all'
    else:
        folder += '/sample'
        release_package_ids = release_package_ids[:4]
    for release_id in release_package_ids[page:]:
        if options.skip:
            release_file = '%s/records/ocds-03ad3f-%s.json' % \
                (folder, release_id)
            if os.path.isfile(release_file):
                print('record exists, skipping %s' % release_file)
                page += 1
                continue
        fetch_release(folder, release_id, options.bigquery)
        page += 1
        with open(page_file, 'w') as n:
            n.write(str(page))
    with open(page_file, 'w') as n:
        n.write(str('1'))


if __name__ == '__main__':
    main()
