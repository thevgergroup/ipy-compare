"""
Small promo brand for the package.
"""

import base64
import pathlib
def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string


image = pathlib.Path(__file__).parent / "The VGER Group-share.png"

BASE64_ENCODED_LOGO = image_to_base64(image_path=image)

# Base64-encoded logo and branding text
footer_html = f"""
<div style="display: flex; justify-content: flex-end; align-items: center; padding: 10px; border-top: 1px solid #ccc;">
    <div>
    <a href="https://thevgergroup.com" target="_blank">
        <img src="data:image/png;base64,{BASE64_ENCODED_LOGO}" style="height: 40px; vertical-align: middle;">
    </a>
    </div>
    <div>
    <a href="https://thevgergroup.com" target="_blank" style="text-decoration: none; color: black;">
        The VGER Group
    </a>
    </div>
</div>
"""