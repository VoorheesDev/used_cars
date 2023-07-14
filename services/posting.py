import os

import requests
from dotenv import load_dotenv


load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

URL_SEND_MESSAGE = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
URL_EDIT_MESSAGE = f"https://api.telegram.org/bot{API_TOKEN}/editMessageCaption"
URL_SEND_MEDIA = f"https://api.telegram.org/bot{API_TOKEN}/sendMediaGroup"


def repeat_request_on_failure(func):
    def wrapper_repeat_request(*args, **kwargs):
        response = func(*args, **kwargs)
        while response.status_code != 200:
            response = func(*args, **kwargs)
        return response

    return wrapper_repeat_request


@repeat_request_on_failure
def send_post_request(url: str, payload: dict) -> requests.Response:
    return requests.post(url, json=payload)


def create_post(images: list[str], caption: str, parse_mode: str = "MarkdownV2") -> int:
    photos = [{"type": "photo", "media": image} for image in images]
    photos[0].update(caption=caption, parse_mode=parse_mode)  # set a caption for entire post
    response = send_post_request(URL_SEND_MEDIA, {"chat_id": CHANNEL_ID, "media": photos})
    data = response.json()
    post_id = data["result"][0]["message_id"]
    return post_id


def edit_post_caption(post_id: int, caption: str, parse_mode: str = "MarkdownV2") -> None:
    send_post_request(
        URL_EDIT_MESSAGE,
        {
            "chat_id": CHANNEL_ID,
            "message_id": post_id,
            "caption": caption,
            "parse_mode": parse_mode,
        },
    )


def reply_to_post(post_id: int, text: str, parse_mode: str = "MarkdownV2") -> None:
    send_post_request(
        URL_SEND_MESSAGE,
        {
            "chat_id": CHANNEL_ID,
            "text": text,
            "parse_mode": parse_mode,
            "reply_to_message_id": post_id,
        },
    )


def update_post(
    post_id: int, caption: str, reply_text: str | None = None, parse_mode: str = "MarkdownV2"
) -> None:
    if reply_text is None:
        reply_text = "The post has been updated"

    edit_post_caption(post_id, caption, parse_mode)
    reply_to_post(post_id, reply_text, parse_mode)
