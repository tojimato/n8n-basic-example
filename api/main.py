"""
Mock CRM API — n8n W21 Demo
Kaynak: aforsoft.com/blog/2026-ai-stack-rehberi-n8n-ile-akilli-is-akisi-529

Bu servis n8n akışının HTTP Request node'undan gelen kayıtları alır ve
in-memory listede tutar. Gerçek projede burada bir veritabanı olur.

Endpoint'ler:
  POST /crm/kayit      → Yeni müşteri kaydı oluştur
  GET  /crm/kayitlar   → Tüm kayıtları listele
  GET  /health         → Servis sağlık kontrolü
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
import uvicorn

# ---------------------------------------------------------------------------
# UYGULAMA
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Mock CRM API",
    description="n8n W21 örneği için sahte CRM servisi. "
                "Gelen müşteri taleplerini bellekte saklar.",
    version="1.0.0",
)

# In-memory kayıt deposu (process yeniden başladığında sıfırlanır)
kayitlar: list[dict] = []


# ---------------------------------------------------------------------------
# VERİ MODELLERİ
# ---------------------------------------------------------------------------

class MusteriTalep(BaseModel):
    """
    n8n'deki Code node'unun ürettiği CRM formatına uygun model.
    Alan adları birebir eşleşmeli.
    """
    isim:   str
    email:  str               # Gerçek projede EmailStr kullanılabilir
    sirket: str
    tur:    str               # 'satis' veya 'destek'
    tarih:  Optional[str] = None


class KayitYanit(BaseModel):
    basarili:   bool
    kayit_id:   int
    mesaj:      str
    kayit:      dict


# ---------------------------------------------------------------------------
# ENDPOINT'LER
# ---------------------------------------------------------------------------

@app.post(
    "/crm/kayit",
    response_model=KayitYanit,
    summary="Yeni müşteri talebi oluştur",
)
async def kayit_olustur(talep: MusteriTalep):
    """
    n8n'deki HTTP Request node'u bu endpoint'e POST isteği atar.
    Kayıt oluşturulur, ID ve oluşturma zamanı eklenerek döner.
    """
    yeni_kayit = talep.model_dump()
    yeni_kayit["id"]           = len(kayitlar) + 1
    yeni_kayit["olusturulma"]  = datetime.now().isoformat()

    # Eğer n8n tarih gönderdiyse koru, göndermemişse şimdiki zamanı yaz
    if not yeni_kayit.get("tarih"):
        yeni_kayit["tarih"] = yeni_kayit["olusturulma"]

    kayitlar.append(yeni_kayit)

    return KayitYanit(
        basarili  = True,
        kayit_id  = yeni_kayit["id"],
        mesaj     = f"Kayıt #{yeni_kayit['id']} oluşturuldu.",
        kayit     = yeni_kayit,
    )


@app.get(
    "/crm/kayitlar",
    summary="Tüm kayıtları listele",
)
async def kayitlari_listele():
    """
    Tarayıcıdan http://localhost:8000/crm/kayitlar ile kontrol edilebilir.
    """
    return {
        "toplam":   len(kayitlar),
        "kayitlar": kayitlar,
    }


@app.delete(
    "/crm/kayitlar",
    summary="Tüm kayıtları temizle (test kolaylığı için)",
)
async def kayitlari_temizle():
    kayitlar.clear()
    return {"mesaj": "Tüm kayıtlar silindi."}


@app.get("/health", summary="Servis sağlık kontrolü")
async def saglik():
    return {"durum": "calisiyor", "kayit_sayisi": len(kayitlar)}


# ---------------------------------------------------------------------------
# GELİŞTİRME SUNUCUSU (docker dışında doğrudan çalıştırma için)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
