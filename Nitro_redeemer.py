# Imports
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from colorama import Fore
from timeit import default_timer as timer
from pystyle import Center, Colorate, Colors
from datetime import timedelta
import sys
import time
import os
import random
import threading
import json

thread_lock = threading.Lock()
activated_accounts = 0


class Console:
    """Console utils"""

    @staticmethod
    def _time():
        return time.strftime("%H:%M:%S", time.gmtime())

    @staticmethod
    def clear():
        os.system("cls" if os.name == "nt" else "clear")

    # Safe print, to stop overlapping when printing in thread tasks
    @staticmethod
    def sprint(content: str, status: bool = True) -> None:
        thread_lock.acquire()
        sys.stdout.write(
            f"{Fore.RESET}[{Fore.LIGHTBLUE_EX}{Console()._time()}{Fore.RESET}] {Fore.GREEN if status else Fore.RED}{content}"
            + "\n"
            + Fore.RESET
        )
        thread_lock.release()

    @staticmethod
    def update_title() -> None:
        start = timer()

        while True:
            thread_lock.acquire()
            end = timer()
            elapsed_time = timedelta(seconds=end - start)
            os.system(
                f"title Opti Services │ Activated Accounts: {activated_accounts} │ Elapsed: {elapsed_time}"
            )
            thread_lock.release()


