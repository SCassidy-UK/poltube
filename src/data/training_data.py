import json
import channel as chan_rqsts
import os.path
import csv
from path import filepaths


class RawTrainingDataDownloader():
    """Docstring for RawTrainingDataDownloader."""
    def __init__(self, paths):
        self.channels_and_labels = self.read_channels_list(paths['channels'])
        self.output_path = paths['output']
        self.cookie_path = paths['cookie']
        self.cache_path = paths['cache']
        self.api_key = self.read_api_key(paths['api-key'])
        self.api_client = chan_rqsts.make_api_client(self.api_key)

    def read_channels_list(self, filepath):
        with open(filepath, 'r', encoding='utf8') as channels:
            next(channels)
            return dict(csv.reader(channels))

    def read_api_key(self, filepath):
        with open(filepath, 'r', encoding='utf8') as apifile:
            key = apifile.read()[:-1]
            return key

    def build_training_file(self):
        if self.check_overwrite():
            with open(self.output_path, 'w', encoding='utf8') as f:
                print("emptied existing file")
        else:
            return
        with chan_rqsts.UrlIdFinder(self.cache_path, self.cookie_path) as uif:
            for channel_dict in self.urls_to_raw_data(uif):
                with open(self.output_path, 'a', encoding='utf8') as f:
                    json.dump(channel_dict, f)

    def urls_to_raw_data(self, urlconverter):
        for chan_url in self.channels_and_labels:
            chan_label = self.channels_and_labels[chan_url]
            chan_id = urlconverter.url_to_id(chan_url)
            requester = chan_rqsts.ChannelDictBuilder(self.api_client, chan_id)
            channel_dict = requester.make_channel_dict(label=chan_label)
            yield channel_dict

    def check_overwrite(self):
        if os.path.exists(self.output_path):
            overwrite = False
            while not overwrite:
                choice = input(f"{self.output_path} exists. Overwrite? y/n?")
                if choice.lower() in ["no", "n"]:
                    return False
                elif choice.lower() in ["yes", "y"]:
                    return True
                else:
                    continue
        else:
            return True
