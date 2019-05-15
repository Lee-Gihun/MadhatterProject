from DataCollector import DataCollector
import sys

def main():
    """
    argument parsing will be implemented for api key.
    """
    data_collector = DataCollector('RGAPI-1a5b4cc6-e9cb-4cd0-bd8a-2bc3af1b3934', batch_size=1000)
    print("Starting for userlist " + sys.argv[1])
    user_list = data_collector.user_selector('./data_batch/', int(sys.argv[1]))
    data_collector.save_data(user_list)
    print("End successfully!")

if __name__ == '__main__':
    main()
