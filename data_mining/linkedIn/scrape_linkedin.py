from selenium import webdriver
import time
import pandas as pd
import numpy as np
import platform
from tqdm import tqdm
import json
import uuid
from collections import defaultdict


op_sys = platform.platform()
executable = "./chromedriver.exe" if "windows" in op_sys else "chromedriver"


def run():
    country = "Russia"
    
    with open("keywords.json") as f:
        keywords = json.load(f)

    with open("config.json") as f:
        config = json.load(f)

    global data
    data = defaultdict(list)

    for keyword in tqdm(keywords):
        wd = webdriver.Chrome(executable_path=executable)
        jobs = get_jobs(wd, keyword, country)
        parse_listings(jobs, config["listings"])
        parse_details(wd, len(jobs), config["details"])

    df = pd.DataFrame(data)
    df.drop_duplicates(subset=["url"], inplace=True)
    df.to_csv(f"linkedin_jobs_{country}.csv")

def get_jobs(wd, search_word, country):
    url = f"https://www.linkedin.com/jobs/search?keywords={'%20'.join(search_word.split(' '))}&location={country}&geoId=101728296&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0"
    wd.get(url)
    wd.maximize_window()
    no_of_jobs = int(wd.find_element_by_css_selector("h1>span").get_attribute("innerText").strip("+").replace(",", ""))

    i = 2
    while i <= int(no_of_jobs / 25) + 1:
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        i = i + 1
        try:
            wd.find_element_by_xpath(
                "/html/body/div/div/main/section[2]/button"
            ).click()
            time.sleep(5)
        except:
            pass
            time.sleep(5)

    job_lists = wd.find_element_by_class_name("jobs-search__results-list")
    jobs = job_lists.find_elements_by_tag_name("li")

    return jobs


def parse_listings(jobs, col_to_loc):

    for job in tqdm(jobs):
        job_id = str(uuid.uuid4())
        data["id"].append(job_id)

        for col, loc in col_to_loc.items():
            element = job.find_element_by_css_selector(
                loc["css_selector"]
            ).get_attribute(loc["attribute"])
            data[col].append(element)


def parse_details(wd, n_jobs, col_to_path):
    for item in tqdm(range(n_jobs)):
        job_click_path = f"/html/body/div[3]/div/main/section[2]/ul/li[{item+1}]/div/a"
        try:
            _ = wd.find_element_by_xpath(job_click_path).click()
            time.sleep(2)
        except:
            print("unable to click")
            time.sleep(2)

        for col, path in col_to_path.items():
            try:
                element = wd.find_element_by_xpath(path).get_attribute("innerText")
            except:
                element = None
            data[col].append(element)


if __name__ == "__main__":
    run()
