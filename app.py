from flask import Flask, jsonify

app = Flask(__name__)

# قائمة الكتب
book_list = [
    {
        'Name': 'Book1',
        'ImageId': '<Google_Drive_Image_File_ID>',
        'FileId': '<Google_Drive_PDF_File_ID>'
    },
    # أضف كتبًا أخرى هنا
]

# URLs لروابط Google Drive
images_url = 'https://drive.google.com/uc?export=download&id='
books_url = 'https://drive.google.com/uc?export=download&id='

@app.route('/getBooks', methods=['GET'])
def get_books():
    books = [
        {
            'Name': book['Name'],
            'ImagePath': images_url + book['ImageId'],
            'FileUrl': books_url + book['FileId']
        }
        for book in book_list
    ]
    return jsonify(books)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)