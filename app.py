from flask import Flask, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

app = Flask(__name__)

# إعداد Google Drive API باستخدام Service Account
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'service_account.json'  # مسار ملف Service Account JSON

def get_drive_service():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('drive', 'v3', credentials=credentials)

# الحصول على معرف المجلد (Folder ID) من Google Drive
def get_folder_id(drive_service, folder_name):
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
    results = drive_service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    folders = results.get('files', [])
    if not folders:
        # إنشاء المجلد إذا لم يكن موجودًا
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = drive_service.files().create(body=file_metadata, fields='id').execute()
        return folder.get('id')
    return folders[0].get('id')

@app.route('/getBooks', methods=['GET'])
def get_books():
    drive_service = get_drive_service()

    # الحصول على معرفات المجلدات
    books_folder_id = get_folder_id(drive_service, 'AdanBooks')
    images_folder_id = get_folder_id(drive_service, 'AdanBooks/Images')

    # جلب ملفات PDF من مجلد AdanBooks
    pdf_query = f"'{books_folder_id}' in parents and mimeType='application/pdf'"
    pdf_results = drive_service.files().list(q=pdf_query, spaces='drive', fields='files(id, name)').execute()
    pdf_files = pdf_results.get('files', [])

    # جلب الصور من مجلد AdanBooks/Images
    image_query = f"'{images_folder_id}' in parents and (mimeType='image/jpeg' or mimeType='image/png')"
    image_results = drive_service.files().list(q=image_query, spaces='drive', fields='files(id, name)').execute()
    image_files = image_results.get('files', [])

    books = []
    images_url = 'https://drive.google.com/uc?export=download&id='
    books_url = 'https://drive.google.com/uc?export=download&id='

    # مطابقة ملفات PDF مع الصور بناءً على الاسم
    for pdf in pdf_files:
        book_name = pdf['name'].replace('.pdf', '')  # إزالة امتداد .pdf
        # البحث عن صورة مطابقة بنفس الاسم
        matching_image = next((img for img in image_files if img['name'].replace('.jpg', '').replace('.png', '') == book_name), None)
        
        if matching_image:
            books.append({
                'Name': book_name,
                'ImagePath': images_url + matching_image['id'],
                'FileUrl': books_url + pdf['id']
            })

    return jsonify(books)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
