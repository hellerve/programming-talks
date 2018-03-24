"""
A script for generating upload date years for videos by scraping
metadata with youtube-dl.

You must have 'youtube-dl' available and installed.

Written by Casey Link (https://github.com/ramblurr)
based on duration script by Bruno Thalmann (https://github.com/thalmann).
"""
import requests
import re
import optparse
from subprocess import check_output
from urllib.parse import parse_qs


def get_number_of_lines(file_name):
    with open(file_name, 'r') as f:
        # no really, this is somehow faster than sum()
        return len([l for l in f])


def has_youtubedl():
    try:
        check_output(['youtube-dl', '--help'])
        return True
    except FileNotFoundError:
        return False


def get_release_year(link):
    try:
        response = check_output(['youtube-dl',
                                 link,
                                 '--skip-download',
                                 '--get-filename',
                                 '-o "%(release_date)s|%(upload_date)s"']
                                ).decode('utf-8').strip()
        release, upload = response.split("|")
        if release != '"NA':
            return release[:4]
        if upload != 'NA"':
            return upload[:4]
    except Exception as e:
        return None


def print_year(year):
    return ' (%s)' % (year.strip())


def handle_log(log):
    print('Done!')
    if not log:
        print('Everything went well!')
    else:
        print('\n'.join(log))


def main():
    parser = optparse.OptionParser('usage%prog -f <target_file>')
    parser.add_option('-f', dest='input_file', type='string',
                      help='specify input file')

    (options, args) = parser.parse_args()
    input_file = options.input_file

    if not has_youtubedl():
        print('error: you do not have youtube-dl available')
        return

    log = []

    number_of_lines = get_number_of_lines(input_file)
    with open(input_file, 'r+') as f:
        data = f.read()
        new_data = []
        for i, line in enumerate(data.split('\n'), 1):
            print('Parsing line: ' + str(i) + ' of ' + str(number_of_lines))
            has_been_added_earlier = re.findall('\(\d\d\d\d\)', line)
            if has_been_added_earlier:
                new_data.append(line)
                print(line)
            else:
                url_match = re.findall('(http[s]?://\S+)\)', line)
                if url_match:
                    link = url_match[0]
                    year = get_release_year(link)
                    if year:
                        new_line = line
                        new_line += print_year(year)
                        new_data.append(''.join(new_line))
                        print(''.join(new_line))
                    else:
                        new_data.append(line)
                        log.append('Failed: to get year for ' + link)
                else:
                    new_data.append(line)
        f.seek(0)  # set file cursor to start of file
        f.write('\n'.join(new_data))
    handle_log(log)


if __name__ == '__main__':
    main()

