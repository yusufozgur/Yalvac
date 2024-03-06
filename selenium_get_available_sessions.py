
from seleniumwire import webdriver
from selenium_stealth import stealth
from urllib.parse import unquote
import logging
import re
import json
from datetime import datetime
import secure_info
from secure_info import Facilities



def extract_available_sessions(username,
                           password,
                           facility,
                           headless = True):
    
    #set logging levels, seleniumwire is noisy in terms of INFO logging
    selenium_logger = logging.getLogger('seleniumwire')
    selenium_logger.setLevel(logging.ERROR)
    
    options = webdriver.ChromeOptions()
    #options.add_argument("start-maximized")

    if headless:
        options.add_argument("--headless")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(options=options)#, executable_path=r"chromedriver.exe"

    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )

    try:
        
        
        secure_info.selenium_secure_part(username,
                                         password,
                                         driver,
                                         facility)



        myschedule_requests = []

        for request in driver.requests:
            if request.method=="POST" and "rez.metu.edu.tr" in request.url and "javax.faces.partial.render=form:myschedule" in unquote(request.body.decode("utf-8")):
                    myschedule_requests.append(request)

        schedule = myschedule_requests[-1].response.body.decode("utf-8")

        driver.quit()

        #find event json object that keeps schedule
        regex_find_event = re.search(r'events":(.*)\}\]\]></update><upda',schedule).group(1)

        events = json.loads(regex_find_event)

        #keep only important keys
        events = [{key: value for key, value in event.items() if key in ['start','end','title']} for event in events]

        #parse "title": "Boş : 52" into "spaces": 52
        for event in events:
            event["spaces"] = re.search('(\\d+)',event.pop('title')).group(1)
        
        #convert this to a single dict where keys = starttime and value = empty_space
        events_just_start_time_and_space = {}
        for event in events:
            events_just_start_time_and_space[event["start"]] = event["spaces"]
        
        #convert events to datetime objects
        #currently: 2024-03-10T10:30:00+0300
        #to: datetime
        events_daytime_objects = {}
        for time,spaces in events_just_start_time_and_space.items():
            re_time = re.findall("(\\d+)",time)
            datetime_obj  = datetime(
                 year = int(re_time[0]),
                 month= int(re_time[1]),
                 day =  int(re_time[2]),
                 hour =  int(re_time[3]),
                 minute =  int(re_time[4]),
                 second=  int(re_time[5]))
            events_daytime_objects[datetime_obj] = spaces
        
        return events_daytime_objects
    except Exception as e:
        driver.quit()
        print(e)
        return None
    
if __name__ == "__main__":
    pass
    print(extract_available_sessions(secure_info.username,secure_info.password,Facilities.swimming,
                                 headless=False))