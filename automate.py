from PIL import Image, ImageFilter
import cv2
import pytesseract
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from time import sleep
import time
import os
from webdriver_manager.chrome import ChromeDriverManager



def prepare_image(img):
    """Transform image to greyscale and blur it"""
    img = img.filter(ImageFilter.SMOOTH_MORE)
    img = img.filter(ImageFilter.SMOOTH_MORE)
    if 'L' != img.mode:
        img = img.convert('L')
    return img

def remove_noise_by_pixel(img, column, line, pass_factor):
    if img.getpixel((column, line)) < pass_factor:
        return (0)
    return (255)

def remove_noise(img, pass_factor):
    for column in range(img.size[0]):
        for line in range(img.size[1]):
            value = remove_noise_by_pixel(img, column, line, pass_factor)
            img.putpixel((column, line), value)
    return img

def prepare_and_clean(image):
    img = Image.open(image)
    pass_factor = 90 
    img = prepare_image(img)
    img = remove_noise(img, pass_factor)
    img.save('out_\download.png')
    im_in = cv2.imread("out_\download.png", cv2.IMREAD_GRAYSCALE)
    (th, im_th) = cv2.threshold(im_in, 220, 255, cv2.THRESH_BINARY_INV)
    im_floodfill = im_th.copy()
    scale_percent = 50 # percent of original size
    width = int(im_floodfill.shape[1] * scale_percent / 100)
    height = int(im_floodfill.shape[0] * scale_percent / 100)
    dim = (width, height)
    resized = cv2.resize(im_floodfill, dim, interpolation = cv2.INTER_AREA)
    cv2.imwrite('out_\image.png',resized)

def resolve(path):
    # it should change this path to your tesseract path
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    return pytesseract.image_to_string(Image.open(path))

