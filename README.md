# SHRI-Upload-Assistant-GUI
Interfaccia grafica per Audionut Upload-Assistant

Uno strumento semplice per semplificare il lavoro di upload.

Questo progetto è una GUI basata sul lavoro originale di Audionut https://github.com/Audionut/Upload-Assistant
Un ringraziamento speciale a lui per aver creato questo progetto.

## Cosa può fare:
  - Genera e analizza MediaInfo/BDInfo.
  - Genera e carica screenshot. Tonemapping HDR se configurato.
  - Usa srrdb per correggere i nomi scena usati nei siti.
  - Può recuperare descrizioni da PTP/BLU/Aither/LST/OE/BHD (automaticamente su match del nome file o tramite argomento).
  - Può estrarre e riutilizzare screenshot già presenti nelle descrizioni per saltare la generazione e l'upload.
  - Ottiene identificatori TMDb/IMDb/MAL/TVDB/TVMAZE.
  - Converte la numerazione assoluta in stagioni/episodi per Anime. Supporto Non-Anime con credenziali TVDB.
  - Genera .torrent personalizzati senza cartelle/nfo inutili.
  - Può riutilizzare torrent esistenti invece di crearne di nuovi.
  - Può cercare automaticamente nei client qBitTorrent (versione 5+) torrent già esistenti.
  - Genera il nome corretto per l'upload usando Mediainfo/BDInfo e TMDb/IMDb conforme alle regole del sito.
  - Controlla se il rilascio è già presente sul sito.
  - Aggiunge al client con resume veloce, seed immediato (rtorrent/qbittorrent/deluge/watch folder).
  - TUTTO CON INPUT MINIMO!
  - Attualmente funziona con .mkv/.mp4/Blu-ray/DVD/HD-DVDs.

## Siti supportati:

ShareIsland

## **Setup:**
   - **RICHIEDE ALMENO PYTHON 3.9 E PIP3**
   - Ottieni il codice sorgente:
      - Clona la repo sul tuo sistema `git clone https://github.com/tiberio87/SHRI-Upload-Assistant-GUI`
      - oppure scarica lo zip dalla pagina dei rilasci e crea/sovrascrivi una copia locale.
      - Modifica `api_keys.json` con i tuoi dati
      - Installa l'ambiente virtuale python `python -m venv .venv`
      - Attiva l'ambiente virtuale `.venv\Scripts\activate`
      - Installa i moduli python necessari `pip install -r requirements.txt`
   - Modifica (se necessario) `config.py` con i tuoi dati
      - La chiave tmdb_api si ottiene da https://www.themoviedb.org/settings/api
      - Le chiavi API degli host immagini si ottengono dai rispettivi siti

   **Risorse aggiuntive disponibili nella [wiki](https://github.com/Audionut/Upload-Assistant/wiki)**

   Contattami pure se hai bisogno di aiuto, non sono difficile da trovare.

## **Aggiornamenti:**
  - Per aggiornare il BOT premi il pulsante verde "Controlla aggiornamenti BOT"
  - Per aggiornare i moduli premi il pulsante verde "Controlla aggiornamenti dipendenze"

## **Attribuzioni:**

Realizzato con BDInfoCLI aggiornato da https://github.com/rokibhasansagar/BDInfoCLI-ng

<p>
  <a href="https://github.com/autobrr/mkbrr"><img src="https://github.com/autobrr/mkbrr/blob/main/.github/assets/mkbrr-dark.png?raw=true" alt="mkbrr" height="40px;"></a>&nbsp;&nbsp;
  <a href="https://ffmpeg.org/"><img src="https://i.postimg.cc/xdj3BS7S/FFmpeg-Logo-new-svg.png" alt="FFmpeg" height="40px;"></a>&nbsp;&nbsp;
  <a href="https://mediaarea.net/en/MediaInfo"><img src="https://i.postimg.cc/vTkjXmHh/Media-Info-Logo-svg.png" alt="Mediainfo" height="40px;"></a>&nbsp;&nbsp;
  <a href="https://www.themoviedb.org/"><img src="https://i.postimg.cc/1tpXHx3k/blue-square-2-d537fb228cf3ded904ef09b136fe3fec72548ebc1fea3fbbd1ad9e36364db38b.png" alt="TMDb" height="40px;"></a>&nbsp;&nbsp;
  <a href="https://www.imdb.com/"><img src="https://i.postimg.cc/CLVmvwr1/IMDb-Logo-Rectangle-Gold-CB443386186.png" alt="IMDb" height="40px;"></a>&nbsp;&nbsp;
  <a href="https://thetvdb.com/"><img src="https://i.postimg.cc/Hs1KKqsS/logo1.png" alt="TheTVDB" height="40px;"></a>&nbsp;&nbsp;
  <a href="https://www.tvmaze.com/"><img src="https://i.postimg.cc/2jdRzkJp/tvm-header-logo.png" alt="TVmaze" height="40px"></a>
</p>
