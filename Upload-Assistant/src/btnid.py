import httpx
import uuid

from src.bbcode import BBCODE
from src.console import console


async def generate_guid():
    return str(uuid.uuid4())


async def get_btn_torrents(btn_api, btn_id, meta):
    imdb_id = 0
    tvdb_id = 0
    if meta['debug']:
        print("Fetching BTN data...")
    post_query_url = "https://api.broadcasthe.net/"
    post_data = {
        "jsonrpc": "2.0",
        "id": (await generate_guid())[:8],
        "method": "getTorrentsSearch",
        "params": [
            btn_api,
            {"id": btn_id},
            50
        ]
    }
    headers = {"Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(post_query_url, headers=headers, json=post_data, timeout=10)
            response.raise_for_status()
            try:
                data = response.json()
            except ValueError as e:
                print(f"[ERROR] Failed to parse BTN response as JSON: {e}")
                print(f"Response content: {response.text[:200]}...")
                return 0, 0
    except Exception as e:
        print(f"[ERROR] Failed to fetch BTN data: {e}")
        return 0, 0

    if not data or not isinstance(data, dict):
        print("[ERROR] BTN API response is empty or invalid.")
        return 0, 0

    if "result" in data and "torrents" in data["result"]:
        torrents = data["result"]["torrents"]
        first_torrent = next(iter(torrents.values()), None)
        if first_torrent:
            imdb_id = first_torrent.get("ImdbID")
            tvdb_id = first_torrent.get("TvdbID")

            if imdb_id or tvdb_id:
                return imdb_id, tvdb_id
    if meta['debug']:
        console.print("[red]No IMDb or TVDb ID found.")
    return 0, 0


async def get_bhd_torrents(bhd_api, bhd_rss_key, meta, only_id=False, info_hash=None, filename=None, foldername=None, torrent_id=None):
    imdb = 0
    tmdb = 0
    if meta['debug']:
        print("Fetching BHD data...")
    post_query_url = f"https://beyond-hd.me/api/torrents/{bhd_api}"

    if torrent_id is not None:
        post_data = {
            "action": "details",
            "torrent_id": torrent_id,
        }
    else:
        post_data = {
            "action": "search",
            "rsskey": bhd_rss_key,
        }

    if info_hash:
        post_data["info_hash"] = info_hash

    if filename:
        post_data["file_name"] = filename

    if foldername:
        post_data["folder_name"] = foldername

    headers = {"Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(post_query_url, headers=headers, json=post_data, timeout=10)
            response.raise_for_status()
            try:
                data = response.json()
            except ValueError as e:
                print(f"[ERROR] Failed to parse BHD response as JSON: {e}")
                print(f"Response content: {response.text[:200]}...")
                return 0, 0
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        print(f"[ERROR] Failed to fetch BHD data: {e}")
        return 0, 0

    if data.get("status_code") == 0 or data.get("success") is False:
        error_message = data.get("status_message", "Unknown BHD API error")
        print(f"[ERROR] BHD API error: {error_message}")
        return 0, 0

    # Handle different response formats from BHD API
    first_result = None

    # For search results that return a list
    if "results" in data and isinstance(data["results"], list) and data["results"]:
        first_result = data["results"][0]

    # For single torrent details that return a dictionary in "result"
    elif "result" in data and isinstance(data["result"], dict):
        first_result = data["result"]

    if not first_result:
        print("No valid results found in BHD API response.")
        return 0, 0

    name = first_result.get("name", "").lower()
    if not torrent_id:
        torrent_id = first_result.get("id", 0)

    # Check if description is just "1" indicating we need to fetch it separately
    description_value = first_result.get("description")
    if description_value == 1 or description_value == "1":

        desc_post_data = {
            "action": "description",
            "torrent_id": torrent_id,
        }

        try:
            async with httpx.AsyncClient() as client:
                desc_response = await client.post(post_query_url, headers=headers, json=desc_post_data, timeout=10)
                desc_response.raise_for_status()
                desc_data = desc_response.json()

                if desc_data.get("status_code") == 1 and desc_data.get("success") is True:
                    description = str(desc_data.get("result", ""))
                    print("Successfully retrieved full description")
                else:
                    description = ""
                    error_message = desc_data.get("status_message", "Unknown BHD API error")
                    print(f"[ERROR] Failed to fetch description: {error_message}")
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            print(f"[ERROR] Failed to fetch description: {e}")
            description = ""
    else:
        # Use the description from the initial response
        description = str(description_value) if description_value is not None else ""

    imdb_id = first_result.get("imdb_id", "").replace("tt", "") if first_result.get("imdb_id") else 0
    imdb = int(imdb_id or 0)

    raw_tmdb_id = first_result.get("tmdb_id", "")
    if raw_tmdb_id and raw_tmdb_id != "0":
        meta["category"], parsed_tmdb_id = await parse_tmdb_id(raw_tmdb_id, meta.get("category"))
        tmdb = int(parsed_tmdb_id or 0)

    if only_id and not meta.get('keep_images'):
        return imdb, tmdb

    bbcode = BBCODE()
    imagelist = []
    if "framestor" in name:
        meta["framestor"] = True
    elif "flux" in name:
        meta["flux"] = True
    description, imagelist = bbcode.clean_bhd_description(description, meta)
    if not only_id:
        meta["description"] = description
        meta["image_list"] = imagelist
    elif meta.get('keep_images'):
        meta["description"] = ""
        meta["image_list"] = imagelist

    console.print(f"[green]Found BHD IDs: IMDb={imdb}, TMDb={tmdb}")

    return imdb, tmdb


async def parse_tmdb_id(tmdb_id, category):
    """Parses TMDb ID, ensures correct formatting, and assigns category."""
    tmdb_id = str(tmdb_id).strip().lower()

    if tmdb_id.startswith('tv/') and '/' in tmdb_id:
        tmdb_id = tmdb_id.split('/')[1].split('-')[0]
        category = 'TV'
    elif tmdb_id.startswith('movie/') and '/' in tmdb_id:
        tmdb_id = tmdb_id.split('/')[1].split('-')[0]
        category = 'MOVIE'

    return category, tmdb_id
