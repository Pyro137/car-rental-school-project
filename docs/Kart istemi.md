# Kart istemi: dosya ve terminal erişimli yapay zekâ araçları için

Bu istem bir görev kartını yapay zekâ aracına baştan sona yaptırmak içindir: dal açma, kod, test, kabul kontrolü ve yerel commit. Dosya okuyup komut çalıştırabilen araçlarda kullanılır (Claude Code, Cursor, Copilot agent modu, Codex). Dosyaları elle yapıştırdığın sohbet araçlarında (ChatGPT, Gemini web) `AGENTS.md` 10. bölümdeki cevap biçimi geçerlidir.

**Nasıl kullanılır**

1. Güncel koda geç ve veritabanını aç: `git switch main`, `git pull`, Docker Desktop'ı başlat.
2. Aşağıdaki "İstem" bölümünün tamamını kopyala, en alttaki alanları doldur ve aracına yapıştır.
3. Araç bitirince raporu oku, değişikliği VS Code'un Source Control sekmesinde satır satır incele ve kabul kontrolünü tarayıcıda kendin dene. Push ve PR senin işindir.

---

## İstem

Bu projede bir görev kartını uyguluyorsun. Dosyaları okuyup yazabilir ve terminalde komut çalıştırabilirsin. Kartı baştan sona sen yaparsın: dal, kod, test, kabul kontrolü ve yerel commit. Push ve pull request öğrencinin işidir. Öğrenciye her açıklamayı Türkçe yap; kod, yorum, arayüz metni ve commit mesajı İngilizce olur.

### 1. Önce oku

1. Proje kökündeki `AGENTS.md` dosyasını baştan sona oku. Bu istemle çelişen bir yer varsa `AGENTS.md` geçerlidir.
2. Kartı oku. Kart aşağıya yapıştırılmadıysa `docs/` altındaki "Kartlar Milestone N" dosyasından al. Yapıştırılan kart repodaki kopyadan farklıysa dur ve hangisinin geçerli olduğunu sor.
3. Kartın atıf yaptığı "Milestone N adım adım" bölümünü oku. Orada kod varsa test edilmiş referans odur: aynen kullan, yalnız dokümanın boş bıraktığı yerleri sen yaz.
4. Kartın "Yapay zekâya ver" satırındaki dosyaları ve örnek gösterilen dosyaları repodan kendin oku; öğrenciden yapıştırmasını isteme. Repoda olmayan bir alan, fonksiyon, rota, fixture ya da şablon bloğu uydurma.
5. Yeni kodu referans dilime benzet: `app/routers/cars.py`, `app/services/cars.py`, `app/templates/cars/list.html`, `app/routers/auth.py`, `app/templates/auth/`, `tests/test_cars.py`, `tests/test_auth.py`.

### 2. Başlamadan kontrol et

1. `git status` temiz olmalı. Değilse dur ve sor; öğrencinin kaydedilmemiş işinin üstüne yazma.
2. Kartın "Bağımlı" satırındaki kartlar `main`'de olmalı (`git log main --oneline` içinde kart numarasıyla başlayan commit). Değilse dur ve söyle. Öğrenci açıkça "şu dalın üstüne kur" demedikçe başka bir dalın üstüne kurma.
3. Veritabanını `docker compose up -d` ile başlat. Docker çalışmıyorsa öğrenciden Docker Desktop'ı açmasını iste.
4. Türkçe 2-4 cümlelik bir plan yaz: ne yapacağını ve değiştireceğin dosyaların tam listesini söyle. Liste kartın "Dosyalar" satırıyla birebir aynı olmalı. Sonra beklemeden devam et; yalnız 4. bölümdeki durumlarda dur.

### 3. Uygula

1. `main`'den dal aç: `git switch -c <kart-no>-<kısa-ad>`, örneğin `1.8a-fleet-service`.
2. Yalnız kartın "Dosyalar" satırındaki dosyaları oluştur ya da değiştir. Başka bir dosyada hata ya da iyileştirme görürsen dokunma; raporda "Açık noktalar"a yaz.
3. En basit doğru kodu yaz; öğrenci her satırı açıklayabilmeli. Yeni paket ekleme.
4. Kartta test dosyası varsa kartın saydığı her testi yaz ve `AGENTS.md` 7. bölüme uy: her yeni service fonksiyonu için normal durum ve uyguladığı her kural için bir test; tarihler `date.today()`'e göre; `client` isteklerinden sonra `db` ile okumadan önce `db.expire_all()`.
5. Kart bir işi açıkça insana veriyorsa (kendin say, kendin çiz, kaynağı kendin aç ve oku, kendi cümlelerinle yaz) o işi yapma ve raporda öğrencinin yapacakları arasına koy. Kaynak, makale ya da künye önermek de bu kapsamdadır.

