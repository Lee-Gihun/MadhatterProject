from DataCollector import DataCollector
import sys

def main():
    """
    argument parsing will be implemented for api key.
    """
    data_collector = DataCollector('RGAPI-bc250003-ad85-4e3b-ab45-8e5fafc45c5a', batch_size=1000)
    print("Starting for userlist " + sys.argv[1])
    user_list = data_collector.user_selector('./data_batch/', int(sys.argv[1]))
    data_collector.save_data(user_list)
    print("End successfully!")

if __name__ == '__main__':
    main()
