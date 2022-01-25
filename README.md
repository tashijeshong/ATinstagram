# ATinstagram

Initial Setup:
1. Download all python libraries you don't have (use "pip3 install selenium" for that library)
2. Download Chrome Driver for your version of Chrome, unzip it, and make note of the location of the executable (see here: https://chromedriver.chromium.org/downloads)
3. Change the line in GetURL.py (src folder) to be your path to the ChromeDriver executable. (Should be line 61 atm).
4. Fill in the credentials.txt file in the auth folder with your Instagram login information


Steps to use:
1. Log into Instagram in any browser
2. Make an API request (details to follow)
3. Save the contents of the page into a text file (CTRL+A, CTRL+C, CTRL+V)
4. Place text file into data folder
5. Run src using textfile name as parameter





API format: 
Get 3 popular posts of <TAG> with 10 most recent:
	https://www.instagram.com/explore/tags/<TAG>/?__a=1

Get <NUMBER> posts under hashtag <TAG>:
	https://www.instagram.com/graphql/query/?query_id=17875800862117404&variables=%7B%22tag_name%22%3A%22<TAG>%22%2C%22first%22%3A<NUMBER>%7D
Get <NUMBER> posts under hashtag <TAG> after <END_CURSOR>:
	https://www.instagram.com/graphql/query/?query_id=17875800862117404&variables=%7B%22tag_name%22%3A%22<TAG>%22%2C%22first%22%3A<NUMBER>%2C%22after%22%3A%22<END_CURSOR>%22%7D

see: https://github.com/InstaPy/instapy-research/blob/master/api/old_api/README.md

To view any actual post: https://www.instagram.com/p/{shortcode}
	where {shortcode} is located in the node in the list of edges
