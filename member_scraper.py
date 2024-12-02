from bs4 import BeautifulSoup 
import requests

# The URL that lists members by popularity
url = "https://letterboxd.com/members/popular/this/all-time/page/"

# Where the name of all members will be stored
members_file = open("members_file.txt", "w")
# Clear file
members_file.write("")


for i in range(1,10):
    print(f"Scraping page {i}...")
    result = requests.get(url + str(i) + "/")
    members_doc = BeautifulSoup(result.text, "html.parser")

    members = members_doc.find_all("a", {"class": "name"})

    for i in range(30):
        members_file.write(members[i]['href'] + "\n")

members_file.write("patrickhwillems" + "\n")
members_file.write("anuragkashyap" + "\n")