from tokopedia_scraper import TokopediaScraper
from pathlib import Path
import os
import requests

def main():
    URL = 'https://www.tokopedia.com/enportumomnbaby/product'
    
    ts = TokopediaScraper(url=URL, debug=True)
    ts.run()

if __name__ == "__main__":
    main()

    # curent_dir = os.path.dirname(os.path.abspath(__file__))
    # parent_dir_name = "Tokopedia"
    # parent_dir_path = os.path.join(curent_dir, parent_dir_name)

    # if os.path.exists(parent_dir_path):
    #     print("Parent folder already exists")
    # else:
    #     os.mkdir(parent_dir_path)
    #     print("Parent folder created")

    # directory = "toko 1"
    # path = os.path.join(parent_dir_path, directory)
    # if os.path.exists(path):
    #     print("{0} already exists".format(directory))
    # else:
    #     os.mkdir(path)
    #     print("Folder for {0} created".format(directory))

    # img_url = "https://images.tokopedia.net/img/cache/900/VqbcmM/2020/10/16/04d6a37e-7c29-41e2-bc2b-84dc0e0cd4f3.jpg"

    # img_req = requests.get(img_url)
    # img_name = 'foto1.jpg'

    # img_path = os.path.join(path, img_name)
    # if img_req.status_code == 200:
    #     with open(img_path, 'wb') as f:
    #         f.write(img_req.content)