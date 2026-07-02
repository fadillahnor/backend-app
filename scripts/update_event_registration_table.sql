-- SQL untuk menambahkan kolom baru ke tabel event_registrations
-- Jalankan ini di database MySQL yang digunakan aplikasi

ALTER TABLE event_registrations
  ADD COLUMN nama_bib varchar(100) NOT NULL AFTER email_peserta,
  ADD COLUMN alamat_peserta varchar(255) NOT NULL AFTER nohp_peserta,
  ADD COLUMN kota_peserta varchar(100) NOT NULL AFTER alamat_peserta,
  ADD COLUMN provinsi_peserta varchar(100) NOT NULL AFTER kota_peserta,
  ADD COLUMN tanggal_lahir varchar(20) NOT NULL AFTER provinsi_peserta,
  ADD COLUMN jenis_kelamin varchar(20) NOT NULL AFTER tanggal_lahir,
  ADD COLUMN scan_wajah varchar(255) DEFAULT NULL AFTER jenis_kelamin,
  ADD COLUMN ukuran_jersey varchar(50) NOT NULL AFTER scan_wajah,
  ADD COLUMN golongan_darah varchar(10) NOT NULL AFTER ukuran_jersey,
  ADD COLUMN nama_kontak_darurat varchar(100) NOT NULL AFTER golongan_darah,
  ADD COLUMN nomor_kontak_darurat varchar(20) NOT NULL AFTER nama_kontak_darurat,
  ADD COLUMN riwayat_penyakit text NULL AFTER nomor_kontak_darurat,
  ADD COLUMN pernyataan_sehat varchar(10) NOT NULL AFTER riwayat_penyakit;
