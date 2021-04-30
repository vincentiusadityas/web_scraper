import re
import os
import csv
from scraper import Scraper

IMAGE_SIZE = {"100-square": "100-square", "500-square": "500-square", "900":"900"}

class TokopediaProductData:
    def __init__(self, weight=None, productId=None, productName=None, productDescription=None, productUrl=None, images_url=[]):
        self.id = productId
        self.name = productName
        self.description = productDescription
        self.weight = weight
        self.url = productUrl
        self.images_url = images_url
        self.imageSize = IMAGE_SIZE["900"]

    def convertImageSize(self):
        regex = '(?<=cache/)(.*?)(?=/)'
        new_img_urls = []
        for img in self.images_url:
            try:
                size = re.search(regex, img).group(1)
                if (size != self.imageSize):
                    img = img.replace(size, self.imageSize)
                    # print(img)
                new_img_urls.append(img)
            except AttributeError:
                size = ''
        self.images_url = new_img_urls

    def display(self):
        print(f"Product name: {self.name}")

    def toList(self):
        data = [
            self.name,
            self.description,
            self.url,
            self.images_url
        ]
        return data

    def toDict(self):
        data_dict = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'weight': self.weight,
            'url': self.url,
        }
        return data_dict


class TokopediaScraper(Scraper):
    def __init__(self, url, debug=False):
        super(TokopediaScraper, self).__init__()
        self.baseURL = 'https://www.tokopedia.com'
        self.url = url
        self.debug = debug
        self.url_products = []
        self.baseFolderPath = None
        self.productData_details = []

    def getDataByProp(self, page, tag, prop, name, as_text=True, strip=True):
        """Get Data by Prop Name
        """
        data = page.find(tag, {prop: name})
        resp = None
        if data:
            if as_text and strip:
                resp = data.text.strip()
            elif as_text and not strip:
                page = "".join([str(item).strip() for item in data.contents])
                resp = page.replace('<br/>', '. ')
            else:
                resp = data
        return resp

    def getMultipleDataByProp(self, page, tag, prop, name):
        results = page.findAll(tag, {prop: name})
        # print(results[0].get('src'))
        images_url = []
        for result in results:
            images_url.append(result.get('src'))

        return images_url

    def getProductWeight(self, page, tag, prop, name):
        regex = '(?<=Berat: )(.*?)(?= Gram)'
        text = self.getDataByProp(page, tag, prop, name)
        weight = re.search(regex, text).group(1)
        weight = weight.replace('.', ",")
        
        return (weight if weight else None)

    def extractProductDetails(self, url, saveImgToFolder=False):
        soup = self.getPage(url)
        product = TokopediaProductData(productUrl=url)
        product.id = url.split('/')[-1]
        product.name = self.getDataByProp(soup, 'h1', 'data-testid', 'lblPDPDetailProductName')
        product.description = self.getDataByProp(soup, 'div', 'data-testid', 'lblPDPDescriptionProduk', strip=False)
        product.weight = self.getProductWeight(soup, 'ul', 'data-testid', 'lblPDPInfoProduk')
        product.images_url = self.getMultipleDataByProp(soup, 'img', 'alt','Thumbnail')
        product.convertImageSize()

        print("Product name:", product.name)
        print("Product desc:", product.description)
        print("Product weight:", product.weight)
        if (saveImgToFolder):
            print()
            print("Saving images...")
            product_folder_path = self.createProductFolder(product.id)
            img_counter = 0
            for img_url in product.images_url:
                img_name = str(img_counter) + "_" + product.id + ".jpg"
                print(img_name)
                self.saveImgToFolder(img_url, img_name, product_folder_path)
                img_counter += 1

        return product

    def getURLs(self, page, className, keyword=""):
        divs = page.findAll("div", class_=className)

        # print(divs)
        counter = 0
        for div in divs:
            href = div.find('a')['href']
            if keyword in href:
                self.url_products.append(href)
                counter += 1
        
        print("Found {0} urls".format(counter))
        print()

    def getAllProductURLs(self, keyword=""):
        print("Page:", self.url)
        waitClassName = "css-7fmtuv"
        page = self.getPageSelenium(self.url, wait=True, waitClassName=waitClassName)
        self.getURLs(page, waitClassName, keyword)

        next_page = page.findAll("a", {"data-testid" : "btnShopProductPageNext"})
        while next_page:
            nextUrl = self.baseURL + next_page[0].attrs['href']
            print("Page:", nextUrl)

            page = self.getPageSelenium(nextUrl, wait=True, waitClassName=waitClassName)
            self.getURLs(page, waitClassName, keyword)

            next_page = page.findAll("a", {"data-testid" : "btnShopProductPageNext"})

    def createProductFolder(self, product_name):
        product_folder_path = os.path.join(self.baseFolderPath, product_name)
        if os.path.exists(product_folder_path):
            print("Folder for product '{0}' already exists".format(product_name))
        else:
            os.mkdir(product_folder_path)
        
        return product_folder_path

    def createFolder(self):
        regex = '(?<=com/)(.*?)(?=/product)'

        curent_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir_name = "Tokopedia"
        parent_dir_path = os.path.join(curent_dir, parent_dir_name)

        if os.path.exists(parent_dir_path):
            print("Parent folder already exists")
        else:
            os.mkdir(parent_dir_path)
            print("Parent folder created")

        shopName = re.search(regex, self.url).group(1)
        path = os.path.join(parent_dir_path, shopName)
        self.baseFolderPath = path
        if os.path.exists(path):
            print("Folder for shop {0} already exists".format(shopName))
        else:
            os.mkdir(path)
            print("Folder for shop {0} created".format(shopName))
        print()
    
    def createSaveFile(self):
        saveFilePath = self.baseFolderPath + "\products_data.csv"
            
        if os.path.exists(saveFilePath):
            file = open(saveFilePath, 'a', encoding='utf-8')
            writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
            print("Save file already exists. Data will be appended...")
        else:
            file = open(saveFilePath, 'a', encoding='utf-8')
            writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
            writer.writerow(['id', 'product_id', 'name', 'weight (gram)', 'description', 'url']) 
            print("Save file created...")
        print()
        return (file, writer)

    def appendDataToSaveFile(self, writer, counter, data):
        # writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        writer.writerow([counter, data.id, data.name, data.weight, data.description, data.url]) 

    def startScraping(self, saveData=False, saveImage=False, start_idx=0, num_of_products=None):

        print("Fetching all product URLs...")
        print()
        self.getAllProductURLs(keyword='puku')
        total_products = len(self.url_products)
        print("Total url found:", total_products)
        print()

        file = None
        writer = None
        if saveData:
            print("Data will be saved to products_data.csv in " + self.baseFolderPath)
            file, writer = self.createSaveFile()
            print(file)

        products = []
        counter = start_idx+1
        last_idx = (start_idx+num_of_products) if num_of_products else total_products
        
        if (self.url_products):
            total_products_fetched = (num_of_products if num_of_products else total_products)
            print("Fetching {0} product details...".format(total_products_fetched))
            print()

            for url in self.url_products[start_idx:last_idx]:
                self.restartDriver()
                print("Product {0}: {1}".format(counter, url))
                product = self.extractProductDetails(url, saveImgToFolder=saveImage)
                print()
                if saveData: self.appendDataToSaveFile(writer, counter, product)
                products.append(product)
                counter+=1

            if saveData: file.close()

        print("Finished scraping..")
        print("Total products scrapped:", len(products))
        # print()
        # print("Example product:")
        # print(products[0].name)
        # print(products[0].images_url)

        # urls = ["https://www.tokopedia.com/enportumomnbaby/puku-baby-stroller-tipe-40116-kereta-bayi-stroller-lipat",
        # "https://www.tokopedia.com/enportumomnbaby/puku-botol-susu-p11528-biru-3pcs-240-cc"]
        # products = []
        # for url in urls:
        #     product = self.extractProductDetails(url)
        #     product = product.toDict()
        #     products.append(product)
        # print(products)
        # self.productData_details = products
        # print("Name:", product.name)
        # print("Desc:", product.description)
        # print("Weight:", product.weight)
        # print("Image URLs:", product.images_url)

    def saveData(self, path=None):
        thePath = (path if path else self.baseFolderPath) + "\products_data.csv"
        with open(thePath, 'a') as file:
            writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
            writer.writerow(['id', 'product_id', 'name', 'weight (gram)', 'description', 'url'])
            index = 0
            for data in self.productData_details:
                index += 1
                writer.writerow([index, data['id'], data['name'], data['weight'], data['description'], data['url']])

            print(f"Data saved to `{path}`")

    def run(self):
        ask_string = ("You are about to run tokopedia scraper.\n"
            "This script will automatically create folders and save files into the folder.\n"
            "Do you want to continue? (Y/N) ")
        inp = input(ask_string)
        print()

        if inp.lower() == 'y':
            self.createFolder()

            ask_string = ("Do you want to save the images? (Y/N) ")
            inp = input(ask_string)
            print()
            saveImage = inp == 'y'

            ask_string = ("Do you want to save the data? (as csv) (Y/N) ")
            inp = input(ask_string)
            print()
            saveData = inp == 'y'

            self.startScraping(saveData=saveData, saveImage=saveImage, start_idx=186, num_of_products=None)
            # self.saveData(self.baseFolderPath)

        elif inp.lower() == 'n':
            print("Thank you. See you later.")

        
