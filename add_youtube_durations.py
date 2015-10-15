import requests
import re
import optparse


def load_youtube_api_key():
    try:
        return open('youtube_api_key.txt', 'r').read().strip()
    except:
        print('Add file called youtube_ api.txt and insert a youtube api key.')
        print('Youtube api key can be obtained at: https://console.developers.google.com.')
        exit(0)

def get_number_of_lines(file_name):
    with open(file_name, 'r') as f:
        for i, l in enumerate(f):
            pass
    return i + 2
        
def get_duration(json_video):
    hours = 0
    minutes = 0
    seconds = 0
    s = json_video['items'][0]['contentDetails']['duration']
    match = re.match(r'PT([0-5]?[\d])M([0-5]?[\d]?)S?', s)
    if match:
        items = match.groups()
        minutes = items[0]
        seconds = items[1]
    else:
        match_with_hours = re.match(r'PT([\d]?[\d])H([0-5]?[\d]?)M?([0-5]?[\d]?)S?', s)
        if match_with_hours:
            items = match_with_hours.groups()
            hours = items[0]
            minutes = items[1]
            seconds = items[2]

    return hours, minutes, seconds

def print_duration(duration):
    hours = duration[0]
    minutes = duration[1]
    seconds = duration[2]
    output = ' ['
    if hours == '':
        output += '00'
    else:
        output += '0' + str(hours)
    output += ':'
    if minutes == '':
        output += '00'
    elif int(minutes) < 10:
        output += '0' + minutes
    else:
        output += minutes
    output += ':'
    if seconds == '':
        output += '00'
    elif int(seconds) < 10:
        output += '0' + seconds
    else:
        output += seconds
    output += ']'
    return output

def handle_log(log):
    print('Done!')
    if not log:
        print('Everything went well!')
    else:
        print('\n'.join(log))

def main():
    youtube_api_key = load_youtube_api_key()

    parser = optparse.OptionParser('usage%prog -f <target_file>')
    parser.add_option('-f', dest='input_file', type='string', help='specify input file')
    (options, args) = parser.parse_args()
    input_file = options.input_file

    log = []

    number_of_lines = get_number_of_lines(input_file)
    with open(input_file, 'r+') as f:
        data = f.read()
        new_data = []
        line_counter = 0
        for line in data.split('\n'):
            line_counter += 1
            print('Parsing line: ' + str(line_counter) + ' of ' + str(number_of_lines))
            has_been_added_earlier = re.findall('\[\d\d:\d\d:\d\d\]', line)
            if has_been_added_earlier:
                new_data.append(line)
            else:
                youtube_match = re.findall('http[s]?://www.youtube.com/watch\?v\=[a-zA-Z0-9_-]+', line)
                if youtube_match:
                    link = youtube_match[0]
                    video_id = link.split('=')[1]
                    try:
                        r = requests.get('https://www.googleapis.com/youtube/v3/videos?key=' + youtube_api_key + '&part=contentDetails&id=' + video_id)
                    except:
                        log.append('The request to the youtube API went wrong. Video id: ' + video_id + '.  Youtube api key: ' + youtube_api_key + '.')
                    duration = get_duration(r.json())
                    new_line = re.split('(\))', line)
                    new_line[1] += print_duration(duration)
                    new_data.append(''.join(new_line))
                    print(''.join(new_line))
                else:
                    new_data.append(line)
        f.seek(0) # set file cursor to start of file
        f.write('\n'.join(new_data))
    handle_log(log)

if __name__ == '__main__':
    main()
