import asyncio
from playwright.async_api import async_playwright
import os
import csv
from datetime import datetime
# from playwright.async_api import Playwright, async_playwright
async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        print("Start")
        # Enable console logging
        page.on("console", lambda msg: print(f"Page log: {msg.text}"))

        # Log responses
        page.on("response", lambda response: print(f"Response: {response.url} - Status: {response.status}"))

        # Set request interception to block images and stylesheets, allow scripts



        # Navigate to the rentals page
        await page.goto('https://www.rentfaster.ca/ab/calgary/rentals/', timeout=580000)
        print("wait for element")
        # Wait for the necessary elements to load
        await page.wait_for_selector('h3.title.is-size-6.mt-1', timeout=580000)

        # Get the text content of the element
        title_element = await page.query_selector('h3.title.is-size-6.mt-1')
        print(title_element)
        title = await title_element.inner_text() if title_element else 'No title found'
        print(f"Title: {title}")

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
        with open(csv_file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            
            # If the file did not exist, write the header
            if not file_exists:
                writer.writerow(['Datetime', 'Number'])  # Write header row

            # Write the datetime and the number as a new row
            writer.writerow([current_datetime, number])

        # Close the browser
        await browser.close()
        return number

if __name__ == '__main__':
    asyncio.run(run())

