import requests
from urllib.request import urlparse, urljoin
from bs4 import BeautifulSoup
import colorama
import sys
#import grequests

colorama.init()
sys.setrecursionlimit(1500)

GREEN = colorama.Fore.GREEN
GRAY = colorama.Fore.LIGHTBLACK_EX
RED = colorama.Fore.RED
YELLOW = colorama.Fore.YELLOW
RESET = colorama.Fore.RESET

internal_urls = set()
external_urls = set()
broken_urls = set()
image_urls_dict = dict()

# checks if the URL is valid
def is_valid(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme) and (url != 'https://www.guardicore.com/') and (url != 'https://www.guardicore.com')


def crawl(url, depth):

    urls = set()
    
    # checks if the url is broken
    requestObj = requests.get(url)
    if(requestObj.status_code == 404):
       if url not in broken_urls:
           broken_urls.add(url)
           return

    soup = BeautifulSoup(requestObj.content, "html.parser")
    domain_name = urlparse(url).netloc

    # get all HTML a tags 
    for a_tag in soup.findAll("a"):
        href = a_tag.attrs.get("href")

        # href is an empty tag
        if href == "" or href is None:
            continue

        href = urljoin(url, href)
        parsed_href = urlparse(href)

        # remove url parameters
        href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path

        if not is_valid(href):
            continue
        
        # already in internal_urls set
        if href in internal_urls:
            continue
        
        # the url is an external link
        if domain_name not in href: 
            if href not in external_urls:
                print(f"{GRAY}[*] External link: {href}{RESET}"+ "  Depth: "+ str(depth))
                external_urls.add(href)
            continue 
        
        # the url is an internal link and not in internal_urls set
        print(f"{GREEN}[*] Internal link: {href}{RESET}" + "  Depth: "+ str(depth))
        internal_urls.add(href)

        # add to childs set
        if not href.endswith((".pdf", ".jpg" ,".png" ,".zip")):
            urls.add(href)
    
    # *************************** BONUS *******************************

    for img in soup.find_all("img"):
        img_url = img.attrs.get("src")

         # if img doesnt contain src attribute
        if not img_url:  
            continue

        img_url = urljoin(url, img_url)

        # remove url parmeters
        try:
            pos = img_url.index("?")
            img_url = img_url[:pos]
        except ValueError:
            pass

        #if the url is valid
        if is_valid(img_url):
            if img_url not in image_urls_dict:
                image_urls_dict.update({img_url : 1})
            if img_url in image_urls_dict:
                if image_urls_dict.get(img_url) == 1:
                   print(f"{YELLOW}[!] Duplicated image: {img_url}{RESET}") 
                   image_urls_dict[img_url] += 1  
                else:
                    image_urls_dict[img_url] += 1

    # *************************** BONUS *******************************

    # iterate childs
    for link in urls:
        if depth < 2:
            crawl(link, depth + 1)


if __name__ == "__main__":
    crawl("https://www.guardicore.com/", 0)
    print("*************************************")
    print("[+] Total External links:", len(external_urls))
    print("[+] Total Internal links:", len(internal_urls))
    print("[+] Total links:", len(external_urls) + len(internal_urls))
    print("*************************************")
    for url in broken_urls:
        print(f"{RED}[!] Broken link: {url}{RESET}")
    print("[+] Total Broken links:", len(broken_urls))
    print("*************************************")
    print("[+] Total Duplicated images:", len(image_urls_dict))