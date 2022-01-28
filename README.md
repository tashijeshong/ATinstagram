# ATinstagram

Initial Setup:
1. Download this project as a .zip and extract the contents
2. Ensure you have installed Google Chrome (version 97*)
3. Install selenium (use "pip3 install selenium")
4. Fill in the credentials.txt file in the auth folder with your Instagram login information (credentials for an account created for this project can be made available upon request)

\*If your version of Google Chrome is 96 or 98, visit https://chromedriver.chromium.org/downloads and replace the executable with the one that is compatible with your version of Chrome


Steps to use:
1. Go into the src folder and call "python GetURL.py <hashtag> <# of pages to parse> <end cursor>" \*\*
2. Check the data folder for the results

\*\*Only the <hashtag> input parameter is required. The default number of pages to parse is 20, and API calls do not require an end cursor to parse recent posts





API format: 
Get 3 popular posts of <TAG> with 10 most recent:
	https://www.instagram.com/explore/tags/<TAG>/?__a=1

Get <NUMBER> posts under hashtag <TAG>:

https://www.instagram.com/graphql/query/?query_id=17875800862117404&variables=%7B%22tag_name%22%3A%22<TAG>%22%2C%22first%22%3A<NUMBER>%7D

<br/>

Get <NUMBER> posts under hashtag <TAG> after <END_CURSOR>:

https://www.instagram.com/graphql/query/?query_id=17875800862117404&variables=%7B%22tag_name%22%3A%22<TAG>%22%2C%22first%22%3A<NUMBER>%2C%22after%22%3A%22<END_CURSOR>%22%7D

see: https://github.com/InstaPy/instapy-research/blob/master/api/old_api/README.md

To view any actual post: https://www.instagram.com/p/{shortcode}
	where {shortcode} is located in the node in the list of edges
