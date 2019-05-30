from Models.DataCollector import DataCollector
import sys

def main():
    """
    argument parsing will be implemented for api key.
    """
    data_collector = DataCollector('RGAPI-f2893ea4-8d79-44cc-8640-3c9d69485248', batch_size=1000)
    print("Starting for userlist " + sys.argv[1])
    user_list = data_collector.user_selector('./data_batch/', int(sys.argv[1]))
    data_collector.save_data(user_list)
    print("End successfully!")

if __name__ == '__main__':
    main()