### 4. Dur ve sor

Aşağıdakilerden biri olursa çalışmayı durdur, durumu Türkçe açıkla ve etrafından dolanma:

- Kart `AGENTS.md` ile çelişiyor.
- Kart, "Dosyalar"da olmayan bir dosyaya dokunmadan yapılamıyor. "Metin only" dosyalar özellikle önemlidir: `app/main.py`, `app/config.py`, `app/db.py`, `app/models.py`, `app/deps.py`, `app/templates/base.html`, `tests/conftest.py`.
- Yeni bir paket gerekiyor.
- Bağımlı kart `main`'de değil ya da gereken bir bilgi repoda yok.

### 5. Doğrula

1. Proje kökünde sırayla çalıştır: `uv run ruff format .`, `uv run ruff check --fix .`, `uv run pytest`. Üçü de temiz olmadan commit etme. Ruff kartın dışındaki bir dosyayı değiştirdiyse o değişikliği geri al ve raporda belirt.
2. Kartın "Kabul" maddelerini tek tek doğrula. Kartın kendi testleriyle kapsanmayan bir madde için:
   - Geçici test yaz ama repoya koyma: repo dışındaki geçici bir klasöre yaz ve `PYTHONPATH=. uv run pytest -q -p tests.conftest <klasör>` ile çalıştır. PowerShell'de önce `$env:PYTHONPATH = "."` yazılır. Bu fixture'lar test veritabanını kullanır.
   - Gerçek uygulamayı dene: `uv run uvicorn app.main:app --port 8765` komutunu arka planda başlat ve sayfaları `curl` ile iste. Bitince sunucuyu durdur.
   - Geliştirme veritabanına deneme verisi eklediysen sil.
3. Göremediğin şeyleri (görünüm, harita, tarayıcı davranışı) "doğrulanmadı, tarayıcıda denenmeli" diye raporla. Denemediğin bir şeye "çalışıyor" deme.

### 6. Commit

- Yalnız kartın dosyalarını ekle: `git add <dosya> <dosya>`. `git add -A` kullanma; `.env` asla commit edilmez.
- Mesaj: `<kart-no>: <emir kipinde İngilizce cümle>`, örneğin `1.8a: Add fleet service`.
- Push etme, PR açma, `main`'e dokunma. Öğrenci açıkça isterse yaparsın.

### 7. Rapor

Bitince Türkçe ve bu sırayla raporla:

1. **Özet:** kart bitti mi, dalın adı ne, commit edildi mi; bir iki cümle.
2. **Dosyalar:** her dosya tıklanabilir bir bağlantı ve yanında ne yaptığını söyleyen bir cümle. Dosyalar diskte olduğu için içeriklerini rapora kopyalama.
3. **Doğrulama:** ruff ve pytest sonucu (kaç test geçti) ve her "Kabul" maddesinin nasıl denendiği ve sonucu. Geçmeyen ya da denenemeyen maddeyi açıkça yaz.
4. **Açıklama:** yeni başlayan biri için her yeni fonksiyonun ya da şablon parçasının ne yaptığı ve neden böyle yazıldığı. Kodu şekillendiren `AGENTS.md` kuralını adıyla an.
5. **Açık noktalar:** dokümandan ya da karttan sapmalar, varsayımlar, fark edip dokunmadığın sorunlar. Yoksa "Yok" yaz.
6. **Senin yapacakların:**
   - Değişikliği VS Code'un Source Control sekmesinde ya da `git diff main` ile satır satır incele.
   - Kabul kontrolünü tarayıcıda kendin dene.
   - `git push -u origin <dal>` ile gönder, GitHub'da "Compare & pull request" ile PR aç ve şablonu doldur.
   - "Anlama soruları"nı kendi cümlelerinle yaz.
   - "Yapay zekâ" bölümüne hangi aracı kullandığını ve çıktıda elle neyi değiştirdiğini yaz.
   - Kartın sana bıraktığı insan işleri (varsa).

### 8. Anlama soruları

Kartın "Anlama soruları"nı öğrencinin yerine cevaplama ve PR açıklamasına yazma. Öğrenci sorarsa ipucu ver ve ilgili dosyayı ve satırı göster; cevabı öğrenci kendi cümleleriyle yazar.

### Kart

- **Kart numarası:**
- **Öğrenci:**
- **Ek not (isteğe bağlı):**
- **Kart metni (isteğe bağlı; boşsa `docs/` altından okunur):**
