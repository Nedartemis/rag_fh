import base64
from typing import Callable

import streamlit.components.v1 as components


def _download_event(bytes_to_download: bytes, download_filename):

    b64 = base64.b64encode(bytes_to_download).decode()

    dl_link = f"""
    <html>
    <head>
    <title>Start Auto Download file</title>
    <script src="http://code.jquery.com/jquery-3.2.1.min.js"></script>
    <script>
    $('<a href="data:text/csv;base64,{b64}" download="{download_filename}">')[0].click()
    </script>
    </head>
    </html>
    """
    return dl_link


def build_dowload_event(
    compute_data: Callable[[], bytes], filename: str
) -> Callable[[], None]:
    return lambda: components.html(
        _download_event(compute_data(), filename),
        height=0,
    )
