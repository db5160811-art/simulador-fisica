# Laboratorio interactivo: MCU, MCUA y HDD

Aplicación educativa elaborada con Python + Streamlit. La aplicación recibe un radio, RPM iniciales, tiempo y (en MCUA) aceleración angular; muestra gráficas y cálculos. Incluye un módulo para estimar la **latencia rotacional media teórica** de un HDD según sus RPM.

## Archivos

- `app.py`: interfaz web y gráficas.
- `fisica.py`: fórmulas y cálculos.
- `test_fisica.py`: pruebas automáticas.
- `requirements.txt`: dependencias.
- `.streamlit/config.toml`: colores de la página.

## Ejecutar en Windows, macOS o Linux

1. Instala Python 3.11 o 3.12 desde https://www.python.org/downloads/ (en Windows, activa *Add Python to PATH*).
2. Extrae el ZIP del proyecto y abre una terminal dentro de la carpeta donde está `app.py`.
3. Crea y activa un entorno virtual (opcional):

   Windows PowerShell:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   macOS / Linux:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

4. Instala las dependencias:
   ```bash
   python -m pip install -r requirements.txt
   ```
5. Ejecuta la app:
   ```bash
   python -m streamlit run app.py
   ```
6. Abre `http://localhost:8501` en el navegador. Los resultados aparecen en esa página.
7. Para detener el servidor local: `Ctrl+C` en la terminal.

## Publicar en Internet (Streamlit Community Cloud)

1. Crea una cuenta gratuita de GitHub en https://github.com/.
2. En GitHub, crea un repositorio nuevo, por ejemplo `laboratorio-circular`. Puede ser público para facilitar el proceso.
3. Sube los archivos **extraídos** del ZIP, incluyendo `app.py`, `fisica.py`, `requirements.txt` y la carpeta `.streamlit`. Puedes subir también `README.md` y `test_fisica.py`.
4. Ve a https://share.streamlit.io/ e inicia sesión con GitHub.
5. Pulsa **Create app**, selecciona el repositorio, rama `main` y archivo principal `app.py`; después selecciona **Deploy**.
6. Cuando termine el despliegue, recibirás una dirección terminada en `.streamlit.app`, que será la página para compartir con tus estudiantes. Esa dirección se asigna al publicar; no existe todavía.

La publicación no permite controlar ni medir físicamente las RPM de un HDD remoto. Para medir un disco real, se necesita hardware y herramientas de diagnóstico/benchmark independientes.

## Fórmulas aplicadas

- Conversión: `ω0 = RPM × 2π / 60` rad/s.
- MCU: `θ = ω0·t`, `ω = ω0`.
- MCUA: `ω = ω0 + α·t`, `θ = ω0·t + (1/2)·α·t²`.
- Rapidez tangencial: `v = |ω|·r`.
- Aceleración centrípeta: `ac = ω²·r`.
- Aceleración tangencial: `at = α·r` (con signo).
- Latencia rotacional media aproximada HDD: `L(ms) = 30000 / RPM`.
- Latencia rotacional máxima aproximada HDD: `Lmax(ms) = 60000 / RPM`.
- RPM teóricas para un objetivo de espera `L`: `RPMmin = 30000 / L`.

Las fórmulas de HDD suponen giro constante, posiciones de sectores uniformemente distribuidas y no incluyen tiempo de búsqueda del cabezal, transferencia ni sobrecargas. Los HDD reales no suelen permitir variar libremente sus RPM; un SSD no gira.

## Comprobar las fórmulas

```bash
python -m unittest test_fisica.py -v
```
