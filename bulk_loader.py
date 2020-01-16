from collector.models import PuzzlePiece

def main():
	with open("images.txt", "r") as infile:
		data = infile.readlines()

	for line in data:
		print(line)
		i = PuzzlePiece()
		i.url = line
		i.ip_address = "127.0.0.1"
		i.approved = True
		i.save()


if __name__ == "__main__":
	main()

