import django
from django.conf import settings
django.setup()
from collector.models import PuzzlePiece
from urllib.parse import urlparse
import hashlib
import requests

def hash_my_data(url):
        url = url.encode("utf-8")
        hash_object = hashlib.sha256(url)
        hex_dig = hash_object.hexdigest()
        return hex_dig

def main():
	with open("images.txt", "r") as infile:
		data = infile.readlines()

	for line in data:
		try:
			line = line.rstrip()
			if not line:
				continue
			print(line)
			host = urlparse(line).hostname 
			if host in ["tjl.co","gamerdvr.com","dropbox.com","www.gamerdvr.com","www.dropbox.com"]:
				raise ValueError('We cannot accept images from gamerdvr or dropbox or tjl.co - try another host please, Discord works great!')
			# Check this can be reached
			request = requests.get(line)
			if request.status_code != 200:
				raise ValueError('That URL does not seem to exist. Please verify and try again.')
			i = PuzzlePiece()
			i.url = line
			i.hash = hash_my_data(line)
			i.ip_address = "127.0.0.1"
			i.approved = True
			i.save()
		except KeyError as ex:
			print ("There was an issue with your request.")
		except ValueError as ex:
			print (str(ex))
		except Exception as ex:
			if "unique" in str(ex).lower() or "duplicate" in str(ex).lower():
				print("Looks like that puzzle piece image has already been submitted. Thanks for submitting!")
			else:
				print ("Something went wrong..." + str(ex))

if __name__ == "__main__":
	main()

