from DataCollector import DataCollector


def main():
    """
    argument parsing will be implemented for api key.
    """
    data_collector = DataCollector('your_api_key')
    data_collector.save_data()



if __name__ == '__main__':
    main()