import math

from time import time
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from database import answer_database, time_database


# Network Latency
LATENCY = 3

# Get driver
def init_driver(mode):
    if mode == "linux":
        driver = webdriver.Chrome("./driver/chromedriver_linux")
    elif mode == "windows":
        driver = webdriver.Chrome("./driver/chromedriver_win.exe")
    elif mode == "mac":
        driver = webdriver.Chrome("./driver/chromedriver_mac")

    print("[+] Loaded Chrome webdriver")
    return driver

def enter_education(driver, ID, PW):
    # Log in portal
    print("[*] Logging in portal... ", end='')
    driver.get("https://portal.korea.ac.kr")
    sleep(LATENCY * 2)
    driver.find_element_by_name("id").send_keys(ID)
    driver.find_element_by_name("pw").send_keys(PW)
    driver.find_element_by_xpath("//*[@id=\"loginsubmit\"]").click()
    print("Done.")
    

    # Enter education
    print("[*] Accessing education page... ", end='') 
    sleep(LATENCY)
    driver.execute_script("moveComponent('http://infodepot.korea.ac.kr', '3', '/common/FMSLogin3.jsp?url=archibus', '86', '4960', 'S')")

    # Remove popup
    sleep(LATENCY)
    driver.switch_to.window(driver.window_handles[-1])
    driver.close()
    driver.switch_to.window(driver.window_handles[-1])

    # Switch to new tab
    sleep(LATENCY*2)
    driver.switch_to.window(driver.window_handles[-1])

    # Select Identification
    sleep(LATENCY*2)
    driver.execute_script("sel_fnc()")

    # Finally enter education page
    sleep(LATENCY)
    driver.get("http://cafm.korea.ac.kr/archibus/safety_edu/selec_req_list.jsp")
    print("Done.")



# Enrolling logic for each class
def enroll(driver, idx):
    '''
    [Requirement]
    driver should be in education page!
    '''
    print(f"[+] Enrolling class #{idx}... ", end='')
    driver.execute_script(f"se_event('{idx}')")
    sleep(LATENCY)
    driver.switch_to.alert.accept()
    print("Done.")

#Automatic Enrolling
def auto_enroll(driver, idxs):
    print(f"[*] Automatically enrolling class #{idxs}...")
    for idx in idxs:
        enroll(driver, idx)
    print("[+] Enrolled.")

def build_ajax_payload(idx, totalTime):
    return '''$.ajax({
			url: "sub_entry.jsp",
			data: {"c_type":"save" ,''' + \
            f'''"chap_type": "{str(idx).zfill(2)}" ,"tstart": {math.ceil(time())}, "tend": {math.ceil(time())+totalTime}, "ct": {totalTime}''' + \
            '''
            },
			type:'post',
			dataType:'json',
			success:function(data){}
            });
            '''

# Doing ajax is enough.
def take_class(driver, idx):
    print(f"[+] Defeating class #{idx}... ")
    driver.get(f"http://cafm.korea.ac.kr/archibus/safety_edu/2020/{str(idx).zfill(2)}/index.jsp")
    sleep(LATENCY)
    for number in range(len(time_database[idx])):
        payload = build_ajax_payload(number+1, time_database[idx][number])
        driver.execute_script(payload)
        sleep(LATENCY * 0.3)
        print(f"[+] Defeated Subclass #{number+1}")
    print(f"[+] Done.")


def auto_take_class(driver, idxs):
    print(f"[*] Automatically taking classes of class #{idxs}...")
    for idx in idxs:
        take_class(driver, idx)
    print("[+] All taken.")



def solve_test(driver, idx):
    sleep(LATENCY)
    # Enter test
    print(f"[+] Automatically solving test of class #{idx}...", end='')
    driver.execute_script(f"test_event('{idx}', 'kor')")
    driver.switch_to.alert.accept()
    sleep(LATENCY*2)

    # Switch tab
    driver.switch_to.window(driver.window_handles[-1])

    # import database
    answer = answer_database[idx]
    
    # Solve question with answer
    for num in range(len(answer)):
        if answer[num] == -1:
            continue
        driver.find_element_by_id(f"ans_{num+1}_{answer[num]}").click()
    
    # Submit    
    driver.execute_script("submitPage()")
    sleep(LATENCY)
    driver.switch_to.alert.accept()
    driver.switch_to.window(driver.window_handles[1])
    print("Done.")


def auto_solve_test(driver, idxs):
    print(f"[*] Automatically taking test(s) of class #{idxs}...")
    driver.get(r"http://cafm.korea.ac.kr/archibus/safety_edu/selec_my_req_list.jsp")
    for idx in idxs:
        solve_test(driver, idx)
    print("[+] All Solved.")


def get_cert(driver):
    # Accessing index page
    print("[*] Accessing certification issuing page... ", end='')
    driver.get("http://cafm.korea.ac.kr/archibus/se_connect_chk.jsp?se_chk=se")
    sleep(LATENCY)
    driver.execute_script("sel_fnc()")
    sleep(LATENCY)
    driver.switch_to.frame("frame1")

    # Find button and click
    driver.find_element_by_xpath("//*[@id=\"data_table_header\"]/tbody/tr[2]/td[9]/input").click()
    sleep(LATENCY*0.3)
    driver.switch_to.window(driver.window_handles[-1])

    # Get cert
    driver.find_element_by_xpath("//*[@id=\"nav\"]/input[1]").click()
    print("Done.")
