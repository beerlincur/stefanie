import os
from typing import List

from instaloader import Instaloader, Post


def get_shortcode_from_url(url: str) -> str:
    return url.split("/")[4]


def download_insta_post(url: str) -> List[str]:
    shortcode = get_shortcode_from_url(url)

    loader = Instaloader()

    post = Post.from_shortcode(loader.context, shortcode)

    loader.download_post(post, "post")
    photos = []
    for t in os.walk("post"):
        files = t[2]
        for f in files:
            if f.endswith(".jpg"):
                photos.append("post/" + f)

    return photos

# download_insta_post("https://www.instagram.com/p/CHf2R53jG44/?utm_source=ig_web_copy_link")