# Just codes of colors
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Bot():
    
    def __init__(self) -> None:
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)
        self.driver.implicitly_wait(0.5)
        self.driver.get('https://syria-visa.sy/passport/')
    
    data_path = {'id':'//*[@id="nat_num"]',
                'first_name':'//*[@id="first_name"]',
                'last_name': '//*[@id="last_name"]',
                'father_name': '//*[@id="father_name"]',
                'mother_name': '//*[@id="mother_name"]',
                'phone':'//*[@id="mobile_num"]',
                'area':'//*[@id="center"]' ,
                'captcha':'//*[@id="captcha"]',
                'submit_button':'//*[@id="register"]',
                'img_url':'//*[@id="reg"]/div/div[7]/span/img',
                'accompanying_persons':'//*[@id="cop_num"]',
                'internal': '//*[@id="personal"]',
                'extrenal': '//*[@id="external"]',
                
    }
    
        
    def download_img(self):
        with open('download.png', 'wb') as file:
            #identify image to be captured
            img = self.driver.find_element(by=By.XPATH, value=self.data_path['img_url'])
            #write file
            file.write(img.screenshot_as_png)

    def fill_form_with_data(self):
        area_msg = """
- Please notice that area_code for your state :
    - Damascus :              0   ---  Tartus      : 6 
    - Damascus Countryside:   1   ---  As-Suwayda  : 7 
    - Aleppo  :               2   ---  Daraa       : 8 
    - Homs    :               3   ---  Al-Hasakah  : 9 
    - Hama    :               4   ---  Quneitra    : 10 
    - Latakia :               5   ---  Deir ez-Zo  : 11
    - An-Nabk :               12  ---  Palestine   : 13
please enter your area code :
                    """
        id_num = input('plaese enter your id number : ').strip()
        first_name = input('plaese enter your first_name : ').strip()
        last_name = input('plaese enter your last_name : ').strip()
        father_name = input('plaese enter your father_name : ').strip()
        mother_name = input('plaese enter your mother_name : ').strip()
        phone_number = input('plaese enter your phone_number : ').strip()
        area_code = int(input(area_msg).strip())
        accompanying_persons = int(input('For people come with you enter num from 0 to 3 : ').strip())
        place = int(input('For the place of owner passport write 0 if owner inside syria and 1 if out : ').strip())
        if place == 0:
            self.driver.find_element(by=By.XPATH, value=self.data_path['internal']).click() 
        else :
            self.driver.find_element(by=By.XPATH, value=self.data_path['extrenal']).click() 
            sleep(3)
            self.driver.find_element(by=By.XPATH, value='/html/body/div[2]/div/div[6]/button[1]').click() 
            id_external = input('plaese enter id for passport owner :').strip()
            self.driver.find_element(by=By.XPATH, value='//*[@id="nat_num_ext"]').send_keys(id_external)
        self.driver.find_element(by=By.XPATH, value=self.data_path['id']).send_keys(id_num)
        self.driver.find_element(by=By.XPATH, value=self.data_path['first_name']).send_keys(first_name)
        self.driver.find_element(by=By.XPATH, value=self.data_path['last_name']).send_keys(last_name)
        self.driver.find_element(by=By.XPATH, value=self.data_path['father_name']).send_keys(father_name)
        self.driver.find_element(by=By.XPATH, value=self.data_path['mother_name']).send_keys(mother_name)
        self.driver.find_element(by=By.XPATH, value=self.data_path['phone']).send_keys(phone_number)
        self.select_fr = Select(self.driver.find_element(by=By.XPATH, value=self.data_path['area']))
        self.select_fr.select_by_index(area_code)
        self.select_fr = Select(self.driver.find_element(by=By.XPATH, value=self.data_path['accompanying_persons']))
        self.select_fr.select_by_index(accompanying_persons)
        

    def get_status(self):
        status = ''
        while status == '':
                try:
                    status = self.driver.find_element(by=By.XPATH, value='//*[@id="swal2-title"]').text.strip()
                except NoSuchElementException as e:
                    print('Retry in 1 second')
                    time.sleep(1.5)
        if  status == 'تحذير': 
            self.driver.find_element(by=By.XPATH, value='/html/body/div[2]/div/div[6]/button[1]').click() 
            print(f"{bcolors.WARNING}Warning the resolved captcha wrong!! : {bcolors.ENDC}",f" {bcolors.WARNING}--------- {status}{bcolors.ENDC}")
        elif status == 'عذرا':
            print(f"{bcolors.OKBLUE}Try book an appointment  : {bcolors.ENDC}",f" {bcolors.OKBLUE}--------- {status}{bcolors.ENDC}")
            self.driver.find_element(by=By.XPATH, value='/html/body/div[2]/div/div[6]/button[1]').click() 
        else:
            self.driver.find_element(by=By.XPATH, value='/html/body/div[2]/div/div[6]/button[1]').click() 
            print('The Time When Register Done is : ',time.localtime())
            print(f"{bcolors.OKGREEN}it's almost Done check this site https://www.syria-visa.sy/passport/check-app.php : {bcolors.ENDC}",f" {bcolors.OKGREEN}--------- {status}{bcolors.ENDC}")
            
        return status
    
        
        
    def run(self):
        self.fill_form_with_data()
        while True:
            start = time.time()
            self.download_img()
            prepare_and_clean('download.png')
            captcha_text = resolve('out_\image.png')
            self.driver.find_element(by=By.XPATH, value=self.data_path['captcha']).send_keys(captcha_text.strip())
            os.remove('download.png')
            os.remove('out_\download.png')
            os.remove('out_\image.png')
            self.driver.find_element(by=By.XPATH, value=self.data_path['submit_button']).click() 
            sleep(4)
            status = self.get_status()
            if status not in ['عذرا', 'تحذير']:
                break
            end = time.time()
            print('excution time is : ', (end - start))
            self.driver.refresh()
            start = 0
            end = 0



if __name__=="__main__":
    bot = Bot()
    bot.run()