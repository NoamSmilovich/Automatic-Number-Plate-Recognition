import requests
import json


def ocr_space_file(filename, overlay=False, api_key='b754bcd9cf88957', language='eng'):
    """ OCR.space API request with local file.
        Python3.5 - not tested on 2.7
    :param filename: Your file path & name.
    :param overlay: Is OCR.space overlay required in your response.
                    Defaults to False.
    :param api_key: OCR.space API key.
                    Defaults to 'helloworld'.
    :param language: Language code to be used in OCR.
                    List of available language codes can be found on https://ocr.space/OCRAPI
                    Defaults to 'en'.
    :return: Result in JSON format.
    """

    payload = {'isOverlayRequired': overlay,
               'apikey': api_key,
               'language': language,
               }
    with open(filename, 'rb') as f:
        r = requests.post('https://api.ocr.space/parse/image',
                          files={filename: f},
                          data=payload,
                          )
    return r.content.decode()


def ocr_space_url(url, overlay=False, api_key='b754bcd9cf88957', language='eng'):
    """
    :param url: Image url.
    :param overlay: Is OCR.space overlay required in your response.
                    Defaults to False.
    :param api_key: OCR.space API key.
                    Defaults to 'helloworld'.
    :param language: Language code to be used in OCR.
                    List of available language codes can be found on https://ocr.space/OCRAPI
                    Defaults to 'en'.
    :return: Result in JSON format.
    """

    payload = {'url': url,
               'isOverlayRequired': overlay,
               'apikey': api_key,
               'language': language,
               }
    r = requests.post('https://api.ocr.space/parse/image',
                      data=payload,
                      )
    return r.content.decode()


def get_lp_num(image_path):
    test_file = ocr_space_file(filename=image_path)
    results = json.loads(test_file)
    print(results)
    if results['IsErroredOnProcessing'] is False:
        parsed_text = results['ParsedResults'][0]['ParsedText']
        file_parse_message = file_parse_exit_message(results)
    else:
        parsed_text = ''
        file_parse_message = 'Error processing'
    return {
        'ParsedText': parsed_text,
        'IsError': results['IsErroredOnProcessing'],
        'OCRExitMessage': ocr_exit_message(results),
        'FileParseExitMessage': file_parse_message
    }


def ocr_exit_message(results):
    if results['OCRExitCode'] == 1:
        message = 'Parsed Successfully'
    elif results['OCRExitCode'] == 2:
        message = 'Parsed Partially'
    elif results['OCRExitCode'] == 3:
        message = 'OCR Engine Failed'
    elif results['OCRExitCode'] == 4:
        message = 'OCR Fatal Error'
    else:
        message = 'Unknown Error'
    return message


def file_parse_exit_message(results):
    if results['ParsedResults'][0]['FileParseExitCode'] == 0:
        message = 'File not found'
    if results['ParsedResults'][0]['FileParseExitCode'] == 1:
        message = 'Success'
    if results['ParsedResults'][0]['FileParseExitCode'] == -10:
        message = 'OCR Engine Parse Error'
    if results['ParsedResults'][0]['FileParseExitCode'] == -20:
        message = 'Timeout'
    if results['ParsedResults'][0]['FileParseExitCode'] == -30:
        message = 'Validation Error'
    else:
        message = 'Unknown Error'
    return message
