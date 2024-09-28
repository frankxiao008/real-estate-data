import requests
from bs4 import BeautifulSoup
import pandas as pd 
import os
from playwright.async_api import async_playwright
import csv
from datetime import datetime
import asyncio


async def get_dynamic_soup(url: str) -> BeautifulSoup:
    async with async_playwright() as p: # Use async_playwright
        browser = await p.chromium.launch() # Use await for asynchronous operations
        page = await browser.new_page() # Use await for asynchronous operations
        await page.goto(url) # Use await for asynchronous operations
        soup = BeautifulSoup(await page.content(), "html.parser") # Use await for asynchronous operations
        await browser.close() # Use await for asynchronous operations
        return soup

async def main():

    soup =await get_dynamic_soup("https://www.rentfaster.ca/ab/calgary/rentals/")
    listing_count_element = soup.find("h3", class_="title is-size-6 mt-1").find("span", class_="dnt ng-binding")

    number =  int(listing_count_element.text.strip("()"))

    # Extract the number of listings
    if listing_count_element:
      print("Number of listings:", number)
    else:
      print("Listing count not found.")

    # Get the current datetime
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
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
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow([current_time, number])


# Run the main function
if __name__ == "__main__":
    asyncio.run(main())