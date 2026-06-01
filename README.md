# n8n Müşteri Talep Akışı — Demo

Aforsoft [W21 blog yazısındaki](https://aforsoft.com/blog/n8n-ile-kod-yazmadan-akilli-is-akisi-nasil-kurulur-530) n8n workflow örneğinin çalıştırılabilir versiyonu.

## Akış

```
[POST /webhook/musteri-talep]
        ↓
[Code Node — CRM formatına çevir]
        ↓
[HTTP Request — Mock CRM API'ye kaydet]
        ↓
[Respond — Webhook'a JSON yanıt döndür]
```

## Proje Yapısı

```
ExampleN8n/
├── docker-compose.yml          # n8n + Mock CRM API
├── .env.example                # Ortam değişkeni şablonu
├── api/
│   ├── Dockerfile
│   ├── main.py                 # FastAPI mock CRM servisi
│   └── requirements.txt
├── workflow/
│   └── musteri-talep-akisi.json   # n8n'e import edilecek akış
├── test/
│   └── test_webhook.ps1        # Test scripti (PowerShell)
└── README.md
```

---

## Kurulum ve Başlatma

### 1. .env dosyasını oluştur

```powershell
Copy-Item .env.example .env
```

`.env` dosyasını aç ve `N8N_ENCRYPTION_KEY` değerini değiştir (en az 32 karakter).

### 2. Servisleri başlat

```powershell
docker compose up -d --build
```

İlk başlatmada Docker image'ları indirilir (~2–3 dakika).

### 3. Servislerin hazır olduğunu kontrol et

```powershell
docker compose ps
```

Her iki servis de `running` durumunda olmalı.

| Servis | URL |
|---|---|
| n8n arayüzü | http://localhost:5678 |
| Mock CRM API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |

---

## Workflow'u İçe Aktar

1. http://localhost:5678 adresini aç
2. İlk açılışta kullanıcı adı/şifre oluştur
3. Sol menü → **Workflows** → **Add Workflow** → **Import from File**
4. `workflow/musteri-talep-akisi.json` dosyasını seç
5. Workflow açıldıktan sonra sağ üstteki toggle ile **Active** yap

> ⚠️ Workflow **Active** olmadan webhook URL'si test edilemez.

---

## Test

### PowerShell ile (önerilen)

```powershell
.\test\test_webhook.ps1
```

### Manuel (Invoke-RestMethod)

```powershell
$body = '{"isim":"Ayse Yilmaz","email":"ayse@ornek.com","sirket":"ABC Ltd.","talep":"demo talebi"}'

Invoke-RestMethod `
  -Uri "http://localhost:5678/webhook/musteri-talep" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

### Beklenen webhook yanıtı

```json
{
  "basarili": true,
  "kayit_id": 1,
  "mesaj": "Kayıt #1 oluşturuldu."
}
```

### CRM kayıtlarını kontrol et

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/crm/kayitlar"
```

veya tarayıcıdan: http://localhost:8000/crm/kayitlar

---

## n8n Akışında Node Detayları

### 1. Webhook Node
- **Method:** POST
- **Path:** `musteri-talep`
- **Response Mode:** Using Respond to Webhook Node
- **Test URL:** `http://localhost:5678/webhook-test/musteri-talep`
- **Canlı URL:** `http://localhost:5678/webhook/musteri-talep`

> Akış pasifken test URL'si, aktifken canlı URL çalışır.

### 2. Code Node (JavaScript)

```javascript
const veri = $input.first().json;

return {
  json: {
    isim:   veri.isim,
    email:  veri.email,
    sirket: veri.sirket,
    tur:    veri.talep === 'demo talebi' ? 'satis' : 'destek',
    tarih:  new Date().toISOString()
  }
};
```

### 3. HTTP Request Node
- **Method:** POST
- **URL:** `http://api:8000/crm/kayit`
  - `api` → Docker ağındaki servis adı (dışarıdan `localhost:8000` ile erişilir)
- **Body:** JSON — Code node çıktısı

### 4. Respond to Webhook Node
- Webhook'a `{ basarili, kayit_id, mesaj }` döner

---

## Servisleri Durdur

```powershell
docker compose down
```

n8n verilerini de sıfırlamak için:

```powershell
docker compose down -v
```

---

## Kaynaklar

- [n8n Resmi Dokümantasyon](https://docs.n8n.io)
- [Aforsoft W21 — n8n Blog Yazısı](https://aforsoft.com/blog/n8n-ile-kod-yazmadan-akilli-is-akisi-nasil-kurulur-530)
- [Aforsoft 2026 AI Haritası](https://aforsoft.com/blog/2026-ai-haritasi-agentlardan-idelere-hangi-araci-nerede-kullanmalisiniz-527)
