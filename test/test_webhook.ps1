# test_webhook.ps1
# ──────────────────────────────────────────────────────────────────────────
# n8n müşteri talep workflow'unu test eder.
# Kullanım: .\test_webhook.ps1
# ──────────────────────────────────────────────────────────────────────────

$webhookUrl = "http://localhost:5678/webhook/musteri-talep"
$crmListUrl = "http://localhost:8000/crm/kayitlar"

$payload = @{
    isim   = "Ayse Yilmaz"
    email  = "ayse@ornek.com"
    sirket = "ABC Ltd."
    talep  = "demo talebi"
} | ConvertTo-Json -Depth 3

Write-Host ""
Write-Host "=== N8N WEBHOOK TEST ===" -ForegroundColor Cyan
Write-Host "Hedef: $webhookUrl"
Write-Host "Payload:" -ForegroundColor Yellow
Write-Host $payload
Write-Host ""

try {
    $yanit = Invoke-RestMethod `
        -Uri $webhookUrl `
        -Method POST `
        -ContentType "application/json; charset=utf-8" `
        -Body ([System.Text.Encoding]::UTF8.GetBytes($payload))

    Write-Host "=== WEBHOOK YANITI ===" -ForegroundColor Green
    $yanit | ConvertTo-Json -Depth 5 | Write-Host
}
catch {
    Write-Host "HATA: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "n8n calisiyor mu? http://localhost:5678" -ForegroundColor Yellow
    Write-Host "Workflow aktif mi? (n8n arayuzunden 'Active' tikini kontrol et)" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "=== CRM KAYITLARI ===" -ForegroundColor Cyan
Write-Host "Hedef: $crmListUrl"

try {
    $kayitlar = Invoke-RestMethod -Uri $crmListUrl -Method GET
    Write-Host "Toplam kayit: $($kayitlar.toplam)" -ForegroundColor Green
    $kayitlar.kayitlar | ConvertTo-Json -Depth 5 | Write-Host
}
catch {
    Write-Host "CRM API'ye ulasılamadı: $_" -ForegroundColor Red
}
