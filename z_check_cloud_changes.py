
import traceback, json, asyncio, requests, os
from libs import LocalRequests, CloudRequests
from libs.Helpers import log_error_cloud
from datetime import datetime

def GetMyDB():
    db = LocalRequests.get_my_db()
    return db

cloud_link = "https://companywebapiendpoint.com/"


def login_to_cloud():
    headers = {
    "User-Agent": "user-companyname",
    "Connection": "keep-alive"
    }
    login_data = {
        "sender": "companyname-user",
        "username": "companyname",
        "password": "blower3mwireproducts"
    }
    result = requests.post(f"{cloud_link}/login", headers=headers, json=login_data, verify=True, allow_redirects=True)
    print(result)
    return result.json()


def check_cloud_changes():
    headers = {"User-Agent": "user-companyname", "Connection": "keep-alive"}
    data = {"sender" : "local_server", "request" : "check_changes"}
    access_data = login_to_cloud()
    if "access_token" in access_data:
        headers["Authorization"] = f"Bearer {access_data['access_token']}"
        http_result = requests.post(f"{cloud_link}/check-changes-1923ccxqw3m", headers=headers, json=data, verify=True, allow_redirects=True)
        result_data = http_result.json()
        return result_data

async def main():
    while True:
        await asyncio.sleep(15)
        try:
            changes_result = check_cloud_changes()

            if changes_result["status"] != "ok":
                print(f"ERROR: {changes_result['error_text']}")
                continue

            changes_list = changes_result["data_list"]

            for item in changes_list:
                print(item, type(item))


            if len(changes_list) == 0:
                print("No change detected on Cloud Server...")
                continue
            else:
                print("Changes detected on cloud server, attempting to sync...")
                for item in changes_list:
                    change_data = item["data"]
                    result = CloudRequests.Handle_Save_New_Changes_To_Database_Dictionary(change_data)

                    if len(result["failed"]) > 0:
                        today_file_name_format = datetime.today().strftime('%Y-%m-%d_%H:%M')
                        print("Changes detected, synchronization attempted.")
                        if len(result["failed"]) > 0:
                            log_path = f"logs/SyncFailCloudToLocal_{today_file_name_format}.json"
                            if os.path.isfile(log_path):
                                with open(log_path, "r", encoding="utf-8") as f:
                                    data = json.load(f)
                                data["failed_queries"] = []
                                for item in result["failed"]:
                                    data["failed_queries"].append(item)
                                with open(log_path, "w", encoding="utf-8") as f:
                                    json.dump(data, f, indent=4)
                            else:
                                data = {"failed_queries" : []}
                                for item in result["failed"]:
                                    data["failed_queries"].append(item)
                                with open(log_path, "w", encoding="utf-8") as f:
                                    json.dump(data, f, indent=4) 
        except Exception as error:
            print(f"ERROR: {error}")
            print(traceback.format_exc())
            log_error_cloud(str(error))
            continue

if __name__ == "__main__":
    asyncio.run(main())