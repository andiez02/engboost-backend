import requests

def translate_word(word):
    """
    Dịch từ tiếng Anh sang tiếng Việt bằng Google Translate API miễn phí.
    """
    url = "https://translate.googleapis.com/translate_a/single"
    params = {
        "client": "gtx",
        "sl": "en",  # Source language (English)
        "tl": "vi",  # Target language (Vietnamese)
        "dt": "t",
        "q": word
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Kiểm tra lỗi HTTP

        # Parse kết quả
        translated_text = response.json()[0][0][0]
        return translated_text

    except requests.exceptions.RequestException as e:
        print(f"Error calling Google Translate API: {e}")
        return "Không tìm thấy"
