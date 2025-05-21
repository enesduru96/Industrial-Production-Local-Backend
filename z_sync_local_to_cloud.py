
import traceback, json, asyncio, requests, os
from libs import LocalRequests, CloudRequests, Utilities
from libs.Helpers import ScaleMaterialMapper, log_error_cloud
from datetime import datetime


def get_my_db():
    db = LocalRequests.get_my_db()
    return db

cloud_link = "https://companyapiendpoint.com/"

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

def sync_changes_to_cloud():
    headers = {"User-Agent": "user-companyname", "Connection": "keep-alive"}
    try:
        db = get_my_db()
        cursor = db.cursor()
        sql_getstring = "SELECT * FROM z_cloud_tasks WHERE is_completed = %s"
        cursor.execute(sql_getstring, (False, ))
        found_records = cursor.fetchall()
        if len(found_records) == 0:
            return {
                "status" : "no_change"
            }
        
        access_data = login_to_cloud()
        if "access_token" in access_data:
            headers["Authorization"] = f"Bearer {access_data['access_token']}"

        total_change_list = []

        row_ids = []
        for row in found_records:
            row_ids.append(row[0])
            new_data = json.loads(row[1])
            total_change_list.append(new_data)
        

        data = {"sender" : "local_server", "request" : "sync_changes", "data_sent": total_change_list}
        http_result = requests.post(f"{cloud_link}/save-changes-1923ccxqw3m", headers=headers, json=data, verify=True, allow_redirects=True)
        result_data = http_result.json()


        for id in row_ids:
            sql_updatestring = f"UPDATE z_cloud_tasks SET is_completed=%s WHERE id = %s"
            cursor.execute(sql_updatestring, (1,id))
            db.commit()

        cursor.close()
        db.close()
        return result_data
    
    except Exception as error:
        print(error)
        print(traceback.format_exc())
        log_error_cloud(str(error))

        return {
            "status": "error",
            "error_text": str(error)
        }

async def main():
    while True:
        await asyncio.sleep(15)
        try:
            changes_result = sync_changes_to_cloud()
            if changes_result["status"] == "error":
                print(f"ERROR: {changes_result['error_text']}")
                continue
            
            elif changes_result["status"] == "no_change":
                print("No change detected...")
                continue
            
            else:
                today_file_name_format = datetime.today().strftime('%Y-%m-%d_%H:%M')
                print("Changes detected, synchronization attempted.")
                if len(changes_result["failed"]) > 0:
                    log_path = f"logs/SyncFailLocalToCloud_{today_file_name_format}.json"
                    if os.path.isfile(log_path):
                        with open(log_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        data["failed_queries"] = []
                        for item in changes_result["failed"]:
                            data["failed_queries"].append(item)
                        with open(log_path, "w", encoding="utf-8") as f:
                            json.dump(data, f, indent=4)
                    else:
                        data = {"failed_queries" : []}
                        for item in changes_result["failed"]:
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