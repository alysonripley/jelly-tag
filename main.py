import re
from pathlib import Path

def get_movie_files(directory):
    return [file for file in Path(directory).iterdir() if file.is_file()]

# Function to extract movie title, year, and tags from file name
def extract_movie_info(file_name):
    #file_name = "Black.Sheep.1995"
    #file_name = file_name.replace('.', ' ')  # Replace periods with spaces before extraction
    title_year_pattern = re.compile(r'.+(19).{2}(\))?|.+(20).{2}(\))?')


    year_pattern = re.compile(r'(19).{2}|(20).{2}')
    resolution_pattern = re.compile(r'\b(2160p|1080p|720p)\b', re.IGNORECASE)
    source_pattern = re.compile(r'\b(UHD|BluRay|blu-ray|DVD|DVDRip|WebRip|HDTV|HDTV Rip|Web Rip|HDTVRip|HDTV-Rip|VHS|VHS Rip|VHS-Rip|VHSRip)\b', re.IGNORECASE)
    codec_pattern = re.compile(r'\b(x264|x265|h264|h265|wvc1|vc1)\b', re.IGNORECASE)
    hdr_pattern = re.compile(r'\b(HDR|HDR10)\b', re.IGNORECASE)
    threed_pattern = re.compile(r'\b3D\b', re.IGNORECASE)

    title_match = title_year_pattern.search(file_name)
    year_match = year_pattern.search(file_name)


    title = title_match.group(0) if title_match else 'INVALID'
    cleaned_title = re.sub(r'\s?(\.)?(\()((19)|(20))\d{2}(\))?|(\.)((19)|(20))\d{2}', '', title)

    cleaned_title = re.sub(r'\s*\(\d{3,4}p\)', '', cleaned_title)
    cleaned_title = re.sub(r'\s*\[.*?\]', '', cleaned_title)
    #print(f"Cleaned Title: {cleaned_title}")
    #title = title.replace('.', ' ')
    year = year_match.group(0) if year_match else 'MISSING_YEAR'
    resolution_match = resolution_pattern.search(file_name)
    source_match = source_pattern.search(file_name)
    codec_match = codec_pattern.search(file_name)
    hdr_match = hdr_pattern.search(file_name)
    threed_pattern = threed_pattern.search(file_name)

    resolution = resolution_match.group(0) if resolution_match else 'MISSING_RES'
    source = source_match.group(0) if source_match else 'MISSING_SOURCE'
    codec = codec_match.group(0) if codec_match else 'MISSSING_CODEC'
    codec = codec.lower().replace('h', 'x')
    hdr = hdr_match.group(0) if hdr_match else None
    three_d = threed_pattern.group(0) if threed_pattern else None

    return cleaned_title, year, resolution, source, codec, hdr, three_d



def is_roman_numeral(s):
    # Check if the word is a Roman numeral (I, II, III, IV, V, etc.)
    roman_numerals = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X',
                      'XI', 'XII', 'XIII', 'XIV', 'XV', 'XVI', 'XVII', 'XVIII', 'XIX', 'XX']
    return s.upper() in roman_numerals

def format_movie_title(title):
    words = title.split(' ')
    formatted_title = []
    for i, word in enumerate(words):
        if word.lower() in ['a', 'an', 'and', 'the', 'in', 'of']:
            formatted_title.append(word.lower())
        elif is_roman_numeral(word):
            formatted_title.append(word.upper())  # Convert Roman numerals to uppercase
        elif word.isupper() and len(word) > 1 and not word.endswith('.'):
            formatted_title.append(word.capitalize())  # Capitalize all-uppercase words that are not acronyms
        elif word.isupper() and '.' in word and len(word) > 1:
            formatted_title.append(word)  # Keep acronyms with periods in uppercase
        else:
            formatted_title.append(word.capitalize())
    return ' '.join(formatted_title)


def fix_title_starting_with_the(title: str):
    if ', the' in title:
        title = title.replace(', the', ', The')
    return title

def fix_dash_title_with_the(title: str):
    if ' - the' in title:
        title = title.replace(' - the', ' - The')
    return title

def format_codec_tag(tag: str):
    if tag:
        if 'h' in tag.lower():
            tag = tag.lower().replace('h', 'x')
        elif tag.lower() == 'wvc1':
            tag = 'vc-1'
        elif tag.lower() == 'vc1':
            tag = 'vc-1'
    return tag

def format_hdr_tag(tag: str):
    if tag:
        return 'HDR' if len(tag) > 3 else tag.upper()

#Ultra HD Blu-ray (4K Ultra HD, UHD-BD, or 4K Blu-ray
def format_source_tag(tag: str):
    if tag:
        if tag.lower() in ('uhd', 'uhd blu-ray', 'uhd bluray', 'uhd blu ray', 'uhdbluray'):
            tag = '4K Blu-ray'
        elif tag.lower() in ('bluray', 'blu-ray', 'blu ray'):
            tag = 'Blu-ray'
        elif tag.lower() in ('hdtv', 'hdtv rip', 'hdtv-rip' 'hdtvrip'):
            tag = 'HDTV'
        elif tag.lower() in ('web', 'web rip', 'web-rip', 'webrip'):
            tag = 'WEB'
        elif tag.lower() in ('vhs', 'vhs rip', 'vhs-rip', 'vhsrip'):
            tag = 'VHS'
    return tag

# Function to rename movie file
def rename_movie_file(old_path, new_name):
    new_path = old_path.with_name(new_name)
    old_path.rename(new_path)

# Main function
def main(directory):
    print("original|renamed")
    movie_files = get_movie_files(directory)
    for file_path in movie_files:
        file_name = file_path.name
        title, year, resolution, source, codec, hdr, three_d = extract_movie_info(file_name)
        if title:
            formatted_title = format_movie_title(title)
            formatted_title = fix_title_starting_with_the(formatted_title)
            formatted_title = fix_dash_title_with_the(formatted_title)
            codec = format_codec_tag(codec)
            source = format_source_tag(source)
            #print(formatted_title)
            tags = [resolution, source, codec]
            if hdr:
                tags.append(hdr)
            if three_d:
                tags.append(three_d)
            formatted_tags = ' '.join([f'[{tag}]' for tag in tags])
            new_name = f"{formatted_title} ({year}) {formatted_tags}{file_path.suffix}"
            #new_name = new_name.replace(' ', '.')
            #rename_movie_file(file_path, new_name)  # Ensure file_path (Path object) is passed
            print(f"{file_name}|{new_name}")
        else:
            print(f"Could not extract info from: {file_name}")


if __name__ == "__main__":
    #directory = './tests/sample_dir/'
    directory = 'z:Movies/BluRay/rename'
    main(directory)
