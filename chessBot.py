import chess
import chess.engine
import os
import sys

class SatrancBotu:
    def __init__(self):
        self.tahta = chess.Board()
        self.oyuncu_rengi = None
        self.engine = None
        self.stockfish_yolu = None
        
    def stockfish_bul(self):
        """Stockfish motorunu bul veya yol iste"""
        # Yaygın Stockfish konumları
        olasi_yollar = [
            "stockfish",
            "/usr/bin/stockfish",
            "/usr/local/bin/stockfish",
            "C:\\Program Files\\Stockfish\\stockfish.exe",
            "C:\\stockfish\\stockfish.exe",
            "./stockfish",
            "./stockfish.exe",
        ]
        
        # Önce yaygın konumlarda ara
        for yol in olasi_yollar:
            try:
                engine = chess.engine.SimpleEngine.popen_uci(yol)
                engine.quit()
                self.stockfish_yolu = yol
                print(f"✓ Stockfish bulundu: {yol}")
                return True
            except:
                continue
        
        # Bulunamadıysa kullanıcıdan iste
        print("\n" + "=" * 60)
        print("⚠️  STOCKFISH MOTORU BULUNAMADI")
        print("=" * 60)
        print("\nStockfish indirmek için:")
        print("1. https://stockfishchess.org/download/ adresini ziyaret edin")
        print("2. İşletim sisteminiz için Stockfish'i indirin")
        print("3. Dosyayı çıkartın ve yolunu aşağıya girin")
        print("\nLinux/Mac: sudo apt install stockfish (veya brew install stockfish)")
        print("=" * 60)
        
        while True:
            yol = input("\nStockfish dosya yolunu girin (veya 'vazgeç' yazın): ").strip()
            
            if yol.lower() == 'vazgeç':
                print("\n❌ Stockfish olmadan bot çalışamaz. Çıkılıyor...")
                sys.exit(1)
            
            try:
                engine = chess.engine.SimpleEngine.popen_uci(yol)
                engine.quit()
                self.stockfish_yolu = yol
                print(f"\n✓ Stockfish başarıyla yüklendi!")
                return True
            except Exception as e:
                print(f"❌ Hata: {e}")
                print("Lütfen geçerli bir Stockfish yolu girin.")
    
    def motor_baslat(self):
        """Stockfish motorunu başlat"""
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(self.stockfish_yolu)
            # Motor ayarları - Maksimum güç
            self.engine.configure({"Skill Level": 20})  # Maksimum beceri
            self.engine.configure({"Threads": 4})  # Çoklu işlemci kullan
            self.engine.configure({"Hash": 256})  # Bellek kullanımı (MB)
            print("✓ Motor başlatıldı - Maksimum güç modu aktif!\n")
        except Exception as e:
            print(f"❌ Motor başlatma hatası: {e}")
            sys.exit(1)
    
    def baslat(self):
        print("=" * 60)
        print("STOCKFISH TABANLI PROFESYONEL SATRANÇ BOTU")
        print("=" * 60)
        
        # Stockfish'i bul ve başlat
        if not self.stockfish_bul():
            return
        self.motor_baslat()
        
        print("\nRakibinizin rengini seçin:")
        print("1. Beyaz (Rakip ilk oynar)")
        print("2. Siyah (Siz ilk oynarsınız)")
        
        while True:
            secim = input("\nSeçiminiz (1 veya 2): ").strip()
            if secim == "1":
                self.oyuncu_rengi = chess.BLACK
                print("\n✓ Siz SİYAH taşlarla oynuyorsunuz.")
                print("Rakibinizin ilk hamlesini girin...\n")
                break
            elif secim == "2":
                self.oyuncu_rengi = chess.WHITE
                print("\n✓ Siz BEYAZ taşlarla oynuyorsunuz.")
                print("İlk hamlenizi öneriyorum...\n")
                self.tahta_goster()
                self.en_iyi_hamle_bul()
                break
            else:
                print("Geçersiz seçim! Lütfen 1 veya 2 girin.")
    
    def tahta_goster(self):
        print("\n" + "=" * 60)
        print("MEVCUT TAHTA DURUMU:")
        print("=" * 60)
        print(self.tahta)
        print("=" * 60)
    
    def en_iyi_hamle_bul(self):
        """Stockfish ile en iyi hamleyi bul"""
        if self.tahta.is_game_over():
            self.oyun_bitti()
            return
        
        print("🤔 Stockfish analiz ediyor...")
        
        try:
            # Stockfish'ten hamle al
            # time: saniye cinsinden düşünme süresi (daha uzun = daha güçlü)
            sonuc = self.engine.play(self.tahta, chess.engine.Limit(time=2.0))
            en_iyi_hamle = sonuc.move
            
            # Opsiyonel: Pozisyon değerlendirmesi
            bilgi = self.engine.analyse(self.tahta, chess.engine.Limit(time=1.0))
            skor = bilgi["score"].relative
            
            print(f"\n✅ ÖNERİLEN HAMLE: {en_iyi_hamle}")
            print(f"   Stockfish değerlendirmesi: {skor}")
            
            # Hamleyi uygula
            self.tahta.push(en_iyi_hamle)
            self.tahta_goster()
            
            if self.tahta.is_checkmate():
                print("\n🎉 ŞAH MAT! KAZANDINIZ!")
                return
            elif self.tahta.is_check():
                print("\n⚠️  ŞAH!")
            
            if not self.tahta.is_game_over():
                print("\nRakibinizin hamlesini girin:")
                
        except Exception as e:
            print(f"❌ Motor hatası: {e}")
    
    def rakip_hamlesi_al(self):
        """Rakibin hamlesini al"""
        while True:
            hamle_str = input("\nRakip hamle (örn: e2e4) veya 'çık': ").strip().lower()
            
            if hamle_str == 'çık':
                print("Oyundan çıkılıyor...")
                return False
            
            if hamle_str == 'yardım':
                print("\nYasal hamleler:")
                for i, hamle in enumerate(list(self.tahta.legal_moves)[:20], 1):
                    print(f"{i}. {hamle}", end="  ")
                    if i % 5 == 0:
                        print()
                print("\n")
                continue
            
            try:
                hamle = chess.Move.from_uci(hamle_str)
                if hamle in self.tahta.legal_moves:
                    self.tahta.push(hamle)
                    self.tahta_goster()
                    
                    if self.tahta.is_checkmate():
                        print("\n💀 ŞAH MAT! Maalesef kaybettiniz.")
                        return False
                    elif self.tahta.is_check():
                        print("\n⚠️  ŞAH! Kral tehdit altında!")
                    
                    return True
                else:
                    print("❌ Geçersiz hamle! 'yardım' yazarak yasal hamleleri görebilirsiniz.")
            except:
                print("❌ Hatalı format! Hamleyi 'e2e4' formatında girin.")
    
    def oyun_bitti(self):
        """Oyun sonu durumu"""
        if self.tahta.is_checkmate():
            if self.tahta.turn == self.oyuncu_rengi:
                print("\n💀 ŞAH MAT! Maalesef kaybettiniz.")
            else:
                print("\n🎉 ŞAH MAT! KAZANDINIZ!")
        elif self.tahta.is_stalemate():
            print("\n🤝 PAT! Oyun berabere.")
        elif self.tahta.is_insufficient_material():
            print("\n🤝 Yetersiz malzeme! Oyun berabere.")
        elif self.tahta.is_fifty_moves():
            print("\n🤝 50 hamle kuralı! Oyun berabere.")
        elif self.tahta.is_repetition():
            print("\n🤝 Pozisyon tekrarı! Oyun berabere.")
    
    def oyna(self):
        """Ana oyun döngüsü"""
        self.baslat()
        
        try:
            while not self.tahta.is_game_over():
                if self.tahta.turn == self.oyuncu_rengi:
                    self.en_iyi_hamle_bul()
                else:
                    if not self.rakip_hamlesi_al():
                        break
            
            if self.tahta.is_game_over():
                self.oyun_bitti()
        finally:
            # Motoru kapat
            if self.engine:
                self.engine.quit()
                print("\n✓ Motor kapatıldı.")
        
        print("\n" + "=" * 60)
        print("Oyun bitti! Tekrar oynamak için programı çalıştırın.")
        print("=" * 60)


if __name__ == "__main__":
    bot = SatrancBotu()
    bot.oyna()