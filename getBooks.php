<?php
header('Content-Type: application/json');

// URLs لروابط Google Drive
$imagesUrl = 'https://drive.google.com/uc?export=download&id=';
$booksUrl = 'https://drive.google.com/uc?export=download&id=';

// قائمة الكتب
$bookList = [
    [
        'Name' => 'Book1',
        'ImageId' => '<Google_Drive_Image_File_ID>',
        'FileId' => '<Google_Drive_PDF_File_ID>'
    ],
    // أضف كتبًا أخرى هنا
];

$books = [];
foreach ($bookList as $book) {
    $books[] = [
        'Name' => $book['Name'],
        'ImagePath' => $imagesUrl . $book['ImageId'],
        'FileUrl' => $booksUrl . $book['FileId']
    ];
}

// إرجاع استجابة JSON
echo json_encode($books);
?>