from app.app.gdrive_connector import GDriveConnector
import os

def main():
    g = GDriveConnector()
    folder_id = g.create_folder("database")
    print(folder_id)
    for file in os.listdir(f"./database"):
        print(file)
        g.upload_file(file, f"database/{file}", parents=[folder_id])

if __name__ == "__main__":
    main()