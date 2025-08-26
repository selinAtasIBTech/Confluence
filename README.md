# Confluence Sayfa İçeriklerinin Otomatik Dışa Aktarımı

Amaç: IBTech Confluence (Data Center) ortamındaki bir sayfanın ve tüm alt sayfalarının içeriklerini, otomatik şekilde .txt dosyalarına dönüştürüp klasör yapısında dışa aktarmak.

Yapılan Adımlar ve Teknik Uygulama
1. Sayfa ID’sinin Alınması
Bireysel Krediler Wiki ve benzeri sayfalar için sayfa ID’si Bruno aracı üzerinden REST API kullanılarak alındı.

API endpoint:

GET /rest/api/content?title=<Sayfa Adı>&spaceKey=<Alan Kodu>

2. Python Script Hazırlığı
Aşağıdaki amaçlarla çalışan bir Python script geliştirildi:

Confluence API’ye bağlanarak verilen root sayfanın altındaki tüm sayfaları recursive olarak çekmek

HTML içerikleri sadeleştirerek .txt formatına dönüştürmek

Her sayfa için özel klasör ve dosya yapısı oluşturmak

Kullanılan Kütüphaneler:
urllib.request: API'den veri çekmek

json: JSON veri işlemek

os: Dosya ve klasör işlemleri

re: Metin temizleme (regex)

unicodedata: Türkçe karakterleri ASCII’ye çevirmek

html.unescape: HTML entity’leri temizlemek

3. .env ile Güvenli Kimlik Doğrulama
API token .env dosyasına alındı.

Script bu dosyadan token’ı okuyarak kimlik doğrulama sağladı.

Token dışarıdan alınarak güvenli hale getirildi.

4. Dosya ve Klasör İsimlendirme Stratejisi
Tüm dosya/klasör isimleri sanitize_name() fonksiyonu ile Windows’a uyumlu hale getirildi.

Türkçe karakterler (ç, ğ, ü) dönüştürüldü.

Yasak karakterler (\, /, :, *, ?, <, >, |, .) temizlendi.

Uzun isimler 30 karakter ile sınırlandırıldı.

Klasör ismi: page_<id>__<temizlenmiş_başlık>

Dosya ismi: content_<id>.txt

5. Recursive Klasör Yapısı
Ana sayfa altında tüm alt sayfalar için klasör oluşturuldu.

Her klasöre ait içerik .txt formatında kaydedildi.

Derinlik sınırsız şekilde tüm alt sayfalar gezildi.

6. Karşılaşılan Problemler ve Çözümler


FileNotFoundError	Path uzunluğu Windows sınırını aştı	\\?\ prefixi kullanıldı
smg.. gibi klasör isimleri	. ile biten veya sadece .. gibi tehlikeli isimler	. karakteri temizlendi
Aynı isimde dosya/klasör çakışması	Başlık tekrarlandığında sorun çıkıyordu	Dosya adı sadece id olarak verildi
Örnek Çıktı Yapısı
bireysel_krediler_wiki_98305/
├── page_123456__giris_maili/
│   └── content_123456.txt
├── page_123457__baglantilar/
│   └── content_123457.txt

Her .txt dosyası içinde:

Sayfa başlığı

HTML'den arındırılmış düz metin içerik yer aldı

Kazanımlar
Confluence verilerinin manuel kopyalama ihtiyacı ortadan kalktı

Kapsamlı klasörleme ile belge arşivleme kolaylaştı

Dosya adlandırması, sistem uyumluluğu ve güvenli API kullanımı öğrenildi