# Main
class Nitro:
    def __init__(self, token: str, cc: str, link: str, proxy: str = None) -> None:
        if ":" in token:
            self.token = token.split(":")[2]
            self.full_token = token
        else:
            self.token = token

        self.card_number, self.expiry, self.ccv = str(cc).split(":")
        self.nitro_link = link
        self.useragent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
        self.proxy = proxy

    def __init_driver__(self) -> None:
        ser = Service(f"chromedriver.exe")

        if not self.proxy:
            capabilities = None
        else:
            proxy = Proxy()
            proxy.proxy_type = ProxyType.MANUAL
            proxy.http_proxy = self.proxy
            proxy.ssl_proxy = self.proxy
            capabilities = webdriver.DesiredCapabilities.CHROME
            proxy.add_to_capabilities(capabilities)

        # Spoofing to not get detected
        options = Options()

        options.add_experimental_option(
            "excludeSwitches",
            [
                "enable-logging",
                "enable-automation",
                "ignore-certificate-errors",
                "safebrowsing-disable-download-protection",
                "safebrowsing-disable-auto-update",
                "disable-client-side-phishing-detection",
            ],
        )

        options.binary_location = (
            "C:\Program Files\Google\Chrome Beta\Application\chrome.exe"
        )
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("--lang=en")
        options.add_argument("--log-level=3")
        options.add_argument("--incognito")
        options.add_argument("--no-sandbox")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--ignore-ssl-errors")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--profile-directory=Null")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--start-maximized")
        options.add_argument(f"--user-agent={self.useragent}")
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")

        self.driver = webdriver.Chrome(
            service=ser, desired_capabilities=capabilities, options=options
        )

        self.driver.execute_cdp_cmd(
            "Network.setUserAgentOverride", {"userAgent": self.useragent}
        )

        self.driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
            Object.defineProperty(navigator, 'deviceMemory', {
            get: () => 99
            })
        """
            },
        )

        self.driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
                })
            """
            },
        )

    def activate_nitro(self):
        global activated_accounts

        self.driver.get(self.nitro_link)

        WebDriverWait(self.driver, 40).until(
            EC.presence_of_element_located((By.XPATH, "//input[@name='email']"))
        )

        # Login
        for _ in range(3):
            self.driver.execute_script(
                '''
            function login(token) {
            setInterval(() => {
            document.body.appendChild(document.createElement `iframe`).contentWindow.localStorage.token = `"${token}"`
            }, 50);
            setTimeout(() => {
            location.reload();
            }, 1500);
            }
            login("'''
                + self.token
                + """")
            """
            )

            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//div[contains(text(),'Next')]")
                    )
                )
                break
            except:
                continue

        # Checks to see if code is taken
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[contains(text(),'Next')]")
                )
            )
        except:
            if (
                "Sorry, looks like this code has already been redeemed."
                in self.driver.page_source
            ):
                Console().sprint("Code has been redeemed", False)
                thread_lock.acquire()
                with open("links.txt", "r+") as io:
                    tokens = io.readlines()
                    io.seek(0)
                    for line in tokens:
                        if not (self.nitro_link in line):
                            io.write(line)
                    io.truncate()
                thread_lock.release()

                return False
            else:
                Console().sprint("Token is invalid", False)
                thread_lock.acquire()
                with open("tokens.txt", "r+") as io:
                    tokens = io.readlines()
                    io.seek(0)
                    for line in tokens:
                        if not (self.token in line):
                            io.write(line)
                    io.truncate()
                thread_lock.release()

                return False

        self.driver.execute_script(
            """
        document.querySelector("button[type='button']").click();
        """
        )

        WebDriverWait(self.driver, 40).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "div[role='button'][aria-disabled='false']")
            )
        )

        try:
            self.driver.find_element(
                By.CSS_SELECTOR, "div[role='button'][aria-disabled='false']"
            ).click()
        except:
            try:
                element = self.driver.find_element(
                    By.CSS_SELECTOR, "div[role='button'][aria-disabled='false']"
                )
                self.driver.execute_script("arguments[0].click();", element)
            except:
                self.driver.execute_script(
                    "document.querySelector('div[role='button'][aria-disabled='false']').click();"
                )

        self.driver.find_element(
            By.XPATH,
            "//div[@role='listbox']//div[@role='option']//div//div[contains(text(),'Add a new payment method')]",
        ).click()

        WebDriverWait(self.driver, 40).until(
            EC.presence_of_element_located((By.XPATH, "//body//div//button[1]"))
        )

        self.driver.execute_script(
            """
        document.querySelector("body div button:nth-child(1)").click();
        """
        )

        # All cc info is under an iframe
        WebDriverWait(self.driver, 50).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "iframe[title='Secure card number input frame']")
            )
        )

        WebDriverWait(self.driver, 50).until(
            EC.frame_to_be_available_and_switch_to_it(
                self.driver.find_element(
                    By.CSS_SELECTOR, "iframe[title='Secure card number input frame']"
                )
            )
        )

        WebDriverWait(self.driver, 40).until(
            EC.element_to_be_clickable((By.NAME, "cardnumber"))
        )
        self.driver.find_element(By.NAME, "cardnumber").send_keys(self.card_number)

        self.driver.switch_to.default_content()
        self.driver.switch_to.frame(1)
        WebDriverWait(self.driver, 40).until(
            EC.element_to_be_clickable((By.NAME, "exp-date"))
        )
        self.driver.find_element(By.NAME, "exp-date").send_keys(self.expiry)

        self.driver.switch_to.default_content()
        self.driver.switch_to.frame(2)
        WebDriverWait(self.driver, 40).until(
            EC.element_to_be_clickable((By.NAME, "cvc"))
        )
        self.driver.find_element(By.NAME, "cvc").send_keys(self.ccv)

        self.driver.switch_to.default_content()
        WebDriverWait(self.driver, 40).until(
            EC.element_to_be_clickable((By.NAME, "name"))
        )
        self.driver.find_element(By.NAME, "name").send_keys("Joseph Ring")

        self.driver.execute_script(
            """
        document.querySelector("button[type='submit']").click();
        """
        )

        try:
            WebDriverWait(self.driver, 40).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//input[@autocomplete='address-line1']")
                )
            )
        except TimeoutException:
            if "unable to confirm payment method" in self.driver.page_source.lower():
                Console().sprint(
                    f"VCC Has Failed -> {self.card_number}:{self.expiry}:{self.ccv}",
                    False,
                )
                used_vcc.append(f"{self.card_number}:{self.expiry}:{self.ccv}")
                return
            else:
                raise (TimeoutException)

        WebDriverWait(self.driver, 40).until(
            EC.element_to_be_clickable((By.ID, "uid_27"))
        )
        country = self.driver.find_element(By.ID, "uid_27")
        country.click()
        country.send_keys("UnitedStates")
        country.send_keys(Keys.ENTER)
        country.send_keys(Keys.ENTER)

        WebDriverWait(self.driver, 40).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//input[@autocomplete='address-line1']")
            )
        )
        self.driver.find_element(
            By.XPATH, "//input[@autocomplete='address-line1']"
        ).send_keys("420 6th Street")

        WebDriverWait(self.driver, 40).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@name='city']"))
        )
        self.driver.find_element(By.XPATH, "//input[@name='city']").send_keys("Decatur")

        self.driver.switch_to.default_content()

        WebDriverWait(self.driver, 40).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Select']"))
        )
        state = self.driver.find_element(By.XPATH, "//input[@placeholder='Select']")
        state.click()
        state.send_keys("Nebraska")
        state.send_keys(Keys.ENTER)
        state.send_keys(Keys.ENTER)

        WebDriverWait(self.driver, 40).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@name='postalCode']"))
        )
        self.driver.find_element(By.XPATH, "//input[@placeholder='00000']").send_keys(
            "68020"
        )

        self.driver.execute_script(
            """
        document.querySelector("button:nth-child(1)").click();
        """
        )

        try:
            WebDriverWait(self.driver, 40).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='checkbox']"))
            )
        except:
            pass

        if not ("Today's Total" in self.driver.page_source):
            for ___ in range(2):
                self.driver.refresh()

                WebDriverWait(self.driver, 40).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, "button[type='button']")
                    )
                )

                self.driver.execute_script(
                    """
                document.querySelector("button[type='button']").click();
                """
                )

                WebDriverWait(self.driver, 40).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//div[contains(text(),'I agree to the')]")
                    )
                )

                self.driver.execute_script(
                    """
                document.querySelector("input[type='checkbox']").click();
                """
                )

                self.driver.execute_script(
                    """
                document.querySelector("button[type='submit']").click();
                """
                )

                try:
                    WebDriverWait(self.driver, 25).until(
                        EC.presence_of_element_located(
                            (
                                By.XPATH,
                                "//div[contains(text(),'You now have superpowered perks and Server Boosts.')]",
                            )
                        )
                    )
                    Console().sprint(f"Nitro Activated -> {self.token}", True)
                    thread_lock.acquire()
                    activated_accounts += 1
                    with open("Success.txt", "a") as nitro_success:
                        if hasattr(self, "full_token"):
                            nitro_success.write(self.full_token + "\n")
                        else:
                            nitro_success.write(self.token + "\n")

                    # Removes the used materials
                    with open("tokens.txt", "r+") as io:
                        tokens = io.readlines()
                        io.seek(0)
                        for line in tokens:
                            if not (self.token in line):
                                io.write(line)
                        io.truncate()

                    with open("links.txt", "r+") as io:
                        tokens = io.readlines()
                        io.seek(0)
                        for line in tokens:
                            if not (self.nitro_link in line):
                                io.write(line)
                        io.truncate()
                    thread_lock.release()

                except TimeoutError:
                    if ___ != 2:
                        continue
                    else:
                        sys.stdout.write(
                            f"{Fore.RED}[-] Could Not Activate Nitro -> {self.token}\n"
                        )

                    return

                except:
                    continue

            sys.stdout.write(
                f"{Fore.RED}[-] Could Not Activate Nitro -> {self.token}\n"
            )

        else:
            self.driver.execute_script(
                """
            document.querySelector("input[type='checkbox']").click();
            """
            )

            self.driver.execute_script(
                """
            document.querySelector("button[type='submit']").click();
            """
            )

            try:
                WebDriverWait(self.driver, 40).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "//div[contains(text(),'You now have superpowered perks and Server Boosts.')]",
                        )
                    )
                )
                Console().sprint(f"Nitro Activated -> {self.token}", True)

                thread_lock.acquire()
                activated_accounts += 1

                with open("Success.txt", "a") as nitro_success:
                    if hasattr(self, "full_token"):
                        nitro_success.write(self.full_token + "\n")
                    else:
                        nitro_success.write(self.token + "\n")

                with open("tokens.txt", "r+") as io:
                    tokens = io.readlines()
                    io.seek(0)
                    for line in tokens:
                        if not (self.token in line):
                            io.write(line)
                    io.truncate()

                with open("links.txt", "r+") as io:
                    links = io.readlines()
                    io.seek(0)
                    for line in links:
                        if not (self.nitro_link in line):
                            io.write(line)
                    io.truncate()

                thread_lock.release()

            except:
                Console().sprint(f"Could Not Activate Nitro -> {self.token}", False)

    def __main__(self):
        self.__init_driver__()

        try:
            self.activate_nitro()
        except TimeoutException:
            Console().sprint("Proxy or host timed out", False)
        except:
            Console().sprint("Unknown Error. Skipping...", False)


