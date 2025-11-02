import os
import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from datetime import datetime
from app.core.security import user_auth

router = APIRouter()

# Konfigurasi Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

MAX_FILE_SIZE_MB = 5  # batas maksimum 5 MB

@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...), _ = Depends(user_auth)):
    try:
        # Validasi ukuran file
        contents = await file.read()
        file_size_mb = len(contents) / (1024 * 1024)
        if file_size_mb > MAX_FILE_SIZE_MB:
            raise HTTPException(
                status_code=400,
                detail=f"Ukuran file terlalu besar ({file_size_mb:.2f} MB). Maksimal {MAX_FILE_SIZE_MB} MB diperbolehkan."
            )

        # Upload ke Cloudinary
        result = cloudinary.uploader.upload(
            contents,
            folder="uploads",  # opsional: folder di cloudinary
            public_id=f"{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}",  # nama unik
            resource_type="image"
        )

        # Ambil URL hasil upload
        image_url = result.get("secure_url")
        if not image_url:
            raise HTTPException(status_code=500, detail="Gagal mendapatkan URL gambar dari Cloudinary")

        # Response sukses
        return JSONResponse(
            content={
                "status": "success",
                "message": "Gambar berhasil diunggah.",
                "image_url": image_url
            },
            status_code=200
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload gagal: {str(e)}")
