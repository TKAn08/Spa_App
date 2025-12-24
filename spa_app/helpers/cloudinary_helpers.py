import cloudinary.uploader
def import_to_cloudinary(file):
    if not file or file.filename == "":
        return None
    try:
        res = cloudinary.uploader.upload(file)
        return res.get('secure_url')
    except Exception as e:
        print("Lỗi tải lên:", e)
        return None
