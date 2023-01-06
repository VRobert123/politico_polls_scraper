import pandas as pd
import datetime
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def render_page(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    time.sleep(3)
    print('Open browser and accept cookies...')
    WebDriverWait(driver, 3).until(
        EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe[id='sp_message_iframe_527577']")))
    driver.find_element(By.CSS_SELECTOR, 'button[title="Agree"]').click()
    driver.switch_to.default_content()
    print('Set time for polls...')
    driver.find_element(By.CSS_SELECTOR, 'a[data-month="-1"]').click()
    print('Saving html file...')
    r = driver.page_source
    driver.quit()
    return r

#Calculating linear regression between two variables (x, y) and returning interception and coef.
def linear_regression(x, y):
    x_mean = x.mean()
    y_mean = y.mean()

    B1_num = ((x - x_mean) * (y - y_mean)).sum()
    B1_den = ((x - x_mean) ** 2).sum()
    B1 = B1_num / B1_den

    B0 = y_mean - (B1 * x_mean)

    return B0, B1

#Use interception and coef to predict Y by X.
def predict(B0, B1, new_x):
    y = B0 + B1 * new_x
    return y



#Class for scraping:
class Politico:

    def __init__(self):
        #Initalization

        #Self.df is used for store party names, position on the x axis and position on the y axis.
        self.df = pd.DataFrame()
        self.df['party'] = 0
        self.df['cx'] = 0
        self.df['cy'] = 0

        #self.df1 is used for storing cy values and the attached percentage values.
        self.df1 = pd.DataFrame()
        self.df1['value'] = 0
        self.df1['percentage'] = 0

        #self.df2 is used for storing cx values and datetime.
        self.df2 = pd.DataFrame()
        self.df2['value'] = 0
        self.df2['time'] = 0

        # list of countries
        self.countries = ['austria', 'switzerland', 'cyprus', 'czech-republic',
                          'germany', 'estonia', 'spain', 'finland', 'greece', 'croatia',
                          'hungary', 'ireland', 'italy', 'lithuania', 'luxembourg', 'latvia', 'malta',
                          'netherlands', 'norway', 'poland', 'portugal', 'romania', 'sweden',
                          'slovakia', 'united-kingdom']

    def get_list(self):

        #print countries
        print('These countries are available in the package:')
        print(self.countries)

    def help(self):
        print('These are the methods what you can use:')
        print('.get_list - shows the available countries to download')
        print(".download - downloads the data. Syntax: myvariable.download('country')")
        print('You can save the result dataframe to a variable as: results = myvariable.df. This gives a pandas dataframe.')

    def download(self, country):

        self.country = country

        if self.country not in self.countries:
            print('Unknown or not supported country. Please try another.')
            return ''

        #create link
        self.link = f"https://www.politico.eu/europe-poll-of-polls/{country}"
        print(f'{self.link} created...')

        #download html file
        self.r = render_page(self.link)

        #search for the poll dots and the cx and cy values for df1 and df2
        print(f'Find important html elements...')
        self.soup = BeautifulSoup(self.r, "html.parser")
        self.poll_dots = self.soup.find_all('circle', {"class": "poll-dot"})
        self.coords = self.soup.find_all('g', {"class": "tick"})

        #collect self.coords to dataframes by a condition
        print('Create pattern tables for cx and cy...')
        for i in range(len(self.coords)):

            #if in 'transform="translate(0,420.5)"' the 10th character is zero, then that belongs to df1
            if self.coords[i]['transform'][10] == '0':

                if self.coords[i].text[:-1] == '':
                    self.df1.loc[len(self.df1)] = [float(self.coords[i]['transform'].split(',')[1][:-1]), int(self.coords[i].text)]
                else:
                    self.df1.loc[len(self.df1)] = [float(self.coords[i]['transform'].split(',')[1][:-1]), int(self.coords[i].text[:-1])]

            #if not, that belongs to df2
            else:

                try:
                    self.df2.loc[len(self.df2)] = [float(self.coords[i]['transform'].split(',')[0][10:]),
                                               datetime.datetime.strptime(f'{self.coords[i].text}-01-01', '%Y-%m-%d')]
                except:
                    pass

        #transform date to numerical dtype because of the regression
        self.df2['time'] = self.df2['time'].map(datetime.datetime.toordinal)

        #create x and y values, and create B0 and B1 by the linear regression function.
        print('Calculate linear regression to predict percentage.....')
        self.x = self.df1['value']
        self.y = self.df1['percentage']
        self.B0, self.B1 = linear_regression(self.x, self.y)

        # create x2 and 2 values, and create B02 and B12 by the linear regression function.
        print('Calculate linear regression to predict date...')
        self.x2 = self.df2['value']
        self.y2 = self.df2['time']
        self.B02, self.B12 = linear_regression(self.x2, self.y2)

        #Add to self.df party names, cx and cy, then apply the predict function on cy and cx
        print('Create result DataFrame...')
        for i in range(len(self.poll_dots)):
            self.df.loc[len(self.df)] = [self.poll_dots[i]['class'][1].split('-')[-1], self.poll_dots[i]['cx'], self.poll_dots[i]['cy']]

        self.df['percentages'] = self.df['cy'].apply(lambda x: predict(self.B0, self.B1, float(x)))
        self.df['date'] = self.df['cx'].apply(lambda x: predict(self.B02, self.B12, float(x)))

        #transform numerical date back to date format
        self.df['date'] = self.df['date'].map(round)
        self.df['date'] = self.df['date'].map(datetime.datetime.fromordinal)

        #remove cx and cy columns from self.df
        self.df = self.df.drop('cy', axis=1)
        self.df = self.df.drop('cx', axis=1)

        #result
        print(self.df)
        print('Now you can reach the DataFrame by using this expression: myvariable.df')




