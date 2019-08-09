from datetime import datetime
from dateutil.relativedelta import relativedelta
from googleapiclient.discovery import build
import pandas as pd

DEVELOPER_KEY = 'AIzaSyCPH3vXx9ITOe3kR6WYvePaZW72FETcJLQ'
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
df = pd.read_csv("youtuber_list.csv")
CHANNEL_ID = list(df["id"])
print(CHANNEL_ID)


youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

channel_videos = []


class Item:

    def __init__(self, videoId, **kwargs):
        self.video_id = videoId


class Feed:

    def __init__(self, items, **kwargs):
        self.next_page_token = kwargs.get('nextPageToken')
        self.items = []
        if isinstance(items, list):
            self.items = [Item(**item['id']) for item in items]


def _request_videos(count=10, channel_id=CHANNEL_ID, token=None):
    # import dummy
    # return Feed(**dummy.response)
    day_start = datetime.now() - relativedelta(years=1, hour=0, minute=0, second=0, microsecond=0)
    day_end = day_start + relativedelta(days=1, microseconds=-1)
    # after_datetime = datetime(year=2019, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    published_after = day_start.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-5] + 'Z'
    published_before = day_end.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-5] + 'Z'

    print(published_after, published_before)

    response = youtube.search().list(channelId=channel_id, maxResults=count, order='viewCount', publishedAfter=published_after,
                                     publishedBefore=published_before, type='video', part='id', pageToken=token).execute()
    return Feed(**response)


def get_channel_videos(count, channel_id, token=None):
    if count == 0:
        print('データ取得を終了しました')
        return

    # Max 50件取得可能
    max_results = count if count <= 50 else 50

    feed = _request_videos(count=max_results, channel_id=channel_id,token=token)
    print(f'{len(feed.items)}件データ取得しました')

    # 次ページのカウント数
    next_count = count - max_results

    channel_videos.extend([item.video_id for item in feed.items])
    if len(channel_videos) == 0 and not feed.next_page_token:
        return

    get_channel_videos(next_count, channel_id, feed.next_page_token)

def get_video_detail(videoId):
    if videoId == None:
        print("動画が取得されませんでした")
        return

    response = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        id=videoId
    ).execute()

    title = response.get("items")[0].get("snippet").get("title")
    viewCount = response.get("items")[0].get("statistics").get("viewCount")

    channel_videos_info = {title: int(viewCount)}
    print(channel_videos_info)


if __name__ == '__main__':
    for channel in CHANNEL_ID:
        get_channel_videos(count=1, channel_id=channel)
    for channel_video in channel_videos:
        get_video_detail(channel_video)