# import required packages
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv

# start the selenium browser session
chrome_options = Options()
#chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 10)
# load desired page in the browser
driver.get("https://www.sunbeaminfo.in/internship")
print("Page Title:", driver.title)
# define wait strategy
driver.implicitly_wait(5)
# interact with web controls
table = wait.until(
    EC.presence_of_element_located(
        (By.XPATH, "//div[@id='collapseSix']//table")
    )
)

rows = table.find_elements(By.XPATH, ".//tbody/tr")

with open("table_data.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        row_data = [cell.get_attribute("textContent").strip() for cell in cells]
        writer.writerow(row_data)

print("Table saved to table_data.csv")
driver.quit()