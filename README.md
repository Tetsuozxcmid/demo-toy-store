python -m PyInstaller --noconfirm --onefile --windowed --name ToyShop `
  --add-data "images;images" `
  --hidden-import=mysql.connector `
  --hidden-import=mysql.connector.locales.eng `
  --collect-submodules=mysql.connector `
  main.py