if __name__ == "__main__":
    Console().clear()

    # Lists of supplies
    nitro_links = open("links.txt", "r").read().splitlines()
    tokens = open("tokens.txt", "r").read().splitlines()
    vcc = open("vcc.txt", "r").read().splitlines()
    proxies = open("proxies.txt", "r").read().splitlines()

    print(
        Center.XCenter(
            Colorate.Vertical(
                Colors.red_to_purple,
                f"""
                                          /$$$$$$              /$$     /$$
                                         /$$__  $$            | $$    |__/
                                        | $$  \ $$  /$$$$$$  /$$$$$$   /$$
                                        | $$  | $$ /$$__  $$|_  $$_/  | $$
                                        | $$  | $$| $$  \ $$  | $$    | $$
                                        | $$  | $$| $$  | $$  | $$ /$$| $$
                                        |  $$$$$$/| $$$$$$$/  |  $$$$/| $$
                                         \______/ | $$____/    \___/  |__/
                                                  | $$                    
                                                  | $$      Made by ! Aran#9999   
                                                  |__/      Nitro Redeemer

    """,
                1,
            )
        )
    )

    sys.stdout.write(
        f"{Fore.GREEN}Successfully Loaded{Fore.WHITE} ~ {Fore.LIGHTBLUE_EX}Nitro Links: {len(nitro_links)}, Tokens: {len(tokens)}, Vcc: {len(vcc)}, Proxies: {len(proxies)}"
        + "\n"
    )

    new_list = []

    with open("config.json", "r") as jsonfile:
        config = json.load(jsonfile)

    amt_of_use_on_cc = config["amt_of_use_on_cc"]
    thread_count = config["thread_count"]

    for x in range(len(vcc)):
        if amt_of_use_on_cc > 1:
            for _ in range(amt_of_use_on_cc):
                new_list.append(vcc[x])
        else:
            new_list.append(vcc[x])

    check_list = list(dict.fromkeys(new_list))

    global used_vcc
    used_vcc = []

    check_status = False

    def check_vcc():
        while not check_status:
            time.sleep(10)
            for item in check_list:
                if item not in new_list and item not in used_vcc:
                    used_vcc.append(item)

        return

    def delete_vcc():
        # To delete all used vcc
        while not check_status:
            time.sleep(10)
            if len(used_vcc) <= 0:
                with open("vcc.txt", "r+") as io:
                    vccs = io.readlines()
                    io.seek(0)
                    for line in vccs:
                        if not (line in list(dict.fromkeys(used_vcc))):
                            io.write(line)
                    io.truncate()

            thread_lock.acquire()
            used_vcc.clear()
            thread_lock.release()

    threading.Thread(target=check_vcc).start()
    threading.Thread(target=delete_vcc).start()
    threading.Thread(target=Console().update_title).start()

    try:
        while len(tokens) and len(new_list) and len(nitro_links) >= 1:
            local_threads = []

            for _ in range(int(thread_count)):
                if len(proxies) >= 1:
                    proxy = random.choice(proxies)
                else:
                    proxy = None

                try:
                    # Checks if vcc is invalid
                    for _ in range(5):
                        if new_list[0] in used_vcc:
                            new_list.pop(0)
                            cc = new_list[0]
                        else:
                            cc = new_list[0]
                            break

                    start_thread = threading.Thread(
                        target=Nitro(tokens[0], cc, nitro_links[0], proxy).__main__
                    )
                    local_threads.append(start_thread)
                    start_thread.start()
                    tokens.pop(0)
                    nitro_links.pop(0)
                    new_list.pop(0)

                except IndexError:
                    raise (Exception)
                except:
                    pass

            for x in local_threads:
                x.join()
    except:
        pass

    sys.stdout.write(f"{Fore.WHITE}[\] Ran out of usable materials\n")

    check_status = True

    os.system("pause")

    os._exit(1)
