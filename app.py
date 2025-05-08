from flask import Flask, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
import json
import logging

# إعداد التسجيل (Logging)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# إعداد Google Drive API باستخدام Service Account
SCOPES = ['https://www.googleapis.com/auth/drive']

def get_drive_service():
    service_account_info = os.getenv('SERVICE_ACCOUNT_JSON')
    if not service_account_info:
        logger.error("SERVICE_ACCOUNT_JSON environment variable not set")
        raise ValueError("SERVICE_ACCOUNT_JSON environment variable not set")
    
    credentials_info = json.loads(service_account_info)
    credentials = service_account.Credentials.from_service_account_info(
        credentials_info, scopes=SCOPES)
    return build('drive', 'v3', credentials=credentials)

# الحصول على معرف المجلد (Folder ID) من Google Drive
def get_folder_id(drive_service, folder_name):
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = drive_service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    folders = results.get('files', [])
    logger.info(f"Looking for folder '{folder_name}': Found {len(folders)} folders")
    if not folders:
        logger.info(f"Folder '{folder_name}' not found, creating it...")
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = drive_service.files().create(body=file_metadata, fields='id').execute()
        logger.info(f"Created folder '{folder_name}' with ID: {folder.get('id')}")
        return folder.get('id')
    return folders[0].get('id')

@app.route('/getBooks', methods=['GET'])
def get_books():
    try:
        drive_service = get_drive_service()
        logger.info("Successfully initialized Google Drive service")

        # الحصول على معرفات المجلدات
        books_folder_id = get_folder_id(drive_service, 'AdanBooks')
        images_folder_id = get_folder_id(drive_service, 'AdanBooks/Images')
        logger.info(f"Books folder ID: {books_folder_id}, Images folder ID: {images_folder_id}")

        # جلب ملفات PDF من مجلد AdanBooks
        pdf_query = f"'{books_folder_id}' in parents and mimeType='application/pdf' and trashed=false"
        pdf_results = drive_service.files().list(q=pdf_query, spaces='drive', fields='files(id, name)').execute()
        pdf_files = pdf_results.get('files', [])
        logger.info(f"Found {len(pdf_files)} PDF files in AdanBooks: {[f['name'] for f in pdf_files]}")

        # جلب الصور من مجلد AdanBooks/Images
        image_query = f"'{images_folder_id}' in parents and (mimeType='image/jpeg' or mimeType='image/png') and trashed=false"
        image_results = drive_service.files().list(q=image_query, spaces='drive', fields='files(id, name)').execute()
        image_files = image_results.get('files', [])
        logger.info(f"Found {len(image_files)} image files in AdanBooks/Images: {[f['name'] for f in image_files]}")

        books = []
        images_url = 'https://drive.google.com/uc?export=download&id='
        books_url = 'https://drive.google.com/uc?export=download&id='

        # مطابقة ملفات PDF مع الصور بناءً على الاسم
        for pdf in pdf_files:
            book_name = pdf['name'].replace('.pdf', '').strip()  # إزالة الامتداد والمسافات
            logger.info(f"Processing PDF: {book_name}")
            # البحث عن صورة مطابقة بنفس الاسم
            matching_image = next(
                (img for img in image_files if img['name'].replace('.jpg', '').replace('.png', '').strip() == book_name),
                None
            )
            if matching_image:
                logger.info(f"Found matching image for {book_name}: {matching_image['name']}")
                books.append({
                    'Name': book_name,
                    'ImagePath': images_url + matching_image['id'],
                    'FileUrl': books_url + pdf['id']
                })
            else:
                logger.warning(f"No matching image found for {book_name}")

        logger.info(f"Returning {len(books)} books")
        return jsonify(books)

    except Exception as e:
        logger.error(f"Error in getBooks: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Welcome to Adan Books API. Use /getBooks to retrieve books."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
