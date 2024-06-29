from selenium import webdriver
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import requests
from requests.exceptions import ReadTimeout
import time

"""

Google image scraper 

"""



def checkForDirectory(dictionary):
    print(">>> Preparing directory for download.")
    folder_name = "images"        
    if os.path.exists(folder_name):
        print(f"{folder_name}/ already exists.")
    else:
        os.makedirs(folder_name, exist_ok=True)
        print(f"Made folder named {folder_name}/")

    for item in dictionary:
        if os.path.exists(f"{folder_name}/{item}"):
            print(f"{folder_name}/{item}/ already exists.")
        else:
            os.makedirs(f"{folder_name}/{item}", exist_ok=True)
            print(f"Made folder named {folder_name}/{item}/")

def googlePopUps(driver):
    print(">>> Skipping google prompts..")
    pressed_continue = False
    try:
        # Wait for the "Before continue" button
        before_continue = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#yDmH0d > c-wiz > div > div > div > div.NIoIEf > div.G4njw > div.AIC7ge > div.CxJub > div.VtwTSb > form:nth-child(2) > div > div > button")))
        # Click the "Before continue" button if found
        before_continue.click()
        pressed_continue = True
    except TimeoutException:
        print("...")


    # Try to find and click the "I agree" button
    if pressed_continue == True:
        pass
    else:
        google_agree = driver.find_element(By.CSS_SELECTOR, "#L2AGLb > div")
        try:
            google_agree.click()
        except Exception as e:
            print("Error:", e)
    return True
    
def scrapeFromGoogleImages(searchtags, number):
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument("lang=en")

    driver = webdriver.Chrome(options=options)
    all_links = {}
    skip = False
    for item in searchtags:
        search_url = f"http://www.google.com/search?q={item}&tbm=isch"
        driver.get(search_url)

        if skip == False:
            skip = googlePopUps(driver=driver)
        else:
            pass
        
        dictionary = findElementCount(driver=driver, number=number)
        all_links[item] = dictionary
    driver.close()
    return all_links

def findElementCount(driver, number):
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
    time.sleep(0.5)
    try:
        # Collecting links
        links = collectLinks(driver=driver, thumbnails=thumbnails, number=number)
    except Exception as e:
        print(">>> Error occured when finding urls.", e)
    return links

def collectLinks(driver, thumbnails, number):
    print(">>> Collecting links.")
    links = []

    for t in range(number):
        try:
            thumbnails[t].click()
            time.sleep(0.6)
            found_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="Sva75c"]/div[2]/div[2]/div/div[2]/c-wiz/div/div[3]/div[1]/a/img')))
            if not found_element:
                pass

            url = found_element.get_attribute("src")

            if "encrypted" in url:
                print("Failed to gather url.")
            else:
                checkResponse(url=url, links=links)

        except WebDriverException as e:
            print(f"Element is not clickable.")

        except Exception as e:
            print(e)
    return links

def checkResponse(url, links):
    try:
        req = requests.get(url, timeout=0.4)
        if req.status_code in {200,202}:
            links.append(req.content)
        else:
            print(">>> Response code not 200 or 202, skipped a link.")
            pass

    except ReadTimeout as e:
        print(e)
    except requests.HTTPError as e:
        print(f">>> HTTP Error occured when downloading image. {e}")
    except Exception as e:
        print(f">>> An error occured. {e}")

def downloadImages(dictionary, searchtag):
    print(">>> Downloading images.")
    time.sleep(1)
    for tag in searchtag:
       for idx, binary in enumerate(dictionary[tag]):
            try:
                print(f">>> Downloading {tag}{idx+1}.jpg")
                os.makedirs(f"images/{tag}", exist_ok=True)
                with open(f"images/{tag}/{tag}{idx+1}.jpg", "wb") as f:
                    f.write(binary)
            except requests.HTTPError as e:
                print(f">>> HTTP Error occured when downloading image. {e}")
            except Exception as e:
                print(e)


def main():
    # Search tag
    searchtag = ["cat", "bunny"]
    # Number of images to search for
    num_images = 20

    
    dictionary = scrapeFromGoogleImages(searchtags=searchtag, number=num_images)
    checkForDirectory(dictionary=dictionary)
    downloadImages(dictionary=dictionary, searchtag=searchtag)

    print(">>> Finished downloading images.")

if __name__ == "__main__":
    main()



