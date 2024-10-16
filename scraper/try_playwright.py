import asyncio
from playwright.async_api import async_playwright
import os
import csv
from datetime import datetime
import pandas as pd
# from playwright.async_api import Playwright, async_playwright



async def run(url: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        print("Start")
        # Enable console logging
        # page.on("console", lambda msg: print(f"Page log: {msg.text}"))

        # Log responses
        # page.on("response", lambda response: print(f"Response: {response.url} - Status: {response.status}"))

        # Set request interception to block images and stylesheets, allow scripts

        # Navigate to the rentals page
        # url https://www.rentfaster.ca   /ab/calgary/  /ab/airdrie/

        await page.goto(url, timeout=580000)
        print("wait for element")
        # Wait for the necessary elements to load
        await page.wait_for_selector('h3.title.is-size-6.mt-1', timeout=580000)

        # Get the text content of the element
        title_element = await page.query_selector('h3.title.is-size-6.mt-1')
        # print(title_element)
        title = await title_element.inner_text() if title_element else 'No title found'
        # print(f"Title: {title}")

        # Extract data for listings
        listings = await page.eval_on_selector_all('h3.title.is-size-6.mt-1', '''
            elements => elements.map(element => {
                const span = element.querySelector('span.dnt.ng-binding');
                return {
                    listings: span ? span.innerText.trim() : 'None'
                };
            })
        ''')

        print("Listings:")
        for listing in listings:
            print(listing)
        
        number = int(listings[0]['listings'].strip("()"))
        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # Define the path to your CSV file
        csv_file_path = 'data/data.csv'

        # Check if the file exists
        file_exists = os.path.isfile(csv_file_path)
        
        # Open the CSV file in append mode
        # with open(csv_file_path, mode='a', newline='') as file:
        #     writer = csv.writer(file)
            
        #     # If the file did not exist, write the header
        #     if not file_exists:
        #         writer.writerow(['Datetime', 'Number'])  # Write header row

        #     # Write the datetime and the number as a new row
        #     writer.writerow([current_datetime, number])

        # Close the browser
        await browser.close()
        return number


async def scrape_rental_stats(url: str) -> pd.DataFrame:
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url,timeout=580000)

        # Wait for the table to load (adjust selector if needed)
        await page.wait_for_selector("table.is-hoverable.is-size-5.is-striped.is-fullwidth", timeout=580000)

        # Extract table data using Playwright's evaluate function

        data = await page.evaluate('''() => {
            const headerRow = document.querySelector("table.is-hoverable.is-size-5.is-striped.is-fullwidth thead tr"); 
            const headers = [...Array.from(headerRow.querySelectorAll("th")).map(th => th.innerText), "Link"];
            const rows = Array.from(document.querySelectorAll("table.is-hoverable.is-size-5.is-striped.is-fullwidth tbody tr"));
            const dataRows = rows.map(row => {
                const columns = Array.from(row.querySelectorAll("td"));
                const link = row.querySelector("a.stats-table-link")?.href; // Get the href attribute of the link
                return [...columns.map(column => column.innerText), link]; // Add the link to the row data
            });

            return [headers, ...dataRows]; // Combine headers and data rows
        }''')
        # Convert the extracted data to a Pandas DataFrame
        df = pd.DataFrame(data[1:], columns=data[0]) 

        # Get the current datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Add the datetime to the DataFrame
        df['Datetime'] = current_time 

        await browser.close()
        # Add ListingsNum column if it doesn't exist
        if 'ListingsNum' not in df.columns:
            df['ListingsNum'] = 0  # Initialize with 0
        print(df)
        return df


async def main():
    url = "https://www.rentfaster.ca/?rr=eJwDAAAAAAE%3D"
    rental_stats_df = await scrape_rental_stats(url)
    for index, row in rental_stats_df.iterrows():
        link = row['Link']
        if link is not None:
            listings_num = await run(link)
            rental_stats_df.loc[index, 'ListingsNum'] = listings_num  
            await asyncio.sleep(10)
    # print(rental_stats_df)

        # Get a list of all column names
    cols = rental_stats_df.columns.tolist()

    # Move 'Datetime' to the beginning of the list
    cols.insert(0, cols.pop(cols.index('Datetime'))) 

    # Reindex the DataFrame with the new column order
    rental_stats_df = rental_stats_df.reindex(columns=cols)    
    rental_stats_df = rental_stats_df.drop('Link', axis=1)


    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    current_dir = os.path.dirname(__file__)  # Gets the directory of the current script
    sibling_dir = os.path.join(current_dir, '..', 'data')  
    csv_file_path = os.path.join(sibling_dir, current_datetime + '_rental_stats.csv')
    print("save file to " + csv_file_path)
    # You can save the DataFrame to a CSV file if needed:
    rental_stats_df.to_csv(csv_file_path, index=False)

def test():
    rental_stats_df = pd.read_csv('data/2024-10-10 225527rental_stats.csv')   
    # Get a list of all column names
    cols = rental_stats_df.columns.tolist()
    # Define the current directory and the sibling directory
    current_dir = os.path.dirname(__file__)  # Gets the directory of the current script
    sibling_dir = os.path.join(current_dir, '..', 'data')  
    print(sibling_dir)
    csv_file_path = os.path.join(sibling_dir, 'test.csv')
    # Move 'Datetime' to the beginning of the list
    cols.insert(0, cols.pop(cols.index('Datetime'))) 

    # Reindex the DataFrame with the new column order
    rental_stats_df = rental_stats_df.reindex(columns=cols)    
    rental_stats_df = rental_stats_df.drop('Link', axis=1)
    
    rental_stats_df.to_csv(csv_file_path, index=False)

if __name__ == '__main__':
    asyncio.run(main())
 