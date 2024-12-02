from bs4 import BeautifulSoup
import requests
import csv

members_file = "members_file.txt"
csv_file = open("movies.csv", "w", newline="", encoding="utf-8")
csv_writer = csv.writer(csv_file)
csv_writer.writerow(["User", "Film ID", "Rating"])

with open(members_file, "r") as file:
    users = [line.strip() for line in file]

for user in users:
    base_url = f"https://letterboxd.com/{user}/films/page/"
    page_number = 1

    while True:
        url = base_url + str(page_number) + "/"
        print(f"Scraping page {page_number} for user {user}...")
        
        try:
            result = requests.get(url)
            result.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
            
            members_doc = BeautifulSoup(result.text, "html.parser")
            films = members_doc.find_all("li", {"class": "poster-container"})
            
            if not films:
                print(f"No more films found for user {user}. Moving to the next user.")
                break
            
            for film in films:
                film_div = film.find("div", {"class": "really-lazy-load"})
                if film_div:
                    film_id = film_div["data-film-slug"]
                    rating_element = film.find("span", {"class": ["rating", "-micro", "-darker"]})
                    if rating_element:
                        rating = rating_element.text.strip()
                        csv_writer.writerow([user, film_id, rating])
            
            page_number += 1
            
        except requests.exceptions.RequestException as e:
            print(f"Error occurred while scraping page {page_number} for user {user}: {e}")
            break

csv_file.close()