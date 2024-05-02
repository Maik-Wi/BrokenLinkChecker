import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def get_links_from_sitemap(sitemap_url):
    try:
        print("Fetching links from sitemap...")
        response = requests.get(sitemap_url)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            urls = []
            for child in root:
                for subchild in child:
                    if subchild.tag.endswith('loc'):
                        urls.append(subchild.text)
            print("Links fetched successfully.")
            return urls
        else:
            print("Failed to fetch sitemap.xml")
            return None
    except Exception as e:
        print("An error occurred:", str(e))
        return None

def get_article_links(url, sitemap_domain):
    try:
        print("Fetching article links from:", url)
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            article_links = []
            for link in soup.find_all('a'):
                href = link.get('href')
                if href and href.startswith("http"):
                    parsed_href = urlparse(href)
                    if parsed_href.netloc.split('.')[-2:] != sitemap_domain.split('.')[-2:]:
                        article_links.append(href)
            print("Article links fetched successfully.")
            return article_links
        else:
            print("Failed to fetch article links:", response.status_code)
            return None
    except Exception as e:
        print("An error occurred while fetching article links:", str(e))
        return None

def check_links(links):
    print("Checking article links for validity...")
    broken_links = []
    for link in links:
        try:
            response = requests.get(link)
            if response.status_code != 200:
                broken_links.append(link)
                print("Broken link found:", link, "- Status code:", response.status_code)
            else:
                print("Link is valid:", link)
        except Exception as e:
            print("An error occurred while checking link:", link, "-", str(e))
    if not broken_links:
        print("All links are valid.")
    return broken_links

def write_to_log(broken_links):
    with open("404.log", "w") as f:
        for link in broken_links:
            f.write(link + "\n")
    print("Broken links written to 404.log")

def main(sitemap_url):
    links = get_links_from_sitemap(sitemap_url)
    if links:
        sitemap_domain = urlparse(sitemap_url).netloc
        article_links = []
        for link in links:
            article_links.extend(get_article_links(link, sitemap_domain))
        if article_links:
            broken_links = check_links(article_links)
            if broken_links:
                write_to_log(broken_links)
                print("Broken links found. Check 404.log for details.")
            else:
                print("No broken links found.")
        else:
            print("No article links found in the sitemap.")
    else:
        print("No links found in the sitemap.")

if __name__ == "__main__":
    sitemap_url = input("Please enter the URL of the sitemap.xml: ")
    main(sitemap_url)
