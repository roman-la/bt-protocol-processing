import re
from xml.etree import ElementTree


def process(protocols):
    speeches = __get_speeches(protocols)
    comments = __get_comments(speeches)
    return comments


def __get_speeches(protocols):
    speeches = []
    for protocol in protocols:
        root = ElementTree.fromstring(protocol['xml'])
        session_id = root.find('.//sitzungsnr').text
        for speech in root.iter('rede'):
            speaker_id = speech.find('.//redner').get('id')
            for comment in speech.iter('kommentar'):
                speeches.append((session_id, speaker_id, comment.text))
    return speeches


def __get_comments(speeches):
    comments = []
    for speech in speeches:
        session_id, speaker_id, raw_comment = speech

        if not re.match(r'^\(.+\[.+]:.+\)$', raw_comment):
            continue

        raw_comment = raw_comment[1:-1]  # remove parenthesis
        raw_comment = raw_comment.replace(' ', ' ')
        raw_comment = raw_comment.replace('­', '')

        for part in raw_comment.split(' – '):
            # TODO: prettier?
            if 'Gegenruf' in part:
                continue

            if ']: ' in part:
                comment = part.split(':')[1].strip()
                commenter = part.split('[')[0].strip().replace('Freiherr', 'Frhr.')  # TODO: prettier?
                comments.append((session_id, speaker_id, comment, commenter))

    return comments
