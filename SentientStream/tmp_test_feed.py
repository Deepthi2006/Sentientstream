import requests
import json

def test_feed():
    try:
        response = requests.get("http://localhost:8000/feed/?mood=calm&k=5")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Videos returned: {len(data)}")
            if len(data) > 0:
                print(f"First video: {data[0]['title']} ({data[0]['video_id']})")
                print(f"Stream URL: {data[0]['stream_url']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Could not connect to backend: {e}")

if __name__ == "__main__":
    test_feed()
