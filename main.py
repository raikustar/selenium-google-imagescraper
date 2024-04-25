from selenium import webdriver
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from urllib.request import urlretrieve
import requests
from requests.exceptions import ReadTimeout
import time

"""

Google image scraper 

"""

def checkForDirectory(dictionary):
    folder_name = "images"        
    if os.path.exists(folder_name):
        print(f"{folder_name}/folder already exists.")
    else:
        os.makedirs(folder_name, exist_ok=True)
        print(f"Made folder named {folder_name}/")

    for item in dictionary:
        if os.path.exists(f"{folder_name}/{item}"):
            print(f"{folder_name}/{item}/folder already exists.")
        else:
            os.makedirs(f"{folder_name}/{item}", exist_ok=True)
            print(f"Made folder named {folder_name}/{item}/")

def downloadImages(dictionary, searchtags):
    time.sleep(1)
    n = 1
    for tag in searchtags:
        if tag in dictionary:
            for idx, link in enumerate(dictionary[tag]):
                try:
                    req = requests.get(link, timeout=0.4)
                    if req.status_code == 200:
                        n =+idx
                        print(f">>>     Downloading image of {tag}: {n}.", end="\r")  
                        urlretrieve(link, f"images/{tag}/{tag}_{n}.jpg")     
                    else:
                        print(f">>> Skipping image of {tag}: {idx+1}. Response code not 200.")
                except ReadTimeout:
                    print(">>> Request timeout, moving to next item.      ", end='\n')
                except requests.HTTPError as e:
                    print(f">>> HTTP Error occured when downloading image of {tag}: {idx+1} of {len(dictionary[tag])}. {e}")
                except Exception as e:
                    print(f">>> An error occured. {e}")

            print(f">>> Downloaded {n} images of {tag}.")
        else:
            print(">>> No links were found.")

def googlePopUps(driver):
    pressed_continue = False
    try:
        # Wait for the "Before continue" button
        before_continue = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#yDmH0d > c-wiz > div > div > div > div.NIoIEf > div.G4njw > div.AIC7ge > div.CxJub > div.VtwTSb > form:nth-child(2) > div > div > button")))
        # Click the "Before continue" button if found
        before_continue.click()
        pressed_continue = True
        print("Clicked 'Before continue'")
    except TimeoutException:
        print("Did not find 'Before continue'")


    # Try to find and click the "I agree" button
    if pressed_continue == True:
        print("Continue button has been pressed before....")
        pass
    else:
        google_agree = driver.find_element(By.CSS_SELECTOR, "#L2AGLb > div")
        try:
            google_agree.click()
            print("Clicked 'I agree'")
        except Exception as e:
            print("Error:", e)
            print("Did not find 'I agree' or encountered an error while clicking")  
    
    return True
    
def scrapeFromGoogleImages(searchtags, number):
    driver = webdriver.Chrome()
    all_links = {}
    skip = False
    for item in searchtags:
        search_url = f"http://www.google.com/search?q={item}&tbm=isch"
        driver.get(search_url)

        if skip == False:
            skip = googlePopUps(driver=driver)
        else:
            pass

        dictionary = getLinks(driver=driver, number=number)
        all_links[item] = dictionary
    driver.close()
    return all_links

def getLinks(driver, number):
    links = []   
    original_height = driver.execute_script("return document.body.scrollHeight")
    reload_elements = WebDriverWait(driver=driver, timeout=10).until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class="F0uyec"]')))
    try:
        while len(reload_elements) <= int(number):    
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1)
            reload_elements = WebDriverWait(driver=driver, timeout=10).until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class="F0uyec"]')))
            new_height = driver.execute_script("return document.body.scrollHeight")
            if len(reload_elements) == int(number):
                print(f"Found the correct amount of images that were searched for.")
                break
            elif original_height == new_height:
                print(f"At the bottom of the page, found only {len(reload_elements)} elements.")
                number = len(reload_elements)
                break
            elif len(reload_elements) >= int(number):
                print(f"Found {number} elements.")
                break           
            original_height = new_height
    except TimeoutException as e:
        print(e)

    thumbnails = driver.find_elements(By.XPATH, '//div[@class="F0uyec"]')
    try:
        links = getUrlFromGoogle(driver=driver, thumbnails=thumbnails, number=number)
    except Exception as e:
        print(">>> Error occured when finding urls.", e)
    return links

def getUrlFromGoogle(driver, thumbnails, number):
    links = []
    for t in range(number):
        thumbnails[t].click()
        time.sleep(0.1)
        load_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#Sva75c > div.A8mJGd.NDuZHe.OGftbe-N7Eqid-H9tDt > div.LrPjRb > div.AQyBn > div.tvh9oe.BIB1wf > c-wiz > div > div > div > div > div.v6bUne > div.p7sI2.PUxBg > a > img.sFlh5c.pT0Scc")))
        enc_url = str(load_element.get_attribute("src"))
        if load_element and not "encrypted" in enc_url:
            found_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#Sva75c > div.A8mJGd.NDuZHe.OGftbe-N7Eqid-H9tDt > div.LrPjRb > div.AQyBn > div.tvh9oe.BIB1wf > c-wiz > div > div > div > div > div.v6bUne > div.p7sI2.PUxBg > a > img.sFlh5c.pT0Scc.iPVvYb")))
            url = found_element.get_attribute("src")
            if url is not None:
                links.append(url)
            else:
                print("Didn't get url.")
                pass
    
        elif load_element and "encrypted" in enc_url:
            pass
    return links


def main():
    # Search tag
    searchtag = ["cat"]
    # Number of images to search for
    num_images = 50


    print(">>> Gathering urls.")
    dictionary = scrapeFromGoogleImages(searchtags=searchtag, number=num_images)

    print(">>> Checking directory path.")
    checkForDirectory(dictionary=dictionary)

    print(">>> Downloading images.")
    downloadImages(dictionary=dictionary, searchtags=searchtag)

    print("    ")
    print(">>> Finished downloading. \n")

if __name__ == "__main__":
    main()


# element not interactable

# ERROR: #google_continue = driver.find_element(By.XPATH, "//div[text()='Accept all']")

# Region change for chromedriver????

# Errors:
    # ERROR:cert_issuer_source_aia.cc(35)] Error parsing cert retrieved from AIA (as DER):
    # ERROR: Couldn't read tbsCertificate as SEQUENCE
    # ERROR: Failed parsing Certificate

